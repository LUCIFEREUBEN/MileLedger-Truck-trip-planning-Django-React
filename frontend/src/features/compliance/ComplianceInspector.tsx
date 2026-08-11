import { useState } from "react";
import { Check, ChevronDown, ExternalLink, MapPin, ShieldCheck, X } from "lucide-react";
import type { ComplianceFinding } from "../../types";

export function ComplianceInspector({ findings, onHighlight, onClose }: { findings: ComplianceFinding[]; onHighlight: (ids: string[]) => void; onClose?: () => void }) {
  const [open, setOpen] = useState(findings[0]?.rule_id ?? "");
  return <aside className="inspector" aria-label="Compliance inspector">
    <div className="inspector-head"><div><p className="eyebrow">Rule-by-rule audit</p><h2>Compliance inspector</h2></div>{onClose && <button aria-label="Close inspector" onClick={onClose}><X /></button>}</div>
    <div className="inspector-score"><span><ShieldCheck /></span><div><strong>{findings.filter(item => item.state === "pass").length} of {findings.length} checks pass</strong><small>FMCSA property-carrier rules · no adverse exception</small></div></div>
    <div className="finding-list">{findings.map(item => <section key={item.rule_id} className={`finding ${item.state}`}>
      <button className="finding-summary" aria-expanded={open === item.rule_id} onClick={() => setOpen(current => current === item.rule_id ? "" : item.rule_id)}><i><Check /></i><span><strong>{item.title}</strong><small>{item.state}</small></span><ChevronDown /></button>
      {open === item.rule_id && <div className="finding-detail"><p>{item.explanation}</p><dl><div><dt>Calculation</dt><dd>{item.calculation}</dd></div><div><dt>Buffer</dt><dd>{item.remaining_buffer}</dd></div></dl>{item.event_ids.length > 0 && <div className="finding-actions"><button onClick={() => onHighlight(item.event_ids)}><ExternalLink /> Show on log</button>{item.can_show_on_map && <button onClick={() => onHighlight(item.event_ids)}><MapPin /> Show on map</button>}</div>}</div>}
    </section>)}</div>
    <p className="inspector-note">Conservative cycle accounting uses only the aggregate hours supplied. No rolling recapture is assumed.</p>
  </aside>;
}

