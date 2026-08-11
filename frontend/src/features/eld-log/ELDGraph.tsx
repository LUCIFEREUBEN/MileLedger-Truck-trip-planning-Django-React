import type { DailyLog, DutyStatus } from "../../types";
import { statusLabel } from "../../lib/format";

const rows: DutyStatus[] = ["OFF_DUTY", "SLEEPER_BERTH", "DRIVING", "ON_DUTY_NOT_DRIVING"];
const y = (status: DutyStatus) => 48 + rows.indexOf(status) * 46;
const x = (minute: number) => 86 + minute / 1440 * 696;

export function ELDGraph({ log, selectedEventId, onSelect }: { log: DailyLog; selectedEventId: string | null; onSelect: (id: string | null) => void }) {
  const events = log.events;
  let path = "";
  events.forEach((event, index) => {
    const startX = x(event.start_minute), endX = x(event.end_minute), rowY = y(event.status);
    path += index === 0 ? `M ${startX} ${rowY}` : ` V ${rowY}`;
    path += ` H ${endX}`;
  });
  const summary = rows.map(status => `${statusLabel[status]} ${Math.floor(log.totals_minutes[status] / 60)} hours ${log.totals_minutes[status] % 60} minutes`).join(", ");
  return <svg className="eld-graph" viewBox="0 0 890 220" role="img" aria-label={`Driver daily log for ${log.date}. ${summary}`}>
    <rect x="85" y="25" width="698" height="184" className="graph-paper" />
    {Array.from({ length: 97 }, (_, index) => <line key={`q${index}`} x1={x(index * 15)} x2={x(index * 15)} y1="25" y2="209" className={index % 4 === 0 ? "hour-grid" : "quarter-grid"} />)}
    {rows.map((status, index) => <g key={status}><line x1="85" x2="783" y1={25 + index * 46} y2={25 + index * 46} className="row-grid" /><text x="5" y={y(status) + 4} className="row-label">{statusLabel[status].replace(" · ", " ")}</text><text x="806" y={y(status) + 4} className="row-total">{(log.totals_minutes[status] / 60).toFixed(2)}</text></g>)}
    <line x1="85" x2="783" y1="209" y2="209" className="row-grid" />
    {Array.from({ length: 25 }, (_, hour) => <text key={hour} x={x(hour * 60)} y="17" textAnchor={hour === 0 ? "start" : hour === 24 ? "end" : "middle"} className="hour-label">{hour === 0 || hour === 24 ? "Mid" : hour === 12 ? "Noon" : hour % 12}</text>)}
    <text x="806" y="17" className="total-label">TOTAL</text>
    <path d={path} className="duty-path" />
    {events.filter(event => event.source_event_id).map(event => <g key={event.id} role="button" tabIndex={0} aria-label={`${event.remark}, ${event.duration_minutes} minutes`} onFocus={() => onSelect(event.source_event_id)} onMouseEnter={() => onSelect(event.source_event_id)} onClick={() => onSelect(event.source_event_id)} onKeyDown={key => { if (key.key === "Enter" || key.key === " ") onSelect(event.source_event_id); }}>
      <rect x={x(event.start_minute)} y={y(event.status) - 13} width={Math.max(3, x(event.end_minute) - x(event.start_minute))} height="26" className="event-hit" />
      {selectedEventId === event.source_event_id && <line x1={x(event.start_minute)} x2={x(event.end_minute)} y1={y(event.status)} y2={y(event.status)} className="selected-path" />}
    </g>)}
  </svg>;
}

