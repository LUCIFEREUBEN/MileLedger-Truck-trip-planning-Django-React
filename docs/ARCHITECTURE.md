# Architecture

## System shape

`React + TypeScript` calls a versioned Django REST API. Django resolves and routes locations through OpenRouteService, passes a provider-neutral route into a pure scheduling service, validates the resulting events, persists the canonical plan, and returns typed JSON. Demo mode swaps only the route provider; scheduling and compliance stay identical.

## Backend boundaries

- `trips/domain`: immutable duty-event and route value objects using minutes, metres and aware datetimes.
- `trips/services/routing.py`: normalized-address cache, ORS geocoding/directions, timeouts and demo fixtures.
- `trips/services/hos_scheduler.py`: compliant-by-construction event generation.
- `trips/services/route_interpolation.py`: distance-to-coordinate interpolation along route geometry.
- `trips/services/log_builder.py`: local-midnight splitting and 24-hour log completion.
- `trips/services/compliance.py`: independent explainable assertions over canonical events.
- `trips/api`: serializers and thin views.

`TripPlan` stores request metadata, route facts and the full result snapshot. `DutyEvent` stores ordered canonical events for querying and audit.

## Frontend boundaries

- `features/trip-planner`: validated inputs, examples and staged progress.
- `features/timeline`, `features/map`, `features/eld-log`, `features/compliance`: alternate projections of the same event IDs.
- `app/TripWorkspace`: owns selected day/event state so hover, focus and click synchronize every representation.
- `lib/api`: the only HTTP boundary; errors are normalized for the UI.

## Reliability

Route providers are never called by tests. Network failures return `{code, message, field_errors, retryable}` and preserve form state. Production settings disable debug, require configured hosts/origins and use database URLs. The UI labels fixture plans as demo data.

