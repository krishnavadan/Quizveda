"use client";

import { useEffect, useState } from "react";
import { adminRequest } from "@/lib/admin-api";

type AuditEvent = {
  id: string;
  actor_subject: string;
  action: string;
  resource_type: string;
  resource_id: string;
  reference?: string | null;
  occurred_at?: string | null;
};
type AuditResponse = { items: AuditEvent[] };

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminRequest<AuditResponse>("/audit-events?limit=100&offset=0")
      .then(result => setEvents(result.items ?? []))
      .catch(err => setError(err instanceof Error ? err.message : "Unable to load audit history."))
      .finally(() => setLoading(false));
  }, []);

  return <main className="detail-wrap"><a className="back-link" href="/admin">← Back to overview</a><header className="detail-header"><div><span className="eyebrow">GOVERNANCE / TRACEABILITY</span><h1>Audit history</h1><p className="muted">Recorded administrator actions for content lifecycle changes.</p></div></header>{error && <div className="error-panel" role="alert"><strong>Audit history unavailable</strong><p>{error}</p><small>Access requires the administrator role. The backend enforces this permission.</small></div>}{loading ? <div className="empty-state">Loading audit events…</div> : !error && events.length === 0 ? <div className="empty-state">No audit events have been recorded.</div> : !error && <div className="data-section table-wrap"><table><thead><tr><th>Time</th><th>Action</th><th>Actor</th><th>Resource</th><th>Reference</th></tr></thead><tbody>{events.map(event=><tr key={event.id}><td>{event.occurred_at ? new Date(event.occurred_at).toLocaleString() : "—"}</td><td><strong>{event.action}</strong></td><td>{event.actor_subject}</td><td><small>{event.resource_type}</small>{event.resource_id}</td><td>{event.reference ?? "—"}</td></tr>)}</tbody></table></div>}</main>;
}
