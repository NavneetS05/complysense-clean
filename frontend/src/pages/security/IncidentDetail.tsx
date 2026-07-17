// Use: Incident control center with a 6-hour CERT-In countdown and AI draft reports.

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";

interface TimelineItem {
  action_taken: string;
  action_at?: string | null;
}

interface IncidentDetailData {
  incident_id: string;
  title: string;
  description?: string | null;
  severity: string;
  status: string;
  incident_type?: string | null;
  detected_at?: string | null;
  cert_in_deadline?: string | null;
  cert_in_reported: boolean;
  dpdp_notification_required: boolean;
  affected_systems?: string | null;
  affected_data_categories?: string | null;
  resolution_notes?: string | null;
  timeline: TimelineItem[];
}

function countdownLabel(deadline?: string | null) {
  if (!deadline) return "—";
  const diff = new Date(deadline).getTime() - Date.now();
  if (diff <= 0) return "OVERDUE";
  const hours = Math.max(1, Math.round(diff / 3600000));
  return `${hours}h remaining`;
}

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<IncidentDetailData | null>(null);
  const { data, loading, error, refetch } = useApi(async () => {
    if (!id) return null as any;
    const res = await api.get<IncidentDetailData>(`/api/v1/incidents/${id}`);
    return res.data as IncidentDetailData;
  }, [id]);

  useEffect(() => {
    if (!data) return;
    setIncident(data as IncidentDetailData | null);
  }, [data]);

  const deadlineHint = useMemo(() => countdownLabel(incident?.cert_in_deadline), [incident]);

  async function updateStatus(nextStatus: string) {
    if (!id) return;
    await api.patch(`/api/v1/incidents/${id}`, { status: nextStatus });
    await load();
  }

  if (loading) return <div className="page-panel"><Loading /></div>;
  if (error) return <div className="page-panel"><ErrorState message={error.message} onRetry={() => void refetch()} /></div>;
  if (!incident) return <div className="page-panel">Incident not found.</div>;

  return (
    <div className="page-panel">
      <PageShell title="Incident Command Center" context="CERT-In countdown and response workspace." />
      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 0.7fr", gap: 16, marginTop: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
            <div>
              <h3 style={{ margin: 0 }}>{incident.title}</h3>
              <div style={{ color: "#6b7280", fontSize: 13 }}>{incident.incident_type ?? "Incident"} • {incident.severity}</div>
            </div>
            <span style={{ padding: "6px 10px", borderRadius: 999, background: "#f3f4f6" }}>{incident.status}</span>
          </div>
          <p>{incident.description}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12, marginTop: 12 }}>
            <div style={{ background: "#f9fafb", borderRadius: 10, padding: 10 }}>
              <div style={{ fontSize: 12, color: "#6b7280" }}>Detected</div>
              <div>{incident.detected_at ? new Date(incident.detected_at).toLocaleString() : "—"}</div>
            </div>
            <div style={{ background: "#f9fafb", borderRadius: 10, padding: 10 }}>
              <div style={{ fontSize: 12, color: "#6b7280" }}>CERT-In deadline</div>
              <div>{incident.cert_in_deadline ? new Date(incident.cert_in_deadline).toLocaleString() : "—"}</div>
            </div>
          </div>
          <div style={{ marginTop: 12, background: incident.cert_in_reported ? "#ecfdf3" : "#fffbeb", border: `1px solid ${incident.cert_in_reported ? "#86efac" : "#fde68a"}`, borderRadius: 10, padding: 10 }}>
            {incident.cert_in_reported ? "CERT-In report filed." : `CERT-In deadline countdown: ${deadlineHint}`}
          </div>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Actions</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <button onClick={() => void updateStatus("investigating")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff" }}>Mark Investigating</button>
            <button onClick={() => void updateStatus("contained")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff" }}>Mark Contained</button>
            <button onClick={() => void updateStatus("resolved")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff" }}>Resolve</button>
            <button onClick={() => void updateStatus("closed")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff" }}>Close</button>
            <button onClick={() => navigate(-1)} style={{ padding: 10, borderRadius: 8, border: 0, background: "#2563eb", color: "#fff" }}>Back to register</button>
          </div>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Incident Details</h3>
          <div style={{ color: "#6b7280", fontSize: 14 }}><strong>Affected systems:</strong> {incident.affected_systems || "—"}</div>
          <div style={{ color: "#6b7280", fontSize: 14 }}><strong>Data categories:</strong> {incident.affected_data_categories || "—"}</div>
          <div style={{ color: "#6b7280", fontSize: 14 }}><strong>DPDP notification:</strong> {incident.dpdp_notification_required ? "Required" : "Not required"}</div>
          <div style={{ color: "#6b7280", fontSize: 14 }}><strong>Resolution notes:</strong> {incident.resolution_notes || "—"}</div>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Timeline</h3>
          {incident.timeline.length === 0 ? <div>No timeline entries yet.</div> : incident.timeline.map((entry, index) => (
            <div key={`${entry.action_taken}-${index}`} style={{ borderTop: index === 0 ? "0" : "1px solid #f3f4f6", paddingTop: index === 0 ? 0 : 8, marginTop: index === 0 ? 0 : 8 }}>
              <div>{entry.action_taken}</div>
              <div style={{ color: "#6b7280", fontSize: 12 }}>{entry.action_at ? new Date(entry.action_at).toLocaleString() : "—"}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
