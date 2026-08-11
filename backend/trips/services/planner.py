from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.db import transaction

from trips.models import DutyEvent, TripPlan
from .compliance import validate_compliance
from .hos_scheduler import schedule_trip
from .log_builder import build_daily_logs
from .routing import build_route


def hours_to_minutes(value: Decimal | float | str) -> int:
    return int(
        (Decimal(str(value)) * 60).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


@transaction.atomic
def create_plan(payload: dict[str, Any]) -> TripPlan:
    route = build_route(
        payload["current_location"],
        payload["pickup_location"],
        payload["dropoff_location"],
    )
    start = payload.get("start_datetime") or datetime.now(timezone.utc).replace(
        second=0, microsecond=0
    )
    cycle_used = hours_to_minutes(payload["cycle_used_hours"])
    events = schedule_trip(route, start, cycle_used)
    total_miles = round(route.distance_m / 1609.344)
    metadata = {**payload, "total_miles": total_miles}
    logs = build_daily_logs(
        events, payload.get("log_timezone", "America/Chicago"), metadata
    )
    findings = validate_compliance(events, logs, cycle_used, route.distance_m)
    route_json = {
        "mode": route.mode,
        "addresses": route.addresses,
        "waypoints": route.waypoints,
        "geometry": {"type": "LineString", "coordinates": route.geometry},
        "distance_m": route.distance_m,
        "distance_miles": total_miles,
        "raw_duration_minutes": route.duration_minutes,
        "segments": [
            {
                "from_label": segment.from_label,
                "to_label": segment.to_label,
                "distance_m": segment.distance_m,
                "duration_minutes": segment.duration_minutes,
                "instructions": segment.instructions,
            }
            for segment in route.segments
        ],
    }
    serializable_payload = {
        **payload,
        "start_datetime": start.isoformat().replace("+00:00", "Z"),
        "cycle_used_hours": str(payload["cycle_used_hours"]),
    }
    result = {
        "trip_id": None,
        "input": serializable_payload,
        "rule_set_version": "FMCSA-395-2022",
        "route": route_json,
        "events": [event.as_dict() for event in events],
        "daily_logs": logs,
        "compliance": findings,
        "summary": {
            "planned_duration_minutes": round(
                (events[-1].end - events[0].start).total_seconds() / 60
            ),
            "estimated_arrival": events[-1].end.isoformat().replace("+00:00", "Z"),
            "days": len(logs),
            "cycle_used_minutes": cycle_used,
            "cycle_assumption": "Aggregate cycle balance; no rolling recapture history is invented.",
        },
    }
    trip = TripPlan.objects.create(
        request_payload=serializable_payload, result=result, route_mode=route.mode
    )
    result["trip_id"] = str(trip.id)
    trip.result = result
    trip.save(update_fields=["result", "updated_at"])
    DutyEvent.objects.bulk_create(
        [
            DutyEvent(
                trip=trip,
                event_id=event.event_id,
                sequence=event.sequence,
                status=event.status.value,
                start_at=event.start,
                end_at=event.end,
                duration_minutes=event.duration_minutes,
                route_distance_m=event.route_distance_m,
                coordinates=event.coordinates,
                reason_code=event.reason_code,
                remark=event.remark,
            )
            for event in events
        ]
    )
    return trip
