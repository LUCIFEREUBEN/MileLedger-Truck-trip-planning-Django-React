import { BedDouble, CircleDot, Clock3, Fuel, MapPin, PackageCheck, PackageOpen, Pause } from "lucide-react";
import { formatDateTime, formatDuration, statusLabel } from "../../lib/format";
import type { DutyEvent, TripPlan } from "../../types";

const iconFor = (event: DutyEvent) => {
  if (event.reason_code === "PICKUP") return PackageOpen;
  if (event.reason_code === "DROPOFF") return PackageCheck;
  if (event.reason_code.includes("FUEL")) return Fuel;
  if (event.reason_code.includes("RESET")) return BedDouble;
  if (event.reason_code === "BREAK") return Pause;
  return CircleDot;
};

export function TripTimeline({ plan, selectedEventId, onSelect }: { plan: TripPlan; selectedEventId: string | null; onSelect: (id: string) => void }) {
  const visible = plan.events.filter((event, index) => event.status !== "DRIVING" || index === 0 || index === plan.events.length - 1);
  return <div className="timeline-panel">
    <div className="pane-heading"><div><p className="eyebrow">Duty sequence</p><h2>Trip timeline</h2></div><span>{plan.events.length} events</span></div>
    <div className="route-origin"><MapPin /><div><small>STARTING FROM</small><strong>{plan.route.addresses.current}</strong></div></div>
    <ol className="timeline-list">
      {visible.map((event, index) => {
        const Icon = iconFor(event); return <li key={event.id} className={selectedEventId === event.id ? "selected" : ""} style={{ "--delay": `${Math.min(index, 12) * 42}ms` } as React.CSSProperties}>
          <button onClick={() => onSelect(event.id)} onMouseEnter={() => onSelect(event.id)} onFocus={() => onSelect(event.id)}>
            <span className={`event-icon ${event.status.toLowerCase()}`}><Icon /></span>
            <span className="event-copy"><small>{formatDateTime(event.start, "America/Chicago")}</small><strong>{event.remark}</strong><em>{statusLabel[event.status]} · {formatDuration(event.duration_minutes)}</em></span>
          </button>
        </li>;
      })}
    </ol>
    <div className="timeline-summary"><Clock3 /><span><small>Raw drive</small><strong>{formatDuration(plan.route.raw_duration_minutes)}</strong></span><span><small>HOS plan</small><strong>{formatDuration(plan.summary.planned_duration_minutes)}</strong></span></div>
  </div>;
}

