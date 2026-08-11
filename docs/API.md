# API

Base path: `/api/`

## `GET health/`

Returns service status, version and route mode.

## `POST trips/plan/`

Required JSON: `current_location`, `pickup_location`, `dropoff_location`, `cycle_used_hours`. Optional: `start_datetime`, `log_timezone` and log metadata fields.

Returns `201` with `trip_id`, normalized `input`, provider route, canonical duty events, daily logs and compliance findings. `input` makes persisted result URLs safely recalculable after a browser refresh.

## `GET trips/{id}/`

Returns the persisted result snapshot.

## `POST trips/{id}/recalculate/`

Merges supplied fields with the original request and returns a new persisted calculation.

## Errors

Errors use:

```json
{
  "code": "invalid_input",
  "message": "Review the highlighted fields.",
  "field_errors": {"cycle_used_hours": ["Enter a value from 0 to 70."]},
  "retryable": false
}
```
