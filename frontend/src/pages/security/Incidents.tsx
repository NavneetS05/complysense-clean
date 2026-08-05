// Use: Security incident logs registry and tracker.

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";

interface IncidentItem {
  incident_id: string;
  title: string;
  severity: string;
  status: string;
  incident_type?: string;
  detected_at?: string;
  cert_in_deadline?: string;
  cert_in_reported: boolean;
  assigned_to?: string | null;
}

function relativeTime(value?: string | null) {
  if (!value) return "";
  const diff = Date.now() - new Date(value).getTime();
  const hours = Math.max(1, Math.round(diff / (1000 * 60 * 60)));
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

function formatDeadline(incident: IncidentItem) {
  if (incident.cert_in_reported) return "Filed ✓";
  if (!incident.cert_in_deadline) return "—";
  const deadline = new Date(incident.cert_in_deadline);
  const diff = deadline.getTime() - Date.now();
  if (diff <= 0) return "OVERDUE";
  const hours = Math.max(1, Math.round(diff / 3600000));
  return `${hours}h left`;
}

export default function Incidents() {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [confirmCloseId, setConfirmCloseId] = useState<string | null>(null);
  const [closing, setClosing] = useState(false);

  const toast = useToast();

  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/incidents", { params: { limit: 100 } });
    const payload = res.data as IncidentItem[] | { incidents?: IncidentItem[] };
    return Array.isArray(payload) ? payload : payload.incidents ?? [];
  }, []);

  useEffect(() => {
    if (!data) return;
    setIncidents(data as IncidentItem[]);
  }, [data]);

  const filtered = useMemo(() => {
    return incidents.filter((incident) => statusFilter === "all" || incident.status === statusFilter);
  }, [incidents, statusFilter]);

  const counts = useMemo(() => {
    return {
      all: incidents.length,
      open: incidents.filter((incident) => incident.status === "open").length,
      investigating: incidents.filter((incident) => incident.status === "investigating").length,
      contained: incidents.filter((incident) => incident.status === "contained").length,
      resolved: incidents.filter((incident) => incident.status === "resolved").length,
      closed: incidents.filter((incident) => incident.status === "closed").length
    };
  }, [incidents]);

  async function closeIncident(incidentId: string) {
    setClosing(true);
    try {
      await api.patch(`/api/v1/incidents/${incidentId}`, { status: "closed" });
      toast.success("Incident closed successfully.");
      await refetch();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to close incident."));
    } finally {
      setClosing(false);
      setConfirmCloseId(null);
    }
  }

  return (
    <div className="page-panel">
      <PageShell title="Incidents" context="Security incident register and response tracker." />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {([
            ["all", counts.all],
            ["open", counts.open],
            ["investigating", counts.investigating],
            ["contained", counts.contained],
            ["resolved", counts.resolved],
            ["closed", counts.closed]
          ] as Array<[string, number]>).map(([key, count]) => (
            <button key={key} onClick={() => setStatusFilter(key)} style={{ padding: "6px 10px", borderRadius: 999, border: statusFilter === key ? "1px solid #2563eb" : "1px solid #d1d5db", background: statusFilter === key ? "#eff6ff" : "#fff" }}>
              {key === "all" ? "All" : key[0].toUpperCase() + key.slice(1)} ({count})
            </button>
          ))}
        </div>
        <Link to="/security/incidents/new">+ Log New Incident</Link>
      </div>
      <div style={{ overflowX: "auto", marginTop: 16 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb" }}>
              <th style={{ padding: 10 }}>Severity</th>
              <th style={{ padding: 10 }}>Title</th>
              <th style={{ padding: 10 }}>Type</th>
              <th style={{ padding: 10 }}>Status</th>
              <th style={{ padding: 10 }}>Detected</th>
              <th style={{ padding: 10 }}>CERT-In</th>
              <th style={{ padding: 10 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} style={{ padding: 16 }}><Loading /></td></tr>
            ) : error ? (
              <tr><td colSpan={7} style={{ padding: 16 }}><ErrorState message={error.message} onRetry={() => void refetch()} /></td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={7} style={{ padding: 16 }}><EmptyState title="No incidents" description="No incidents logged." /></td></tr>
            ) : filtered.map((incident) => (
              <tr key={incident.incident_id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                <td style={{ padding: 10 }}>{incident.severity}</td>
                <td style={{ padding: 10 }}><Link to={`/security/incidents/${incident.incident_id}`}>{incident.title}</Link></td>
                <td style={{ padding: 10 }}>{incident.incident_type ?? "Other"}</td>
                <td style={{ padding: 10 }}>{incident.status}</td>
                <td style={{ padding: 10 }}>{relativeTime(incident.detected_at)}</td>
                <td style={{ padding: 10 }}>{formatDeadline(incident)}</td>
                <td style={{ padding: 10 }}>
                  <Link to={`/security/incidents/${incident.incident_id}`}>View</Link>
                  {incident.status === "resolved" ? <span> • <button onClick={() => setConfirmCloseId(incident.incident_id)} style={{ border: 0, background: "transparent", color: "#2563eb", cursor: "pointer" }}>Close</button></span> : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmModal
        open={confirmCloseId !== null}
        title="Close Incident"
        description="Are you sure you want to mark this incident as closed? This action cannot be undone."
        confirmLabel="Close Incident"
        confirmVariant="destructive"
        loading={closing}
        onConfirm={() => confirmCloseId && void closeIncident(confirmCloseId)}
        onCancel={() => setConfirmCloseId(null)}
      />
    </div>
  );
}

