import { useEffect, useState } from "react";
import { BookOpenText, Printer, RotateCcw, ShieldCheck } from "lucide-react";
import { ErrorBoundary } from "./ErrorBoundary";
import { PlannerForm } from "../features/trip-planner/PlannerForm";
import { TripWorkspace } from "./TripWorkspace";
import type { PlanInput, TripPlan } from "../types";
import { getTrip } from "../lib/api";

export default function App() {
  const [plan, setPlan] = useState<TripPlan | null>(null);
  const [lastInput, setLastInput] = useState<PlanInput | null>(null);
  const [restoring, setRestoring] = useState(() => new URLSearchParams(window.location.search).has("trip"));

  useEffect(() => {
    const tripId = new URLSearchParams(window.location.search).get("trip");
    if (!tripId) return;
    getTrip(tripId)
      .then(next => { setPlan(next); setLastInput(next.input); })
      .catch(() => window.history.replaceState({}, "", window.location.pathname))
      .finally(() => setRestoring(false));
  }, []);

  const revise = () => { setPlan(null); setLastInput(null); window.history.replaceState({}, "", window.location.pathname); };

  return <ErrorBoundary>
    <header className="app-header">
      <a className="brand" href="#top" aria-label="MileLedger home"><span className="brand-mark">ML</span><span><strong>MileLedger</strong><small>Hours & route planning</small></span></a>
      <div className="header-rule"><ShieldCheck size={16} /> FMCSA 395 · property carrier</div>
      {plan && <div className="header-actions">
        <button className="text-button" onClick={revise}><RotateCcw size={16} /> Revise trip</button>
        <button className="primary compact" onClick={() => window.print()}><Printer size={16} /> Print logs</button>
      </div>}
    </header>
    <div id="top">
      {restoring ? <main className="restore-state" aria-live="polite"><span className="spinner" /> Restoring saved trip…</main> : plan && lastInput
        ? <TripWorkspace plan={plan} input={lastInput} onPlan={setPlan} />
        : <PlannerForm onPlan={(next, input) => { setPlan(next); setLastInput(input); window.history.replaceState({}, "", `?trip=${next.trip_id}`); }} />}
    </div>
    <footer className="site-footer"><BookOpenText size={15} /> MileLedger is a planning demonstration—not an FMCSA-certified electronic logging device.</footer>
  </ErrorBoundary>;
}
