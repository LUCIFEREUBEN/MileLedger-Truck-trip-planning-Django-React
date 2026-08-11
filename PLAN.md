# MileLedger execution plan

## Product contract

MileLedger plans a property-carrying trip from current location to pickup to drop-off, then renders the same canonical duty events as a route, timeline, daily log and compliance explanation. All scheduling uses integer minutes and metres. The frontend never invents schedule data.

## Phases and acceptance gates

- [x] **Domain and API contract** — assumptions, event model, provider boundary and structured errors documented.
- [x] **Backend engine** — deterministic scheduling, daily splitting, interpolation and compliance covered by rule-boundary tests.
- [x] **Routing and persistence** — OpenRouteService adapter, deterministic fixtures, caching, timeouts and persisted endpoints complete.
- [x] **Frontend** — planner, staged progress, synchronized workspace, print view and responsive navigation complete.
- [x] **Quality and delivery** — automated checks, four-viewport visual QA, screenshots, deployment configuration and operator documentation complete.

## Rule decisions

- A plan begins after a qualifying 10-hour rest, so its first driving/on-duty event opens a new 14-hour window. The supplied cycle-used value still limits the 70-hour/8-day cycle.
- Aggregate cycle history cannot support rolling recapture. Remaining cycle is `4,200 - cycle_used_minutes`; a 34-hour restart is inserted when it is insufficient.
- Split sleeper pairings, adverse-driving, short-haul and personal-conveyance exceptions are out of scope.
- A 30-minute consecutive non-driving event qualifies for the break. Pickup, drop-off or fuel service can satisfy it when timing permits.
- Fuel is targeted every 900 route miles, never beyond 1,000 miles, with a 30-minute on-duty/not-driving service period.
- Logs use the selected IANA timezone, split at local midnight, and fill all uncovered time as off duty so each day totals exactly 1,440 minutes.

## External blockers

- Live route/geocoding requires `OPENROUTESERVICE_API_KEY`.
- Public deployment and Loom/GitHub publication require the user's account authorization. Everything else is built and verified locally first.
