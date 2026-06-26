// Use: Super Admin — Global Health Dashboard showing platform stats, anomaly alerts, institution health table, and activity chart.

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { AlertTriangle, X, Building2, Users, Siren, BarChart3, TrendingUp, Eye, ScrollText } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface PlatformStats {
  total_institutions: number;
  active_users: number;
  weekly_incidents: number;
  avg_compliance: number;
}

interface AnomalyAlert {
  id: string;
  severity: string;
  message: string;
  timestamp: string;
  link: string;
}

interface Institution {
  institution_id: string;
  institution_name: string;
  institution_type: string;
  city: string;
  state: string;
  staff_count: number;
  is_active: boolean;
  compliance_percentage: number;
}

interface AuditLog {
  audit_log_id: string;
  institution_name: string;
  user_name: string;
  action_type: string;
  created_at: string;
}

function buildActivityData(logs: AuditLog[]) {
  const buckets = new Map<string, { date: string; logins: number; actions: number }>();

  for (let i = 13; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const key = d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
    buckets.set(key, { date: key, logins: 0, actions: 0 });
  }

  logs.forEach((log) => {
    const createdAt = new Date(log.created_at);
    if (Number.isNaN(createdAt.getTime())) return;
    const key = createdAt.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
    const bucket = buckets.get(key);
    if (!bucket) return;
    bucket.actions += 1;
    if (log.action_type === "login") bucket.logins += 1;
  });

  return Array.from(buckets.values());
}

function CompliancePill({ pct }: { pct: number }) {
  const color = pct > 80 ? "var(--success)" : pct > 50 ? "var(--warning)" : "var(--danger)";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: "var(--surface-raised)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: 12, fontWeight: 600, color, minWidth: 30 }}>{pct}%</span>
    </div>
  );
}

function InstitutionStatusBadge({ active, pct }: { active: boolean; pct: number }) {
  if (!active) return <span className="badge badge-inactive">Inactive</span>;
  if (pct > 80) return <span className="badge badge-compliant">Healthy</span>;
  if (pct > 50) return <span className="badge badge-in_progress">Warning</span>;
  return <span className="badge badge-non_compliant">Critical</span>;
}

