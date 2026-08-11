from datetime import datetime, timezone
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
import requests

from trips.domain import DutyStatus, RoutePlan, RouteSegment
from trips.services.compliance import validate_compliance
from trips.services.hos_scheduler import FUEL_INTERVAL_M, schedule_trip
from trips.services.log_builder import build_daily_logs
from trips.services.planner import hours_to_minutes
from trips.services.routing import RoutingError, build_route


def route(minutes=300, distance_m=400_000, pickup_minutes=None):
    pickup_minutes = pickup_minutes or max(1, minutes // 3)
    ratio = pickup_minutes / minutes
    pickup_distance = round(distance_m * ratio)
    return RoutePlan(
        {"current": "Origin", "pickup": "Pickup", "dropoff": "Drop-off"},
        {"current": [-90, 35], "pickup": [-87, 36], "dropoff": [-80, 30]},
        [[-90, 35], [-87, 36], [-80, 30]],
        distance_m,
        minutes,
        [
            RouteSegment("Origin", "Pickup", pickup_distance, pickup_minutes),
            RouteSegment(
                "Pickup",
                "Drop-off",
                distance_m - pickup_distance,
                minutes - pickup_minutes,
            ),
        ],
    )


START = datetime(2026, 8, 11, 12, 0, tzinfo=timezone.utc)


class SchedulerTests(SimpleTestCase):
    def test_short_trip_requires_no_break(self):
        events = schedule_trip(route(240), START, 0)
        self.assertNotIn("BREAK", {e.reason_code for e in events})
        self.assertEqual(
            [
                e.duration_minutes
                for e in events
                if e.reason_code in {"PICKUP", "DROPOFF"}
            ],
            [60, 60],
        )

    def test_exactly_eight_hours_needs_no_break_if_trip_ends(self):
        events = schedule_trip(route(480, pickup_minutes=60), START, 0)
        self.assertNotIn("BREAK", {e.reason_code for e in events})

    def test_break_is_inserted_before_driving_beyond_eight_hours(self):
        events = schedule_trip(route(482, pickup_minutes=1), START, 0)
        break_event = next(e for e in events if e.reason_code == "BREAK")
        pickup = next(e for e in events if e.reason_code == "PICKUP")
        driving_before = sum(
            e.duration_minutes
            for e in events
            if e.status == DutyStatus.DRIVING
            and pickup.end <= e.start
            and e.end <= break_event.start
        )
        self.assertEqual(driving_before, 480)

    def test_eleven_hour_limit_triggers_ten_hour_reset(self):
        events = schedule_trip(route(700, pickup_minutes=1), START, 0)
        self.assertTrue(
            any(
                e.reason_code == "DAILY_RESET" and e.duration_minutes == 600
                for e in events
            )
        )
        self.assertLessEqual(max_shift_drive(events), 660)

    def test_pickup_consumes_window(self):
        events = schedule_trip(route(800, pickup_minutes=600), START, 0)
        pickup = next(e for e in events if e.reason_code == "PICKUP")
        following_reset = next(
            e
            for e in events
            if e.reason_code == "DAILY_RESET" and e.start >= pickup.end
        )
        self.assertEqual(following_reset.duration_minutes, 600)

    def test_dropoff_consumes_cycle(self):
        events = schedule_trip(route(60), START, 4_000)
        counted = sum(
            e.duration_minutes
            for e in events
            if e.status in {DutyStatus.DRIVING, DutyStatus.ON_DUTY_NOT_DRIVING}
        )
        self.assertEqual(counted, 180)

    def test_fuel_stop_before_one_thousand_miles(self):
        events = schedule_trip(route(1_800, FUEL_INTERVAL_M * 2 + 100_000), START, 0)
        fuel = [
            e.route_distance_m
            for e in events
            if e.reason_code in {"FUEL", "FUEL_BREAK"}
        ]
        points = [0, *fuel, FUEL_INTERVAL_M * 2 + 100_000]
        self.assertLessEqual(max(b - a for a, b in zip(points, points[1:])), 1_609_344)

    def test_fuel_stop_is_qualifying_non_driving_period(self):
        events = schedule_trip(route(1_000, FUEL_INTERVAL_M + 10_000), START, 0)
        fuel = next(e for e in events if e.reason_code in {"FUEL", "FUEL_BREAK"})
        self.assertEqual(fuel.duration_minutes, 30)
        self.assertEqual(fuel.status, DutyStatus.ON_DUTY_NOT_DRIVING)

    def test_low_cycle_inserts_restart(self):
        events = schedule_trip(route(240), START, 4_190)
        self.assertTrue(any(e.reason_code == "CYCLE_RESTART" for e in events))

    def test_restart_is_thirty_four_hours(self):
        event = next(
            e
            for e in schedule_trip(route(60), START, 4_200)
            if e.reason_code == "CYCLE_RESTART"
        )
        self.assertEqual(event.duration_minutes, 2_040)

    def test_event_crossing_midnight_is_split(self):
        start = datetime(2026, 8, 11, 23, 30, tzinfo=timezone.utc)
        events = schedule_trip(route(120), start, 0)
        logs = build_daily_logs(events, "UTC", {"total_miles": 100})
        self.assertEqual(len(logs), 2)

    def test_daily_totals_are_1440(self):
        events = schedule_trip(route(1_400), START, 0)
        logs = build_daily_logs(events, "America/Chicago", {"total_miles": 1_000})
        self.assertTrue(all(log["total_minutes"] == 1_440 for log in logs))

    def test_no_event_overlap_or_gap(self):
        events = schedule_trip(route(1_400), START, 0)
        self.assertTrue(all(a.end == b.start for a, b in zip(events, events[1:])))

    def test_chronological_stop_order(self):
        events = schedule_trip(route(1_400), START, 0)
        self.assertTrue(
            all(
                a.route_distance_m <= b.route_distance_m
                for a, b in zip(events, events[1:])
            )
        )

    def test_timezone_aware_log_splitting(self):
        events = schedule_trip(route(600), START, 0)
        logs = build_daily_logs(events, "America/Denver", {"total_miles": 500})
        self.assertEqual(logs[0]["timezone"], "America/Denver")

    def test_cycle_boundaries_convert_exactly(self):
        self.assertEqual(hours_to_minutes("0"), 0)
        self.assertEqual(hours_to_minutes("70"), 4_200)
        self.assertEqual(hours_to_minutes("28.25"), 1_695)

    def test_compliance_findings_pass(self):
        value = route(1_400)
        events = schedule_trip(value, START, 0)
        logs = build_daily_logs(events, "UTC", {"total_miles": 1_000})
        findings = validate_compliance(events, logs, 0, value.distance_m)
        self.assertTrue(all(item["state"] == "pass" for item in findings))


class RoutingTests(SimpleTestCase):
    @override_settings(OPENROUTESERVICE_API_KEY="key", ROUTING_TIMEOUT_SECONDS=1)
    @patch("trips.services.routing.requests.get", side_effect=requests.Timeout)
    def test_external_api_timeout(self, _mock):
        with self.assertRaises(RoutingError) as caught:
            build_route("A", "B", "C")
        self.assertEqual(caught.exception.code, "routing_timeout")

    @override_settings(OPENROUTESERVICE_API_KEY="key")
    @patch("trips.services.routing.requests.get")
    def test_invalid_unresolved_location(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"features": []}
        with self.assertRaises(RoutingError) as caught:
            build_route("Nowhere", "B", "C")
        self.assertEqual(caught.exception.code, "location_unresolved")


def max_shift_drive(events):
    current = maximum = 0
    for event in events:
        if event.reason_code in {"DAILY_RESET", "CYCLE_RESTART"}:
            current = 0
        elif event.status == DutyStatus.DRIVING:
            current += event.duration_minutes
            maximum = max(maximum, current)
    return maximum
