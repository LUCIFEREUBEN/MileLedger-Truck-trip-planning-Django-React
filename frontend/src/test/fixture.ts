import type { TripPlan } from "../types";

export const planFixture: TripPlan = {
  trip_id: "11111111-1111-1111-1111-111111111111",
  input: { current_location: "Louisville, KY", pickup_location: "Nashville, TN", dropoff_location: "Memphis, TN", cycle_used_hours: "28.25", start_datetime: "2026-08-11T12:00:00Z", log_timezone: "America/Chicago" },
  rule_set_version: "FMCSA-395-2022",
  route: {
    mode: "demo",
    addresses: { current: "Louisville, KY", pickup: "Nashville, TN", dropoff: "Memphis, TN" },
    waypoints: { current: [-85.75, 38.25], pickup: [-86.78, 36.16], dropoff: [-90.05, 35.14] },
    geometry: { type: "LineString", coordinates: [[-85.75,38.25],[-86.78,36.16],[-90.05,35.14]] },
    distance_m: 622800, distance_miles: 387, raw_duration_minutes: 400,
    segments: [{ from_label: "Louisville", to_label: "Nashville", distance_m: 281600, duration_minutes: 180, instructions: [{ instruction: "Follow I-65 South", distance_m: 281600 }] }, { from_label: "Nashville", to_label: "Memphis", distance_m: 341200, duration_minutes: 220, instructions: [{ instruction: "Continue on I-40 West", distance_m: 341200 }] }],
  },
  events: [
    { id: "evt-001", sequence: 0, status: "DRIVING", start: "2026-08-11T12:00:00Z", end: "2026-08-11T15:00:00Z", duration_minutes: 180, route_distance_m: 281600, coordinates: [-86.78,36.16], location_label: "Nashville", reason_code: "DRIVE", remark: "Drive route to pickup" },
    { id: "evt-002", sequence: 1, status: "ON_DUTY_NOT_DRIVING", start: "2026-08-11T15:00:00Z", end: "2026-08-11T16:00:00Z", duration_minutes: 60, route_distance_m: 281600, coordinates: [-86.78,36.16], location_label: "Nashville", reason_code: "PICKUP", remark: "Pickup - loading and paperwork" },
    { id: "evt-003", sequence: 2, status: "DRIVING", start: "2026-08-11T16:00:00Z", end: "2026-08-11T19:40:00Z", duration_minutes: 220, route_distance_m: 622800, coordinates: [-90.05,35.14], location_label: "Memphis", reason_code: "DRIVE", remark: "Drive route to drop-off" },
    { id: "evt-004", sequence: 3, status: "ON_DUTY_NOT_DRIVING", start: "2026-08-11T19:40:00Z", end: "2026-08-11T20:40:00Z", duration_minutes: 60, route_distance_m: 622800, coordinates: [-90.05,35.14], location_label: "Memphis", reason_code: "DROPOFF", remark: "Drop-off - unloading and paperwork" },
  ],
  daily_logs: [{
    date: "2026-08-11", timezone: "America/Chicago", total_minutes: 1440, miles_driven: 387,
    totals_minutes: { OFF_DUTY: 980, SLEEPER_BERTH: 0, DRIVING: 400, ON_DUTY_NOT_DRIVING: 60 },
    metadata: { driver_name: "Not provided", carrier_name: "Not provided", main_office_address: "Not provided", vehicle_number: "Not provided", shipping_document_number: "Not provided", shipper_commodity: "Not provided" },
    events: [
      { id: "fill-1", source_event_id: null, status: "OFF_DUTY", start: "2026-08-11T05:00:00Z", end: "2026-08-11T12:00:00Z", start_minute: 0, end_minute: 420, duration_minutes: 420, remark: "Off duty", location_label: "", reason_code: "OFF_DUTY_FILL" },
      { id: "evt-001", source_event_id: "evt-001", status: "DRIVING", start: "2026-08-11T12:00:00Z", end: "2026-08-11T15:00:00Z", start_minute: 420, end_minute: 600, duration_minutes: 180, remark: "Drive route to pickup", location_label: "Nashville", reason_code: "DRIVE" },
      { id: "evt-002", source_event_id: "evt-002", status: "ON_DUTY_NOT_DRIVING", start: "2026-08-11T15:00:00Z", end: "2026-08-11T16:00:00Z", start_minute: 600, end_minute: 660, duration_minutes: 60, remark: "Pickup - loading and paperwork", location_label: "Nashville", reason_code: "PICKUP" },
      { id: "evt-003", source_event_id: "evt-003", status: "DRIVING", start: "2026-08-11T16:00:00Z", end: "2026-08-11T19:40:00Z", start_minute: 660, end_minute: 880, duration_minutes: 220, remark: "Drive route to drop-off", location_label: "Memphis", reason_code: "DRIVE" },
      { id: "evt-004", source_event_id: "evt-004", status: "ON_DUTY_NOT_DRIVING", start: "2026-08-11T19:40:00Z", end: "2026-08-11T20:40:00Z", start_minute: 880, end_minute: 940, duration_minutes: 60, remark: "Drop-off - unloading and paperwork", location_label: "Memphis", reason_code: "DROPOFF" },
      { id: "fill-2", source_event_id: null, status: "OFF_DUTY", start: "2026-08-11T20:40:00Z", end: "2026-08-12T05:00:00Z", start_minute: 940, end_minute: 1440, duration_minutes: 560, remark: "Off duty", location_label: "", reason_code: "OFF_DUTY_FILL" },
    ],
  }],
  compliance: [{ rule_id: "daily-total", title: "Daily total equals 24 hours", state: "pass", explanation: "Compliant by construction.", calculation: "1,440 min", remaining_buffer: "0 min variance", event_ids: ["evt-001"], can_show_on_log: true, can_show_on_map: false }],
  summary: { planned_duration_minutes: 520, estimated_arrival: "2026-08-11T20:40:00Z", days: 1, cycle_used_minutes: 1695, cycle_assumption: "Aggregate cycle balance; no rolling recapture history is invented." },
};
