# MileLedger 3–5 minute Loom script

## 0:00 — Objective

“MileLedger answers the assessment’s core question: given a current location, pickup, drop-off, and cycle usage, what route and duty schedule can a property-carrying driver follow without merely discovering violations afterward?”

Mention Django/DRF, React/TypeScript, OpenRouteService, and that the schedule is deterministic—not AI-generated.

## 0:25 — Inputs and route generation

Show the planner. Point out the four required fields, optional start/timezone, and collapsed log metadata. Load the Seattle–Denver–Miami example, then build the plan while the staged status messages run.

Call out that the displayed route is a labelled deterministic demo fixture; with the server-side key configured, the same adapter requests a live HGV route without exposing credentials to the browser.

## 0:55 — Workspace and automatic schedule

On the trip ribbon, show distance, planned duration, arrival, and 9/9 compliance. Scan the timeline and point out pickup, 900-mile fuel targets, required breaks, 10-hour sleeper periods, and the conservative 34-hour restart caused by the supplied 48.5 cycle hours.

Explain that pickup and drop-off are each exactly one on-duty hour and that the planner inserts legal rest before additional driving.

## 1:35 — Daily logs and synchronization

Select a fuel or break event. Show the same selection on the map, timeline, ELD segment, and remark. Move between log days and explain that the backend splits events at local midnight, fills off-duty edges, and proves each date totals exactly 24 hours.

Show the four-row SVG graph, quarter-hour grid, daily status totals, metadata, remarks, and print button. Mention browser “Save as PDF,” one US Letter page per day.

## 2:20 — Compliance inspector

Open the inspector. Expand the 11-hour, break, and cycle findings. Read one calculation and buffer, then use “Show on log.” Explain that all findings inspect the same canonical events rather than trusting frontend decoration.

## 2:55 — Engineering design

Briefly show `backend/trips/services`: route provider boundary, pure HOS scheduler, route interpolation, daily-log builder, and independent compliance validator. Show the thin API view and structured error contract. Mention UTC persistence, integer minutes, metres, PostgreSQL production support, and fixture-only tests.

## 3:30 — Tests, responsive UI, and delivery

Show the passing backend and frontend commands. Mention the 23 Django tests plus frontend unit and Playwright desktop/mobile coverage. Resize to mobile and use Map, Logs, and Inspector tabs. Finish with the Vercel frontend, Render Docker backend, PostgreSQL, CI, and documented environment variables.

Close with: “MileLedger is a planning demonstration, not a certified ELD, but the assessment workflow is complete, explainable, testable, and deployment-ready.”
