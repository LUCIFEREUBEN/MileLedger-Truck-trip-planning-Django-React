import { CircleCheck, PenLine } from "lucide-react";
import type { DailyLog } from "../../types";
import { ELDGraph } from "./ELDGraph";
import { formatDuration, statusLabel } from "../../lib/format";

export function DailyLogSheet({ log, dayIndex, dayCount, selectedEventId, onSelect }: { log: DailyLog; dayIndex: number; dayCount: number; selectedEventId: string | null; onSelect: (id: string | null) => void }) {
  const meta = log.metadata;
  return <article className="daily-log" aria-labelledby={`log-${log.date}`}>
    <div className="log-document-head"><div><p>MILELEDGER / RECORD OF DUTY STATUS</p><h2 id={`log-${log.date}`}>Driver’s Daily Log</h2></div><div><strong>{new Date(`${log.date}T12:00:00`).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</strong><span>Day {dayIndex + 1} of {dayCount} · {log.timezone}</span></div></div>
    <div className="log-meta"><Meta label="Driver" value={meta.driver_name} /><Meta label="Carrier" value={meta.carrier_name} /><Meta label="Main office" value={meta.main_office_address} wide /><Meta label="Vehicle / unit" value={meta.vehicle_number} /><Meta label="Miles today" value={`${log.miles_driven.toLocaleString()} mi`} /><Meta label="Shipping document" value={meta.shipping_document_number} /></div>
    <div className="graph-wrap"><ELDGraph log={log} selectedEventId={selectedEventId} onSelect={onSelect} /></div>
    <div className="log-lower">
      <section className="remarks"><div className="section-label"><span>Remarks / duty changes</span><small>LOCAL TIME</small></div>{log.events.filter(event => event.source_event_id).map(event => <button key={event.id} className={selectedEventId === event.source_event_id ? "selected" : ""} onClick={() => onSelect(event.source_event_id)}><time>{new Date(event.start).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", timeZone: log.timezone })}</time><span><strong>{event.remark}</strong><small>{event.location_label || statusLabel[event.status]}</small></span></button>)}</section>
      <aside className="status-totals"><div className="section-label">Daily totals</div>{Object.entries(log.totals_minutes).map(([status, minutes]) => <div key={status}><span>{statusLabel[status]}</span><strong>{formatDuration(minutes)}</strong></div>)}<p><CircleCheck /> <span>Accounted</span><strong>{log.total_minutes / 60}h</strong></p></aside>
    </div>
    <div className="signature"><span><PenLine /> Driver signature</span><i /><small>I certify these entries are true and correct.</small></div>
  </article>;
}

function Meta({ label, value, wide }: { label: string; value: string; wide?: boolean }) { return <div className={wide ? "wide" : ""}><small>{label}</small><strong>{value}</strong></div>; }
