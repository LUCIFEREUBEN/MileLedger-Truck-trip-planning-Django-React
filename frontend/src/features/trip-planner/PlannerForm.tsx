import { useMemo, useState } from "react";
import { ArrowRight, ChevronDown, CircleCheck, MapPinned, Route, ShieldCheck, TimerReset } from "lucide-react";
import { ApiError, planTrip } from "../../lib/api";
import type { PlanInput, TripPlan } from "../../types";

const shortExample: PlanInput = {
  current_location: "Louisville, KY", pickup_location: "Nashville, TN", dropoff_location: "Memphis, TN",
  cycle_used_hours: "28.25", log_timezone: "America/Chicago",
};
const longExample: PlanInput = {
  current_location: "Seattle, WA", pickup_location: "Denver, CO", dropoff_location: "Miami, FL",
  cycle_used_hours: "48.5", log_timezone: "America/Denver",
};
const stages = ["Resolving locations", "Building truck route", "Scheduling duty periods", "Validating compliance", "Drawing daily logs"];

export function PlannerForm({ onPlan }: { onPlan: (plan: TripPlan, input: PlanInput) => void }) {
  const [input, setInput] = useState<PlanInput>({ ...shortExample, current_location: "", pickup_location: "", dropoff_location: "", cycle_used_hours: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState(0);
  const [requestError, setRequestError] = useState<string | null>(null);
  const startLocal = useMemo(() => {
    const local = new Date(Date.now() + 5 * 60_000);
    local.setSeconds(0, 0);
    return local.toISOString().slice(0, 16);
  }, []);

  const update = (key: keyof PlanInput, value: string) => {
    setInput(current => ({ ...current, [key]: value }));
    setErrors(current => ({ ...current, [key]: "" }));
  };

  const validate = () => {
    const next: Record<string, string> = {};
    for (const key of ["current_location", "pickup_location", "dropoff_location"] as const) if (!input[key].trim()) next[key] = "Enter a location.";
    const hours = Number(input.cycle_used_hours);
    if (input.cycle_used_hours === "" || Number.isNaN(hours) || hours < 0 || hours > 70) next.cycle_used_hours = "Enter a value from 0 to 70 hours.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validate()) return;
    setBusy(true); setRequestError(null); setStage(0);
    const timers = stages.slice(1).map((_, index) => window.setTimeout(() => setStage(index + 1), 280 * (index + 1)));
    try {
      const payload = { ...input, start_datetime: input.start_datetime ? new Date(input.start_datetime).toISOString() : new Date(startLocal).toISOString() };
      const [plan] = await Promise.all([planTrip(payload), new Promise(resolve => window.setTimeout(resolve, 1_300))]);
      onPlan(plan, payload);
    } catch (error) {
      if (error instanceof ApiError) {
        setRequestError(error.detail.message);
        setErrors(Object.fromEntries(Object.entries(error.detail.field_errors).map(([key, value]) => [key, value[0]])));
      } else setRequestError("The trip could not be planned. Your entries are still here—please try again.");
    } finally {
      timers.forEach(clearTimeout); setBusy(false);
    }
  };

  return <main className="planner-page">
    <section className="planner-intro">
      <p className="eyebrow">Property-carrying · 70-hour / 8-day cycle</p>
      <h1>Plan the road.<br /><em>Account for every hour.</em></h1>
      <p className="lede">A route plan, a legal duty schedule and a paper-faithful daily log—built together, explained line by line.</p>
      <div className="intro-proof">
        <span><Route /> Truck-aware route</span><span><TimerReset /> Automatic breaks & rest</span><span><ShieldCheck /> Explainable checks</span>
      </div>
      <div className="log-preview" aria-hidden="true">
        <div className="preview-head"><span>DRIVER'S DAILY LOG</span><span>24 HOURS</span></div>
        {[0,1,2,3].map(row => <div className="preview-row" key={row}><small>{["OFF","SB","D","ON"][row]}</small><i className={`preview-line p${row}`} /></div>)}
        <div className="preview-note"><CircleCheck /> 24 hours accounted for</div>
      </div>
    </section>
    <section className="planner-sheet" aria-labelledby="planner-title">
      <div className="sheet-number">ML / 001</div>
      <p className="eyebrow">New trip plan</p><h2 id="planner-title">Where are you headed?</h2>
      <p>Four details are enough to build the first compliant plan.</p>
      {requestError && <div className="error-summary" role="alert"><strong>Plan not created</strong><span>{requestError}</span></div>}
      <form onSubmit={submit} noValidate>
        <Field label="Current location" name="current_location" value={input.current_location} error={errors.current_location} placeholder="City, state or address" onChange={update} />
        <div className="route-thread" aria-hidden="true"><i /><i /><i /></div>
        <Field label="Pickup location" name="pickup_location" value={input.pickup_location} error={errors.pickup_location} placeholder="Pickup city or address" onChange={update} />
        <Field label="Drop-off location" name="dropoff_location" value={input.dropoff_location} error={errors.dropoff_location} placeholder="Delivery city or address" onChange={update} />
        <Field label="Current cycle used" name="cycle_used_hours" value={input.cycle_used_hours} error={errors.cycle_used_hours} placeholder="0–70" suffix="hours" inputMode="decimal" onChange={update} />
        <div className="form-row">
          <label><span>Trip starts</span><input type="datetime-local" value={input.start_datetime ?? startLocal} onChange={event => update("start_datetime", event.target.value)} /></label>
          <label><span>Log time zone</span><select value={input.log_timezone} onChange={event => update("log_timezone", event.target.value)}><option>America/Chicago</option><option>America/New_York</option><option>America/Denver</option><option>America/Los_Angeles</option><option>UTC</option></select></label>
        </div>
        <details className="log-details"><summary>Log details <ChevronDown size={16} /></summary><div className="optional-grid">
          <Field label="Driver name" name="driver_name" value={input.driver_name ?? ""} onChange={update} />
          <Field label="Carrier name" name="carrier_name" value={input.carrier_name ?? ""} onChange={update} />
          <Field label="Main office address" name="main_office_address" value={input.main_office_address ?? ""} onChange={update} />
          <Field label="Vehicle / unit" name="vehicle_number" value={input.vehicle_number ?? ""} onChange={update} />
          <Field label="Shipping document" name="shipping_document_number" value={input.shipping_document_number ?? ""} onChange={update} />
          <Field label="Shipper & commodity" name="shipper_commodity" value={input.shipper_commodity ?? ""} onChange={update} />
        </div></details>
        <button className="primary submit" disabled={busy}>{busy ? <><span className="spinner" /> {stages[stage]}…</> : <>Build compliant trip plan <ArrowRight size={18} /></>}</button>
        <div className="sr-only" aria-live="polite">{busy ? stages[stage] : requestError ?? ""}</div>
      </form>
      <div className="examples"><span>Try a verified fixture</span><button type="button" onClick={() => { setInput(shortExample); setErrors({}); }}>Load short example</button><button type="button" onClick={() => { setInput(longExample); setErrors({}); }}>Load multi-day example</button></div>
      <p className="fixture-note"><MapPinned size={14} /> Demo routes are clearly labelled. Configure OpenRouteService for live HGV routing.</p>
    </section>
  </main>;
}

function Field({ label, name, value, error, placeholder, suffix, inputMode, onChange }: { label: string; name: keyof PlanInput; value: string; error?: string; placeholder?: string; suffix?: string; inputMode?: "decimal"; onChange: (key: keyof PlanInput, value: string) => void }) {
  const id = `field-${name}`;
  return <label className={`field ${error ? "invalid" : ""}`} htmlFor={id}><span>{label}{name === "cycle_used_hours" && <b> Required</b>}</span><div className="input-wrap"><input id={id} name={name} value={value} placeholder={placeholder} inputMode={inputMode} aria-invalid={!!error} aria-describedby={error ? `${id}-error` : undefined} onChange={event => onChange(name, event.target.value)} />{suffix && <small>{suffix}</small>}</div>{error && <em id={`${id}-error`}>{error}</em>}</label>;
}

