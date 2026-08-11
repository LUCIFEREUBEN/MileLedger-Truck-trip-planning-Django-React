import { useMemo, useState } from "react";
import { CalendarDays, ChevronLeft, ChevronRight, Gauge, PanelRightOpen, Route, ShieldCheck } from "lucide-react";
import type { PlanInput, TripPlan } from "../types";
import { formatDateTime, formatDuration } from "../lib/format";
import { recalculateTrip } from "../lib/api";
import { TripTimeline } from "../features/timeline/TripTimeline";
import { RouteMap } from "../features/map/RouteMap";
import { DailyLogSheet } from "../features/eld-log/DailyLogSheet";
import { ComplianceInspector } from "../features/compliance/ComplianceInspector";

type Tab = "timeline" | "map" | "logs" | "inspector";

export function TripWorkspace({ plan, input, onPlan }: { plan: TripPlan; input: PlanInput; onPlan: (plan: TripPlan) => void }) {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [activeDay, setActiveDay] = useState(0);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [mobileTab, setMobileTab] = useState<Tab>("map");
  const [recalculating, setRecalculating] = useState(false);
  const log = plan.daily_logs[activeDay];
  const selected = useMemo(() => plan.events.find(event => event.id === selectedEventId) ?? null, [plan.events, selectedEventId]);
  const passCount = plan.compliance.filter(item => item.state === "pass").length;

  const highlight = (ids: string[]) => { setSelectedEventId(ids[0] ?? null); if (ids[0]) setMobileTab("logs"); };
  const recalc = async () => { setRecalculating(true); try { const next = await recalculateTrip(plan.trip_id, input); onPlan(next); window.history.replaceState({}, "", `?trip=${next.trip_id}`); } finally { setRecalculating(false); } };

  return <main className="workspace-page">
    <section className="trip-ribbon">
      <div><p className="eyebrow">Trip plan</p><h1>{plan.route.addresses.current.split(",")[0]} <span>→</span> {plan.route.addresses.dropoff.split(",")[0]}</h1></div>
      <dl><div><dt><Route /> Distance</dt><dd>{plan.route.distance_miles.toLocaleString()} mi</dd></div><div><dt><Gauge /> Planned time</dt><dd>{formatDuration(plan.summary.planned_duration_minutes)}</dd></div><div><dt><CalendarDays /> Arrival</dt><dd>{formatDateTime(plan.summary.estimated_arrival, input.log_timezone)}</dd></div><div><dt><ShieldCheck /> Compliance</dt><dd>{passCount}/{plan.compliance.length} pass</dd></div></dl>
      <div className={`mode-flag ${plan.route.mode}`}><i /> {plan.route.mode === "live" ? "Live HGV route" : "Verified demo route"}</div>
    </section>
    <nav className="mobile-tabs" aria-label="Trip workspace"><button className={mobileTab === "timeline" ? "active" : ""} onClick={() => setMobileTab("timeline")}>Timeline</button><button className={mobileTab === "map" ? "active" : ""} onClick={() => setMobileTab("map")}>Map</button><button className={mobileTab === "logs" ? "active" : ""} onClick={() => setMobileTab("logs")}>Logs</button><button className={mobileTab === "inspector" ? "active" : ""} onClick={() => setMobileTab("inspector")}>Inspector</button></nav>
    <section className="workspace-grid">
      <aside className={`timeline-pane mobile-${mobileTab}`}><TripTimeline plan={plan} selectedEventId={selectedEventId} onSelect={setSelectedEventId} /></aside>
      <section className={`map-pane mobile-${mobileTab}`}><RouteMap plan={plan} selectedEventId={selectedEventId} onSelect={setSelectedEventId} /></section>
      <section className={`log-pane mobile-${mobileTab}`}>
        <div className="log-toolbar"><div><button aria-label="Previous day" disabled={activeDay === 0} onClick={() => setActiveDay(day => day - 1)}><ChevronLeft /></button><span><b>Day {activeDay + 1} of {plan.daily_logs.length}</b>{new Date(`${log.date}T12:00:00`).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}</span><button aria-label="Next day" disabled={activeDay === plan.daily_logs.length - 1} onClick={() => setActiveDay(day => day + 1)}><ChevronRight /></button></div><button className="inspector-toggle" aria-expanded={inspectorOpen} onClick={() => setInspectorOpen(open => !open)}><PanelRightOpen /> Inspector <span>{passCount}/{plan.compliance.length}</span></button></div>
        <DailyLogSheet log={log} dayIndex={activeDay} dayCount={plan.daily_logs.length} selectedEventId={selectedEventId} onSelect={setSelectedEventId} />
        {selected && <div className="selection-note"><span>Selected</span><strong>{selected.remark}</strong><button onClick={() => setSelectedEventId(null)}>Clear</button></div>}
        {inspectorOpen && <ComplianceInspector findings={plan.compliance} onHighlight={highlight} onClose={() => setInspectorOpen(false)} />}
      </section>
      <section className={`inspector-mobile mobile-${mobileTab}`}><ComplianceInspector findings={plan.compliance} onHighlight={highlight} /></section>
    </section>
    <section className="print-logs" aria-hidden="true">{plan.daily_logs.map((dayLog, index) => <DailyLogSheet key={dayLog.date} log={dayLog} dayIndex={index} dayCount={plan.daily_logs.length} selectedEventId={null} onSelect={() => undefined} />)}</section>
    <div className="assumption-bar"><span><strong>Conservative cycle model</strong> {plan.summary.cycle_assumption}</span><button className="text-button" disabled={recalculating} onClick={recalc}>{recalculating ? "Recalculating…" : "Recalculate same trip"}</button></div>
  </main>;
}
