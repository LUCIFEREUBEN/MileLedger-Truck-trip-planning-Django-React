# HOS rules and assumptions

MileLedger implements the property-carrying rules summarized by FMCSA and the supplied April 2022 driver's guide.

- **11-hour driving limit:** no more than 660 driving minutes after 10 consecutive hours off duty.
- **14-hour window:** no driving after 840 consecutive minutes from the first on-duty or driving event following a qualifying reset. Non-driving time does not pause the window.
- **30-minute break:** before driving beyond 480 cumulative driving minutes without a qualifying 30-consecutive-minute non-driving interruption.
- **70-hour/8-day cycle:** driving and on-duty/not-driving count. The assessment supplies only an aggregate, so no recapture history is invented; a 34-hour restart is inserted when necessary.
- **Daily reset:** 600 consecutive sleeper-berth minutes reset the 11/14-hour clocks. Split sleeper pairings are intentionally excluded.
- **Fuel:** a planned 30-minute on-duty/not-driving stop at a 900-mile target keeps every interval below 1,000 miles.
- **Pickup/drop-off:** exactly 60 minutes on duty, not driving, at each location.
- **Daily records:** events are split at midnight in the selected IANA timezone; each log covers exactly 1,440 minutes with no overlap or gaps.

Planning assumes a rested driver at trip start, no adverse-driving exception, no short-haul exception and no personal conveyance. Route duration comes from the route provider; fixtures are visibly marked. MileLedger is not an FMCSA-certified ELD and does not replace official compliance review.

