from __future__ import annotations

from datetime import datetime, timedelta, timezone

from trips.domain import DutyEventValue, DutyStatus, RoutePlan
from .route_interpolation import interpolate_route

DRIVING_LIMIT = 660
WINDOW_LIMIT = 840
BREAK_LIMIT = 480
BREAK_DURATION = 30
DAILY_RESET = 600
CYCLE_LIMIT = 4_200
CYCLE_RESTART = 2_040
FUEL_INTERVAL_M = 1_448_410  # 900 miles


def schedule_trip(
    route: RoutePlan, start: datetime, cycle_used_minutes: int
) -> list[DutyEventValue]:
    if start.tzinfo is None:
        raise ValueError("start must be timezone-aware")
    current = start.astimezone(timezone.utc)
    events: list[DutyEventValue] = []
    route_drive = 0
    route_distance = 0
    pickup_drive = route.segments[0].duration_minutes
    pickup_done = False
    fuel_target = FUEL_INTERVAL_M
    shift_start: datetime | None = None
    shift_drive = 0
    drive_since_break = 0
    cycle_remaining = CYCLE_LIMIT - cycle_used_minutes

    def distance_at(drive_minutes: int) -> int:
        first = route.segments[0]
        if drive_minutes <= pickup_drive:
            return round(drive_minutes / max(1, pickup_drive) * first.distance_m)
        second_drive = route.duration_minutes - pickup_drive
        return first.distance_m + round(
            (drive_minutes - pickup_drive)
            / max(1, second_drive)
            * route.segments[1].distance_m
        )

    def drive_at(distance_m: int) -> int:
        first = route.segments[0]
        if distance_m <= first.distance_m:
            return round(distance_m / max(1, first.distance_m) * pickup_drive)
        return pickup_drive + round(
            (distance_m - first.distance_m)
            / max(1, route.segments[1].distance_m)
            * (route.duration_minutes - pickup_drive)
        )

    def location(
        distance_m: int, fallback: str = "Along route"
    ) -> tuple[list[float] | None, str]:
        coords = interpolate_route(route.geometry, route.distance_m, distance_m)
        return coords, fallback

    def add(
        status: DutyStatus,
        minutes: int,
        reason: str,
        remark: str,
        distance_m: int | None = None,
        label: str = "Along route",
    ) -> None:
        nonlocal current, drive_since_break, cycle_remaining
        distance_m = route_distance if distance_m is None else distance_m
        coords, resolved_label = location(distance_m, label)
        event = DutyEventValue(
            f"evt-{len(events) + 1:03d}",
            len(events),
            status,
            current,
            current + timedelta(minutes=minutes),
            distance_m,
            coords,
            resolved_label,
            reason,
            remark,
        )
        events.append(event)
        current = event.end
        if status in (DutyStatus.DRIVING, DutyStatus.ON_DUTY_NOT_DRIVING):
            cycle_remaining -= minutes
        if status == DutyStatus.DRIVING:
            drive_since_break += minutes
        elif minutes >= BREAK_DURATION:
            drive_since_break = 0

    def reset(minutes: int, reason: str, remark: str) -> None:
        nonlocal shift_start, shift_drive, cycle_remaining
        add(DutyStatus.SLEEPER_BERTH, minutes, reason, remark)
        shift_start = None
        shift_drive = 0
        if minutes >= CYCLE_RESTART:
            cycle_remaining = CYCLE_LIMIT

    def ensure_cycle(required: int) -> None:
        if cycle_remaining < required:
            reset(
                CYCLE_RESTART,
                "CYCLE_RESTART",
                "34-hour restart - aggregate cycle balance exhausted",
            )

    while route_drive < route.duration_minutes:
        if not pickup_done and route_drive >= pickup_drive:
            ensure_cycle(60)
            add(
                DutyStatus.ON_DUTY_NOT_DRIVING,
                60,
                "PICKUP",
                "Pickup - loading and paperwork",
                route.segments[0].distance_m,
                route.addresses["pickup"],
            )
            pickup_done = True
            continue

        if route_distance >= fuel_target and fuel_target < route.distance_m:
            ensure_cycle(BREAK_DURATION)
            combined = drive_since_break >= BREAK_LIMIT - 30
            add(
                DutyStatus.ON_DUTY_NOT_DRIVING,
                BREAK_DURATION,
                "FUEL_BREAK" if combined else "FUEL",
                "Fuel + qualifying 30-minute break"
                if combined
                else "Fuel stop - vehicle service",
                route_distance,
                "Planned fuel stop",
            )
            fuel_target += FUEL_INTERVAL_M
            continue

        if cycle_remaining <= 0:
            reset(
                CYCLE_RESTART,
                "CYCLE_RESTART",
                "34-hour restart - aggregate cycle balance exhausted",
            )
            continue
        if shift_start is None:
            shift_start = current
            shift_drive = 0
        window_used = int((current - shift_start).total_seconds() // 60)
        if shift_drive >= DRIVING_LIMIT or window_used >= WINDOW_LIMIT:
            reset(DAILY_RESET, "DAILY_RESET", "10 consecutive hours in sleeper berth")
            continue
        if drive_since_break >= BREAK_LIMIT:
            add(
                DutyStatus.OFF_DUTY,
                BREAK_DURATION,
                "BREAK",
                "Required 30-minute non-driving break",
            )
            continue

        remaining_drive = route.duration_minutes - route_drive
        to_pickup = pickup_drive - route_drive if not pickup_done else remaining_drive
        next_fuel_drive = drive_at(fuel_target)
        to_fuel = (
            next_fuel_drive - route_drive
            if fuel_target < route.distance_m
            else remaining_drive
        )
        chunk = min(
            remaining_drive,
            max(1, to_pickup),
            max(1, to_fuel),
            DRIVING_LIMIT - shift_drive,
            WINDOW_LIMIT - window_used,
            BREAK_LIMIT - drive_since_break,
            cycle_remaining,
        )
        route_drive += chunk
        shift_drive += chunk
        route_distance = min(route.distance_m, distance_at(route_drive))
        add(
            DutyStatus.DRIVING,
            chunk,
            "DRIVE",
            f"Drive route - {round(route_distance / 1609.344):,} mi progress",
            route_distance,
        )

    if not pickup_done:
        ensure_cycle(60)
        add(
            DutyStatus.ON_DUTY_NOT_DRIVING,
            60,
            "PICKUP",
            "Pickup - loading and paperwork",
            route.segments[0].distance_m,
            route.addresses["pickup"],
        )
    ensure_cycle(60)
    add(
        DutyStatus.ON_DUTY_NOT_DRIVING,
        60,
        "DROPOFF",
        "Drop-off - unloading and paperwork",
        route.distance_m,
        route.addresses["dropoff"],
    )
    return events
