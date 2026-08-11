from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from trips.domain import DutyEventValue, DutyStatus


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def build_daily_logs(
    events: list[DutyEventValue], timezone_name: str, metadata: dict
) -> list[dict]:
    if not events:
        return []
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("Unknown IANA time zone") from exc
    first_date = events[0].start.astimezone(zone).date()
    last_date = (events[-1].end - timedelta(microseconds=1)).astimezone(zone).date()
    logs = []
    day = first_date
    while day <= last_date:
        local_start = datetime.combine(day, time.min, tzinfo=zone)
        local_end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone)
        day_start, day_end = (
            local_start.astimezone(timezone.utc),
            local_end.astimezone(timezone.utc),
        )
        slices = []
        cursor = day_start
        for event in events:
            start, end = max(event.start, day_start), min(event.end, day_end)
            if end <= start:
                continue
            if start > cursor:
                slices.append(
                    _slice(
                        None,
                        DutyStatus.OFF_DUTY,
                        cursor,
                        start,
                        "Off duty",
                        zone,
                        day_start,
                    )
                )
            slices.append(
                _slice(event, event.status, start, end, event.remark, zone, day_start)
            )
            cursor = max(cursor, end)
        if cursor < day_end:
            slices.append(
                _slice(
                    None,
                    DutyStatus.OFF_DUTY,
                    cursor,
                    day_end,
                    "Off duty",
                    zone,
                    day_start,
                )
            )
        totals = {status.value: 0 for status in DutyStatus}
        for item in slices:
            totals[item["status"]] += item["duration_minutes"]
        total = sum(totals.values())
        if total != 1_440:
            # DST transitions are normalized to the 24-hour paper-log grid.
            totals[DutyStatus.OFF_DUTY.value] += 1_440 - total
        logs.append(
            {
                "date": day.isoformat(),
                "timezone": timezone_name,
                "events": slices,
                "totals_minutes": totals,
                "total_minutes": sum(totals.values()),
                "miles_driven": round(
                    sum(
                        x["duration_minutes"]
                        for x in slices
                        if x["status"] == DutyStatus.DRIVING.value
                    )
                    / max(
                        1,
                        sum(
                            e.duration_minutes
                            for e in events
                            if e.status == DutyStatus.DRIVING
                        ),
                    )
                    * metadata.get("total_miles", 0)
                ),
                "metadata": {
                    key: metadata.get(key) or "Not provided"
                    for key in [
                        "driver_name",
                        "carrier_name",
                        "main_office_address",
                        "vehicle_number",
                        "shipping_document_number",
                        "shipper_commodity",
                    ]
                },
            }
        )
        day += timedelta(days=1)
    return logs


def _slice(
    event: DutyEventValue | None,
    status: DutyStatus,
    start: datetime,
    end: datetime,
    remark: str,
    zone: ZoneInfo,
    day_start: datetime,
) -> dict:
    duration = round((end - start).total_seconds() / 60)
    start_local = start.astimezone(zone)
    start_minute = round((start - day_start).total_seconds() / 60)
    return {
        "id": event.event_id if event else f"fill-{start_local.isoformat()}",
        "source_event_id": event.event_id if event else None,
        "status": status.value,
        "start": _iso(start),
        "end": _iso(end),
        "start_minute": start_minute,
        "end_minute": start_minute + duration,
        "duration_minutes": duration,
        "remark": remark,
        "location_label": event.location_label if event else "",
        "reason_code": event.reason_code if event else "OFF_DUTY_FILL",
    }
