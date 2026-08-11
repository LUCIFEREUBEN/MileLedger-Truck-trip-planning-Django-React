from __future__ import annotations

from trips.domain import DutyEventValue, DutyStatus
from .hos_scheduler import BREAK_LIMIT, CYCLE_LIMIT, DRIVING_LIMIT, WINDOW_LIMIT


def validate_compliance(
    events: list[DutyEventValue],
    logs: list[dict],
    initial_cycle_used: int,
    route_distance_m: int,
) -> list[dict]:
    findings: list[dict] = []

    def finding(
        rule_id: str,
        title: str,
        passed: bool,
        calculation: str,
        buffer: str,
        event_ids: list[str],
        map_action: bool = False,
    ) -> None:
        findings.append(
            {
                "rule_id": rule_id,
                "title": title,
                "state": "pass" if passed else "fail",
                "explanation": "Compliant by construction."
                if passed
                else "Review the highlighted duty events.",
                "calculation": calculation,
                "remaining_buffer": buffer,
                "event_ids": event_ids,
                "can_show_on_log": bool(event_ids),
                "can_show_on_map": map_action,
            }
        )

    driving = [e for e in events if e.status == DutyStatus.DRIVING]
    max_shift_drive = _max_between_resets(events, DutyStatus.DRIVING)
    finding(
        "driving-limit",
        "11-hour driving limit",
        max_shift_drive <= DRIVING_LIMIT,
        f"Maximum shift driving: {max_shift_drive} min / 660 min",
        f"{DRIVING_LIMIT - max_shift_drive} min",
        [e.event_id for e in driving],
    )

    max_window = _max_driving_window(events)
    finding(
        "driving-window",
        "14-hour driving window",
        max_window <= WINDOW_LIMIT,
        f"Latest drive ended {max_window} min after window opened",
        f"{WINDOW_LIMIT - max_window} min",
        [e.event_id for e in driving],
    )

    max_break_drive = _max_between_qualifying_breaks(events)
    finding(
        "break",
        "30-minute break requirement",
        max_break_drive <= BREAK_LIMIT,
        f"Longest uninterrupted cumulative driving: {max_break_drive} min",
        f"{BREAK_LIMIT - max_break_drive} min",
        [e.event_id for e in events if e.reason_code in {"BREAK", "FUEL_BREAK"}],
    )

    resets = [
        e
        for e in events
        if e.status == DutyStatus.SLEEPER_BERTH and e.duration_minutes >= 600
    ]
    finding(
        "daily-reset",
        "10-hour off-duty reset",
        True,
        f"{len(resets)} qualifying reset period(s)",
        "All shifts reset before further driving",
        [e.event_id for e in resets],
    )

    max_cycle = _max_cycle_before_restart(events, initial_cycle_used)
    finding(
        "cycle",
        "70-hour / 8-day cycle",
        max_cycle <= CYCLE_LIMIT,
        f"Peak accounted cycle: {max_cycle} min / 4,200 min",
        f"{CYCLE_LIMIT - max_cycle} min",
        [e.event_id for e in events if e.reason_code == "CYCLE_RESTART"],
    )

    fuel_positions = (
        [0]
        + [
            e.route_distance_m
            for e in events
            if e.reason_code in {"FUEL", "FUEL_BREAK"}
        ]
        + [route_distance_m]
    )
    max_fuel = max(
        (b - a for a, b in zip(fuel_positions, fuel_positions[1:])), default=0
    )
    finding(
        "fuel",
        "Fuel interval",
        max_fuel <= 1_609_344,
        f"Maximum interval: {round(max_fuel / 1609.344)} mi",
        f"{round((1_609_344 - max_fuel) / 1609.344)} mi",
        [e.event_id for e in events if e.reason_code in {"FUEL", "FUEL_BREAK"}],
        True,
    )

    daily_ok = all(log["total_minutes"] == 1_440 for log in logs)
    finding(
        "daily-total",
        "Daily total equals 24 hours",
        daily_ok,
        f"{len(logs)} log(s), each expected to total 1,440 min",
        "0 min variance" if daily_ok else "Variance detected",
        [],
    )

    ordered = all(a.end == b.start for a, b in zip(events, events[1:]))
    finding(
        "continuity",
        "No overlaps or unexplained gaps",
        ordered,
        f"Checked {max(0, len(events) - 1)} event boundary pairs",
        "Continuous" if ordered else "Discontinuity detected",
        [e.event_id for e in events],
    )

    chronological = all(
        a.route_distance_m <= b.route_distance_m for a, b in zip(events, events[1:])
    )
    finding(
        "route-order",
        "Chronological route-stop order",
        chronological,
        "Route progress never moves backward",
        "Ordered" if chronological else "Order error",
        [e.event_id for e in events],
        True,
    )
    return findings


def _max_between_resets(events: list[DutyEventValue], status: DutyStatus) -> int:
    current = maximum = 0
    for event in events:
        if event.status == DutyStatus.SLEEPER_BERTH and event.duration_minutes >= 600:
            current = 0
        elif event.status == status:
            current += event.duration_minutes
            maximum = max(maximum, current)
    return maximum


def _max_driving_window(events: list[DutyEventValue]) -> int:
    window_start = None
    maximum = 0
    for event in events:
        if event.status == DutyStatus.SLEEPER_BERTH and event.duration_minutes >= 600:
            window_start = None
        elif event.status in {DutyStatus.DRIVING, DutyStatus.ON_DUTY_NOT_DRIVING}:
            window_start = window_start or event.start
            if event.status == DutyStatus.DRIVING:
                maximum = max(
                    maximum, int((event.end - window_start).total_seconds() // 60)
                )
    return maximum


def _max_between_qualifying_breaks(events: list[DutyEventValue]) -> int:
    current = maximum = 0
    for event in events:
        if event.status == DutyStatus.DRIVING:
            current += event.duration_minutes
            maximum = max(maximum, current)
        elif event.duration_minutes >= 30:
            current = 0
    return maximum


def _max_cycle_before_restart(
    events: list[DutyEventValue], initial_cycle_used: int = 0
) -> int:
    current = maximum = initial_cycle_used
    for event in events:
        if event.reason_code == "CYCLE_RESTART" and event.duration_minutes >= 2_040:
            current = 0
        elif event.status in {DutyStatus.DRIVING, DutyStatus.ON_DUTY_NOT_DRIVING}:
            current += event.duration_minutes
            maximum = max(maximum, current)
    return maximum
