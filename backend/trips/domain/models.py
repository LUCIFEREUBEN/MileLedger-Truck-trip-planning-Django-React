from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class DutyStatus(StrEnum):
    OFF_DUTY = "OFF_DUTY"
    SLEEPER_BERTH = "SLEEPER_BERTH"
    DRIVING = "DRIVING"
    ON_DUTY_NOT_DRIVING = "ON_DUTY_NOT_DRIVING"


@dataclass(frozen=True)
class RouteSegment:
    from_label: str
    to_label: str
    distance_m: int
    duration_minutes: int
    instructions: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class RoutePlan:
    addresses: dict[str, str]
    waypoints: dict[str, list[float]]
    geometry: list[list[float]]
    distance_m: int
    duration_minutes: int
    segments: list[RouteSegment]
    mode: str = "demo"


@dataclass
class DutyEventValue:
    event_id: str
    sequence: int
    status: DutyStatus
    start: datetime
    end: datetime
    route_distance_m: int
    coordinates: list[float] | None
    location_label: str
    reason_code: str
    remark: str

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.event_id,
            "sequence": self.sequence,
            "status": self.status.value,
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat().replace("+00:00", "Z"),
            "duration_minutes": self.duration_minutes,
            "route_distance_m": self.route_distance_m,
            "coordinates": self.coordinates,
            "location_label": self.location_label,
            "reason_code": self.reason_code,
            "remark": self.remark,
        }
