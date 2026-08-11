from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

from trips.domain import RoutePlan, RouteSegment


class RoutingError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = True,
        field: str | None = None,
    ):
        super().__init__(message)
        self.code, self.message, self.retryable, self.field = (
            code,
            message,
            retryable,
            field,
        )


DEMO_ROUTES = {
    "short": {
        "match": ("louisville", "nashville", "memphis"),
        "addresses": {
            "current": "Louisville, KY, USA",
            "pickup": "Nashville, TN, USA",
            "dropoff": "Memphis, TN, USA",
        },
        "waypoints": {
            "current": [-85.7585, 38.2527],
            "pickup": [-86.7816, 36.1627],
            "dropoff": [-90.0490, 35.1495],
        },
        "geometry": [
            [-85.7585, 38.2527],
            [-86.15, 37.75],
            [-86.45, 37.10],
            [-86.7816, 36.1627],
            [-87.45, 36.05],
            [-88.30, 35.75],
            [-89.15, 35.45],
            [-90.049, 35.1495],
        ],
        "segments": [(281_600, 180), (341_200, 220)],
    },
    "multi": {
        "match": ("seattle", "denver", "miami"),
        "addresses": {
            "current": "Seattle, WA, USA",
            "pickup": "Denver, CO, USA",
            "dropoff": "Miami, FL, USA",
        },
        "waypoints": {
            "current": [-122.3321, 47.6062],
            "pickup": [-104.9903, 39.7392],
            "dropoff": [-80.1918, 25.7617],
        },
        "geometry": [
            [-122.3321, 47.6062],
            [-119.1, 46.2],
            [-116.2, 43.6],
            [-112.0, 41.2],
            [-108.5, 40.4],
            [-104.9903, 39.7392],
            [-101.0, 38.7],
            [-97.5, 36.2],
            [-94.2, 35.1],
            [-90.1, 32.4],
            [-86.8, 30.8],
            [-83.2, 29.5],
            [-81.4, 27.7],
            [-80.1918, 25.7617],
        ],
        "segments": [(2_143_000, 1_260), (3_308_000, 1_920)],
    },
}


def _fixture(current: str, pickup: str, dropoff: str) -> RoutePlan:
    normalized = tuple(x.lower().strip() for x in (current, pickup, dropoff))
    fixture = next(
        (
            x
            for x in DEMO_ROUTES.values()
            if all(
                term in value
                for term, value in zip(x["match"], normalized, strict=True)
            )
        ),
        DEMO_ROUTES["short"],
    )
    labels = [
        fixture["addresses"]["current"],
        fixture["addresses"]["pickup"],
        fixture["addresses"]["dropoff"],
    ]
    segments = [
        RouteSegment(
            labels[0],
            labels[1],
            *fixture["segments"][0],
            instructions=[
                {
                    "instruction": "Follow the truck route to pickup",
                    "distance_m": fixture["segments"][0][0],
                }
            ],
        ),
        RouteSegment(
            labels[1],
            labels[2],
            *fixture["segments"][1],
            instructions=[
                {
                    "instruction": "Continue to the delivery location",
                    "distance_m": fixture["segments"][1][0],
                }
            ],
        ),
    ]
    return RoutePlan(
        fixture["addresses"],
        fixture["waypoints"],
        fixture["geometry"],
        sum(x.distance_m for x in segments),
        sum(x.duration_minutes for x in segments),
        segments,
        "demo",
    )


def _geocode(text: str) -> tuple[str, list[float]]:
    try:
        response = requests.get(
            "https://api.openrouteservice.org/geocode/search",
            params={
                "api_key": settings.OPENROUTESERVICE_API_KEY,
                "text": text,
                "size": 1,
            },
            timeout=settings.ROUTING_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        features = response.json().get("features", [])
    except requests.Timeout as exc:
        raise RoutingError(
            "routing_timeout", "The route service took too long to respond."
        ) from exc
    except requests.RequestException as exc:
        raise RoutingError(
            "routing_unavailable", "The route service is temporarily unavailable."
        ) from exc
    if not features:
        raise RoutingError(
            "location_unresolved",
            f"We could not resolve ‘{text}’ to a usable location.",
            retryable=False,
        )
    feature = features[0]
    return feature["properties"].get("label", text), feature["geometry"]["coordinates"]


def _live(current: str, pickup: str, dropoff: str) -> RoutePlan:
    resolved = [_geocode(x) for x in (current, pickup, dropoff)]
    coordinates = [x[1] for x in resolved]
    try:
        response = requests.post(
            "https://api.openrouteservice.org/v2/directions/driving-hgv/geojson",
            headers={
                "Authorization": settings.OPENROUTESERVICE_API_KEY,
                "Content-Type": "application/json",
            },
            json={"coordinates": coordinates, "instructions": True},
            timeout=settings.ROUTING_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        feature = response.json()["features"][0]
    except requests.Timeout as exc:
        raise RoutingError(
            "routing_timeout", "The route service took too long to respond."
        ) from exc
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        raise RoutingError(
            "route_not_found", "No usable truck route was returned for these locations."
        ) from exc
    summary = feature["properties"]["summary"]
    raw_segments = feature["properties"].get("segments", [])
    labels = [x[0] for x in resolved]
    segments = []
    for index in range(2):
        raw = (
            raw_segments[index]
            if index < len(raw_segments)
            else {
                "distance": summary["distance"] / 2,
                "duration": summary["duration"] / 2,
                "steps": [],
            }
        )
        segments.append(
            RouteSegment(
                labels[index],
                labels[index + 1],
                round(raw["distance"]),
                round(raw["duration"] / 60),
                raw.get("steps", []),
            )
        )
    return RoutePlan(
        {"current": labels[0], "pickup": labels[1], "dropoff": labels[2]},
        {
            "current": coordinates[0],
            "pickup": coordinates[1],
            "dropoff": coordinates[2],
        },
        feature["geometry"]["coordinates"],
        round(summary["distance"]),
        round(summary["duration"] / 60),
        segments,
        "live",
    )


def build_route(current: str, pickup: str, dropoff: str) -> RoutePlan:
    mode = "live" if settings.OPENROUTESERVICE_API_KEY else "demo"
    if mode == "demo" and not settings.DEMO_MODE:
        raise RoutingError(
            "route_configuration", "Live routing is not configured.", retryable=False
        )
    cache_key = (
        "route:"
        + hashlib.sha256(
            json.dumps(
                [
                    mode,
                    current.strip().lower(),
                    pickup.strip().lower(),
                    dropoff.strip().lower(),
                ]
            ).encode()
        ).hexdigest()
    )
    cached: dict[str, Any] | None = cache.get(cache_key)
    if cached:
        return RoutePlan(
            cached["addresses"],
            cached["waypoints"],
            cached["geometry"],
            cached["distance_m"],
            cached["duration_minutes"],
            [RouteSegment(**segment) for segment in cached["segments"]],
            cached["mode"],
        )
    route = (
        _live(current, pickup, dropoff)
        if mode == "live"
        else _fixture(current, pickup, dropoff)
    )
    cache.set(
        cache_key,
        {**asdict(route), "segments": [asdict(x) for x in route.segments]},
        60 * 60 * 24,
    )
    return route
