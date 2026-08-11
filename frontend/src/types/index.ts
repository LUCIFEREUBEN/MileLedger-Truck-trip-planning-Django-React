export type DutyStatus = "OFF_DUTY" | "SLEEPER_BERTH" | "DRIVING" | "ON_DUTY_NOT_DRIVING";

export interface PlanInput {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  cycle_used_hours: string;
  start_datetime?: string;
  log_timezone: string;
  driver_name?: string;
  carrier_name?: string;
  main_office_address?: string;
  vehicle_number?: string;
  shipping_document_number?: string;
  shipper_commodity?: string;
}

export interface DutyEvent {
  id: string;
  sequence: number;
  status: DutyStatus;
  start: string;
  end: string;
  duration_minutes: number;
  route_distance_m: number;
  coordinates: [number, number] | null;
  location_label: string;
  reason_code: string;
  remark: string;
}

export interface LogEvent {
  id: string;
  source_event_id: string | null;
  status: DutyStatus;
  start: string;
  end: string;
  start_minute: number;
  end_minute: number;
  duration_minutes: number;
  remark: string;
  location_label: string;
  reason_code: string;
}

export interface DailyLog {
  date: string;
  timezone: string;
  events: LogEvent[];
  totals_minutes: Record<DutyStatus, number>;
  total_minutes: number;
  miles_driven: number;
  metadata: Record<string, string>;
}

export interface ComplianceFinding {
  rule_id: string;
  title: string;
  state: "pass" | "warning" | "fail";
  explanation: string;
  calculation: string;
  remaining_buffer: string;
  event_ids: string[];
  can_show_on_log: boolean;
  can_show_on_map: boolean;
}

export interface TripPlan {
  trip_id: string;
  input: PlanInput;
  rule_set_version: string;
  route: {
    mode: "demo" | "live";
    addresses: Record<"current" | "pickup" | "dropoff", string>;
    waypoints: Record<"current" | "pickup" | "dropoff", [number, number]>;
    geometry: { type: "LineString"; coordinates: [number, number][] };
    distance_m: number;
    distance_miles: number;
    raw_duration_minutes: number;
    segments: { from_label: string; to_label: string; distance_m: number; duration_minutes: number; instructions: { instruction?: string; distance_m?: number }[] }[];
  };
  events: DutyEvent[];
  daily_logs: DailyLog[];
  compliance: ComplianceFinding[];
  summary: {
    planned_duration_minutes: number;
    estimated_arrival: string;
    days: number;
    cycle_used_minutes: number;
    cycle_assumption: string;
  };
}

export interface ApiErrorShape {
  code: string;
  message: string;
  field_errors: Record<string, string[]>;
  retryable: boolean;
}