export default function SuperAdminDashboard() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [alerts, setAlerts] = useState<AnomalyAlert[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [chartData, setChartData] = useState<{ date: string; logins: number; actions: number }[]>([]);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [statsRes, alertsRes, instRes, auditRes] = await Promise.allSettled([
          api.get("/api/v1/institutions/stats"),
          api.get("/api/v1/institutions/anomaly-alerts"),
          api.get("/api/v1/institutions"),
          api.get("/api/v1/audit/recent?limit=10"),
        ]);
        if (statsRes.status === "fulfilled") setStats(statsRes.value.data);
        if (alertsRes.status === "fulfilled") setAlerts(alertsRes.value.data.alerts ?? []);
        if (instRes.status === "fulfilled") setInstitutions(instRes.value.data);
        if (auditRes.status === "fulfilled") {
          const data = auditRes.value.data;
          setAuditLogs(data);
          setChartData(buildActivityData(data));
        }
      } catch { /* handled individually */ }
      setLoading(false);
    }
    load();
  }, []);

  const activeAlerts = alerts.filter((a) => !dismissedAlerts.has(a.id));
  const filtered = institutions.filter((i) =>
    i.institution_name.toLowerCase().includes(search.toLowerCase())
  );

  const ACTION_LABELS: Record<string, string> = {
    login: "Logged in",
    logout: "Logged out",
    user_created: "Created user",
    role_changed: "Changed role",
    login_failed: "Failed login attempt",
    evidence_approved: "Approved evidence",
    evidence_rejected: "Rejected evidence",
    reviewer_assigned: "Assigned reviewer",
    user_blocked: "Account blocked",
    password_reset_requested: "Requested password reset",
  };

  return (
    <PageShell
      title="Platform Overview"
      subtitle="System-wide health status across all registered institutions"
      actions={
        <Link to="/super-admin/tenants" className="btn btn-primary" style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Building2 size={15} /> Manage Institutions
        </Link>
      }
    >
      {/* Anomaly Alerts */}
      {activeAlerts.map((alert) => (
        <div key={alert.id} className="card" style={{ background: "var(--warning-bg)", border: "1px solid var(--warning)", marginBottom: 16, padding: "14px 18px", display: "flex", alignItems: "flex-start", gap: 12, borderRadius: 8 }}>
          <AlertTriangle size={18} style={{ color: "var(--warning)", flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontSize: 13, fontWeight: 500, color: "var(--text-primary)" }}>{alert.message}</p>
            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              <Link to={alert.link} style={{ fontSize: 12, color: "var(--primary)", fontWeight: 600 }}>Investigate →</Link>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{alert.timestamp}</span>
            </div>
          </div>
          <button onClick={() => setDismissedAlerts((s) => new Set([...s, alert.id]))} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 4 }}>
            <X size={16} />
          </button>
        </div>
      ))}

      {/* KPI Cards */}
      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: 24 }}>
        {[
          { icon: Building2, label: "Total Institutions", value: loading ? "—" : stats?.total_institutions ?? 0, link: "/super-admin/tenants", color: "var(--primary)" },
          { icon: Users, label: "Active Users", value: loading ? "—" : stats?.active_users ?? 0, color: "var(--success)" },
          { icon: Siren, label: "Incidents This Week", value: loading ? "—" : stats?.weekly_incidents ?? 0, color: (stats?.weekly_incidents ?? 0) > 5 ? "var(--danger)" : "var(--warning)" },
          { icon: BarChart3, label: "Avg Compliance Score", value: loading ? "—" : `${stats?.avg_compliance ?? 0}%`, color: "var(--info)" },
        ].map(({ icon: Icon, label, value, link, color }) => (
          <div key={label} className="stat-card">
            <div className="stat-card-icon" style={{ background: `${color}22`, color }}><Icon size={20} /></div>
            <div className="stat-card-value">{value}</div>
            <div className="stat-card-label">{label}</div>
            {link && <Link to={link} style={{ fontSize: 11, color: "var(--primary)", marginTop: 6, display: "block" }}>View all →</Link>}
          </div>
        ))}
      </div>

      {/* Institution Health Table */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">Institution Health</h2>
          <input
            className="form-input"
            placeholder="Search institutions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 220, fontSize: 13 }}
          />
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Institution Name</th>
                <th>Type</th>
                <th>City, State</th>
                <th>Staff</th>
                <th>Compliance</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={7} style={{ textAlign: "center", color: "var(--text-muted)", padding: "32px 16px" }}>No institutions registered yet.</td></tr>
              ) : (
                filtered.map((inst) => (
                  <tr key={inst.institution_id}>
                    <td style={{ fontWeight: 600 }}>{inst.institution_name}</td>
                    <td><span className="badge badge-draft">{inst.institution_type}</span></td>
                    <td style={{ color: "var(--text-secondary)", fontSize: 13 }}>{inst.city}, {inst.state}</td>
                    <td>{inst.staff_count ?? "—"}</td>
                    <td style={{ width: 150 }}><CompliancePill pct={inst.compliance_percentage} /></td>
                    <td><InstitutionStatusBadge active={inst.is_active} pct={inst.compliance_percentage} /></td>
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <Link to={`/super-admin/tenants/${inst.institution_id}`} className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}><Eye size={13} /> View</Link>
                        <Link to={`/super-admin/audit-trail?institution_id=${inst.institution_id}`} className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}><ScrollText size={13} /> Audit</Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom Row: Audit Events + Activity Chart */}
      <div className="grid-2" style={{ gap: 20 }}>
        <div className="card">
          <div className="card-header"><h2 className="card-title">Recent Audit Events</h2></div>
          <div>
            {auditLogs.length === 0 ? (
              <p style={{ color: "var(--text-muted)", padding: "16px 0", fontSize: 13 }}>No recent events.</p>
            ) : (
              auditLogs.slice(0, 10).map((log) => (
                <div key={log.audit_log_id} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-primary)" }}>
                      {log.institution_name && <span style={{ color: "var(--text-muted)" }}>{log.institution_name} · </span>}
                      {log.user_name || "System"}
                    </div>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                      {ACTION_LABELS[log.action_type] ?? log.action_type}
                    </div>
                  </div>
                  <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)", flexShrink: 0 }}>
                    {new Date(log.created_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              ))
            )}
            <Link to="/super-admin/audit-trail" style={{ fontSize: 12, color: "var(--primary)", display: "block", marginTop: 12, fontWeight: 600 }}>View full audit trail →</Link>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Platform Activity</h2>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Last 14 days</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 0, left: -20 }}>
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }} />
              <Line type="monotone" dataKey="logins" stroke="var(--primary)" strokeWidth={2} dot={false} name="Logins" />
              <Line type="monotone" dataKey="actions" stroke="var(--success)" strokeWidth={2} dot={false} name="Actions" />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
            <span style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 6, color: "var(--text-secondary)" }}><span style={{ width: 12, height: 3, background: "var(--primary)", borderRadius: 2, display: "inline-block" }} />Logins</span>
            <span style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 6, color: "var(--text-secondary)" }}><span style={{ width: 12, height: 3, background: "var(--success)", borderRadius: 2, display: "inline-block" }} />Actions</span>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
