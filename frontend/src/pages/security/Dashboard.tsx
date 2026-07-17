// Use: Dashboard highlighting technical control status and recent incidents.

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

interface IncidentSummary {
  incident_id: string;
  title: string;
  severity: string;
  status: string;
  incident_type?: string;
  detected_at?: string;
  cert_in_deadline?: string;
  cert_in_reported: boolean;
}

interface DashboardStats {
  active_incidents: number;
  critical_incidents: number;
  pending_cert_in: number;
  compliance_rate: number;
  last_incident_created?: string | null;
  timeline: Array<{ label: string; on_time: number; late: number; not_reported: number }>;
}

function relativeTime(value?: string | null) {
  if (!value) return "";
  const diff = Date.now() - new Date(value).getTime();
  const hours = Math.max(1, Math.round(diff / (1000 * 60 * 60)));
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

function formatDeadline(incident: IncidentSummary) {
  if (incident.cert_in_reported) return "Filed ✓";
  if (!incident.cert_in_deadline) return "—";
  const deadline = new Date(incident.cert_in_deadline);
  const diff = deadline.getTime() - Date.now();
  if (diff <= 0) return "OVERDUE";
  const hours = Math.max(1, Math.round(diff / 3600000));
  return `${hours}h left`;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);

  const { data: statsData, loading: loadingStats, error: statsError, refetch: refetchStats } = useApi(async () => {
    const res = await api.get<DashboardStats>("/api/v1/incidents/dashboard-stats");
    return res.data;
  }, []);

  const { data: incidentsData, loading: loadingIncidents, error: incidentsError, refetch: refetchIncidents } = useApi(async () => {
    const res = await api.get<IncidentSummary[]>("/api/v1/incidents", { params: { limit: 5 } });
    return Array.isArray(res.data) ? res.data : res.data?.incidents ?? [];
  }, []);

  useState(() => {
    if (statsData) setStats(statsData as DashboardStats);
    if (incidentsData) setIncidents(incidentsData as IncidentSummary[]);
    return undefined;
  });

  const criticalAlert = useMemo(() => {
    if (!stats) return false;
    return stats.critical_incidents > 0 || stats.pending_cert_in > 0;
  }, [stats]);

  return (
    <div className="page-panel">
      <PageShell title="Security Dashboard" context="Morning control health and active incident posture." />
      {criticalAlert ? (
        <div style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b", padding: 14, borderRadius: 10, marginTop: 16 }}>
          <strong>🚨 Active critical response:</strong> {stats?.critical_incidents ?? 0} critical or pending reporting items require immediate attention.
        </div>
      ) : null}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginTop: 16 }}>
        {loadingStats || loadingIncidents ? (
          Array.from({ length: 5 }).map((_, idx) => <div key={idx} style={{ padding: 16, borderRadius: 12, border: "1px solid #e5e7eb", background: "#fff" }}><Loading /></div>)
        ) : statsError || incidentsError ? (
          <div style={{ gridColumn: "1 / -1" }}><ErrorState message={(statsError || incidentsError)?.message} onRetry={() => { void refetchStats(); void refetchIncidents(); }} /></div>
        ) : (
          <>
            <div style={{ padding: 16, borderRadius: 12, border: "1px solid #e5e7eb", background: "#fff" }}>
              <div style={{ color: "#6b7280", fontSize: 12 }}>IT Controls Assigned</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats?.active_incidents ?? 0} active</div>
              <Link to="/security/controls">Review controls</Link>
            </div>
            <div style={{ padding: 16, borderRadius: 12, border: "1px solid #e5e7eb", background: "#fff" }}>
              <div style={{ color: "#6b7280", fontSize: 12 }}>Open Incidents</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: stats?.active_incidents ? "#dc2626" : "#16a34a" }}>{stats?.active_incidents ?? 0}</div>
              <Link to="/security/incidents">Manage incidents</Link>
            </div>
            <div style={{ padding: 16, borderRadius: 12, border: "1px solid #e5e7eb", background: "#fff" }}>
              <div style={{ color: "#6b7280", fontSize: 12 }}>CERT-In Pending</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: (stats?.pending_cert_in ?? 0) > 0 ? "#dc2626" : "#16a34a" }}>{stats?.pending_cert_in ?? 0}</div>
            </div>
            <div style={{ padding: 16, borderRadius: 12, border: "1px solid #e5e7eb", background: "#fff" }}>
              <div style={{ color: "#6b7280", fontSize: 12 }}>Critical Severity</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: "#dc2626" }}>{stats?.critical_incidents ?? 0}</div>
            </div>
            <div style={{ padding: 16, borderRadius: 12, border: "1px solid #e5e7eb", background: "#fff" }}>
              <div style={{ color: "#6b7280", fontSize: 12 }}>Last Incident Closed</div>
              <div style={{ fontSize: 18, fontWeight: 700 }}>{stats?.last_incident_created ? relativeTime(stats.last_incident_created) : "No incidents this month"}</div>
            </div>
          </>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 16, marginTop: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Assigned Controls</h3>
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            {[
              { label: "Compliant", value: 8, color: "#16a34a" },
              { label: "In Progress", value: 3, color: "#2563eb" },
              { label: "Non-Compliant", value: 2, color: "#dc2626" },
              { label: "Not Started", value: 1, color: "#9ca3af" }
            ].map((item) => (
              <div key={item.label} style={{ flex: 1, textAlign: "center" }}>
                <div style={{ fontSize: 12, color: "#6b7280" }}>{item.label}</div>
                <div style={{ height: 6, borderRadius: 999, background: "#f3f4f6", marginTop: 4, overflow: "hidden" }}>
                  <div style={{ width: `${item.value * 10}%`, height: "100%", background: item.color }} />
                </div>
              </div>
            ))}
          </div>
          <div style={{ color: "#6b7280", fontSize: 13 }}>Critical non-compliant controls are highlighted for review.</div>
          <Link to="/security/controls">View all controls →</Link>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Active Incidents</h3>
          {incidents.length === 0 ? <div style={{ color: "#16a34a" }}>No active incidents</div> : incidents.map((incident) => (
            <div key={incident.incident_id} style={{ borderTop: "1px solid #f3f4f6", padding: "8px 0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                <strong>{incident.title}</strong>
                <span style={{ color: incident.severity === "critical" ? "#dc2626" : "#d97706", fontSize: 12 }}>{incident.severity}</span>
              </div>
              <div style={{ fontSize: 12, color: "#6b7280" }}>{incident.incident_type ?? "Incident"} • {relativeTime(incident.detected_at)}</div>
              <div style={{ fontSize: 12, color: incident.cert_in_reported ? "#16a34a" : "#b45309" }}>{formatDeadline(incident)}</div>
              <Link to={`/security/incidents/${incident.incident_id}`}>View →</Link>
            </div>
          ))}
          <Link to="/security/incidents/new">+ Log New Incident</Link>
        </div>
      </div>

      <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Incident History — Last 90 Days</h3>
        <div style={{ width: "100%", height: 220 }}>
          <ResponsiveContainer>
            <BarChart data={stats?.timeline ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="on_time" stackId="a" fill="#16a34a" />
              <Bar dataKey="late" stackId="a" fill="#f59e0b" />
              <Bar dataKey="not_reported" stackId="a" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ marginTop: 8, color: "#4b5563" }}>CERT-In Reporting: {stats?.compliance_rate ?? 0}% on time in the last 90 days.</div>
      </div>
    </div>
  );
}
