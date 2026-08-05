// Use: Institution Admin — Risk Scorecard dashboard. KPIs, framework readiness bars, dept heatmap, AI risk panel, calendar preview, recent activity.

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useAuthStore } from "../../store/authStore";
import { BarChart3, AlertTriangle, Shield, Siren, Sparkles, RefreshCw } from "lucide-react";
import { getFrameworkColor } from "../../lib/frameworkColors";

interface DashboardStats {
  overall_compliance: number;
  compliance_delta: number;
  active_gaps: number;
  critical_gaps: number;
  high_gaps: number;
  overdue_controls: number;
  open_incidents: number;
  critical_incidents: number;
}

interface FrameworkReadiness {
  framework_name: string;
  percentage: number;
  trend: "up" | "down" | "flat";
}

interface DeptScore {
  department_name: string;
  compliance_score: number;
}

interface CalendarEvent {
  calendar_id: string;
  event_type: string;
  title: string;
  due_date: string;
  is_completed: boolean;
}

interface AuditLog {
  audit_log_id: string;
  user_name: string;
  action_type: string;
  created_at: string;
}

interface AIRisk {
  rank: number;
  framework: string;
  description: string;
  severity: "critical" | "high" | "medium";
  affected_dept: string;
}

const EVENT_COLORS: Record<string, string> = {
  control_due: "var(--primary)",
  assessment_scheduled: "#8b5cf6",
  evidence_expiry: "var(--warning)",
  policy_review: "#6366f1",
  vendor_contract_expiry: "#f97316",
  audit_scheduled: "var(--success)",
};

function TrendArrow({ trend }: { trend: "up" | "down" | "flat" }) {
  if (trend === "up") return <span style={{ color: "var(--success)", fontSize: 14 }}>↑</span>;
  if (trend === "down") return <span style={{ color: "var(--danger)", fontSize: 14 }}>↓</span>;
  return <span style={{ color: "var(--text-muted)", fontSize: 14 }}>→</span>;
}

function ProgressBar({ pct }: { pct: number }) {
  const color = pct > 75 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)";
  return (
    <div style={{ flex: 1, height: 8, background: "var(--surface-raised)", borderRadius: 4, overflow: "hidden" }}>
      <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 4, transition: "width 0.4s ease" }} />
    </div>
  );
}

function DeptHeatCard({ dept }: { dept: DeptScore }) {
  const s = dept.compliance_score;
  let bg = "#bbf7d0", text = "#15803d"; // green
  if (s < 75 && s >= 50) { bg = "#fef3c7"; text = "#d97706"; }
  if (s < 50) { bg = "#fee2e2"; text = "#dc2626"; }
  return (
    <div style={{ background: bg, borderRadius: 10, padding: "14px 16px", cursor: "pointer" }}
      onClick={() => {}}>
      <div style={{ fontWeight: 600, fontSize: 13, color: text }}>{dept.department_name}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: text, marginTop: 4 }}>{s}%</div>
    </div>
  );
}

export default function AdminDashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [frameworks, setFrameworks] = useState<FrameworkReadiness[]>([]);
  const [departments, setDepartments] = useState<DeptScore[]>([]);
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
  const [recentActivity, setRecentActivity] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [aiRisks, setAiRisks] = useState<AIRisk[] | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiGenTime, setAiGenTime] = useState<string | null>(null);

  async function loadDashboardData() {
    setLoading(true);
    const [dashboardRes, calRes, auditRes] = await Promise.allSettled([
      api.get("/api/v1/institutions/dashboard"),
      api.get("/api/v1/calendar"),
      api.get("/api/v1/audit/recent?limit=10"),
    ]);

    if (dashboardRes.status === "fulfilled") {
      const payload = dashboardRes.value.data;
      setStats(payload.stats);
      setFrameworks(payload.frameworks ?? []);
      setDepartments(payload.departments ?? []);
      setAiRisks(payload.ai_risks ?? []);
      setAiGenTime("Just now");
    }

    if (calRes.status === "fulfilled") setCalendarEvents(calRes.value.data.slice(0, 7));
    if (auditRes.status === "fulfilled") setRecentActivity(auditRes.value.data);
    setLoading(false);
  }

  useEffect(() => {
    void loadDashboardData();
  }, []);

  async function handleGenerateRiskHeatmap() {
    setAiLoading(true);
    try {
      const res = await api.post("/api/v1/ai/admin/risk-heatmap", {});
      // The AI endpoint returns { ai_risks: [...], raw_response: {...} }
      const risks = res.data?.ai_risks ?? [];
      if (Array.isArray(risks) && risks.length > 0) {
        setAiRisks(risks as AIRisk[]);
        setAiGenTime(new Date().toLocaleTimeString());
      } else {
        // Fallback: re-fetch dashboard static risks
        const dashRes = await api.get("/api/v1/institutions/dashboard");
        setAiRisks(dashRes.data.ai_risks ?? []);
        setAiGenTime("Just now");
      }
    } catch {
      // Keep existing list if refresh fails; surface nothing to user
    }
    setAiLoading(false);
  }

  const ACTION_LABELS: Record<string, string> = {
    login: "Logged in", user_created: "Created user", reviewer_assigned: "Assigned reviewer",
    evidence_approved: "Approved evidence", role_changed: "Changed role",
  };

  return (
    <PageShell
      title={`Risk Overview`}
      subtitle={`Welcome back, ${user?.email?.split("@")[0] ?? "Admin"} — Last updated just now`}
    >
      {/* KPI Cards */}
      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: 24 }}>
        {loading ? Array.from({ length: 4 }).map((_, i) => <div key={i} className="stat-card"><div className="skeleton" style={{ height: 60 }} /></div>) : (
          <>
            <div className="stat-card">
              <div className="stat-card-icon" style={{ background: "var(--primary-bg)", color: "var(--primary)" }}><BarChart3 size={20} /></div>
              <div className="stat-card-value">{stats?.overall_compliance}%</div>
              <div className="stat-card-label">Overall Compliance</div>
              <div style={{ fontSize: 12, marginTop: 4, color: (stats?.compliance_delta ?? 0) >= 0 ? "var(--success)" : "var(--danger)" }}>
                {(stats?.compliance_delta ?? 0) >= 0 ? "↑" : "↓"} {Math.abs(stats?.compliance_delta ?? 0)}% vs last month
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-icon" style={{ background: "var(--warning-bg)", color: "var(--warning)" }}><AlertTriangle size={20} /></div>
              <div className="stat-card-value">{stats?.active_gaps}</div>
              <div className="stat-card-label">Active Gaps</div>
              <div style={{ fontSize: 11, marginTop: 4, color: "var(--text-muted)" }}>
                Critical: {stats?.critical_gaps} · High: {stats?.high_gaps}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-icon" style={{ background: "var(--danger-bg)", color: "var(--danger)" }}><Shield size={20} /></div>
              <div className="stat-card-value" style={{ color: (stats?.overdue_controls ?? 0) > 0 ? "var(--danger)" : undefined }}>{stats?.overdue_controls}</div>
              <div className="stat-card-label">Overdue Controls</div>
              <Link to="/compliance/controls?status=overdue" style={{ fontSize: 11, color: "var(--primary)", marginTop: 4, display: "block" }}>View controls →</Link>
            </div>
            <div className="stat-card">
              <div className="stat-card-icon" style={{ background: "#fee2e2", color: "var(--danger)" }}><Siren size={20} /></div>
              <div className="stat-card-value" style={{ color: (stats?.critical_incidents ?? 0) > 0 ? "var(--danger)" : undefined }}>{stats?.open_incidents}</div>
              <div className="stat-card-label">Open Incidents</div>
              <div style={{ fontSize: 11, marginTop: 4, color: "var(--text-muted)" }}>Critical: {stats?.critical_incidents}</div>
            </div>
          </>
        )}
      </div>

      {/* Framework Bars + Dept Heatmap */}
      <div className="grid-2" style={{ gap: 20, marginBottom: 24 }}>
        <div className="card">
          <div className="card-header"><h2 className="card-title">Framework Compliance</h2></div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {frameworks.map((fw) => {
              const colors = getFrameworkColor(fw.framework_name);
              return (
                <div key={fw.framework_name}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, alignItems: "center" }}>
                    <span 
                      className="badge" 
                      style={{ 
                        backgroundColor: colors.bg, 
                        color: colors.text,
                        border: `1px solid ${colors.border}`
                      }}
                    >
                      {fw.framework_name}
                    </span>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: fw.percentage > 75 ? "var(--success)" : fw.percentage >= 50 ? "var(--warning)" : "var(--danger)" }}>{fw.percentage}%</span>
                      <TrendArrow trend={fw.trend} />
                    </div>
                  </div>
                  <ProgressBar pct={fw.percentage} />
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h2 className="card-title">Department Compliance</h2></div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {departments.map((d) => <DeptHeatCard key={d.department_name} dept={d} />)}
          </div>
        </div>
      </div>

      {/* AI Risk Heatmap Panel */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <h2 className="card-title">AI Risk Heatmap</h2>
            <span className="badge badge-in_progress" style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <Sparkles size={10} /> AI Insights
            </span>
          </div>
          {aiGenTime && <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Generated: {aiGenTime}</span>}
        </div>
        {aiRisks === null ? (
          <div style={{ textAlign: "center", padding: "32px 16px" }}>
            <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 16 }}>
              AI will analyze department summaries to predict emerging compliance risks
            </p>
            <button className="btn btn-primary" onClick={handleGenerateRiskHeatmap} disabled={aiLoading} style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
              {aiLoading ? <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Predicting risks...</> : <><Sparkles size={14} /> Generate Risk Prediction</>}
            </button>
          </div>
        ) : (
          <div>
            {aiRisks.map((risk) => (
              <div key={risk.rank} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "12px 0", borderBottom: "1px solid var(--border)" }}>
                <span style={{ width: 24, height: 24, borderRadius: "50%", background: "var(--primary-bg)", color: "var(--primary)", fontSize: 11, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{risk.rank}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-primary)" }}>{risk.description}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{risk.framework} · {risk.affected_dept}</div>
                </div>
                <span className={`badge badge-${risk.severity === "critical" ? "non_compliant" : risk.severity === "high" ? "submitted" : "in_progress"}`}>
                  {risk.severity.toUpperCase()}
                </span>
              </div>
            ))}
            <button className="btn btn-ghost" onClick={handleGenerateRiskHeatmap} disabled={aiLoading} style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
              <RefreshCw size={12} /> {aiLoading ? "Regenerating..." : "Regenerate"}
            </button>
          </div>
        )}
      </div>

      {/* Bottom Row */}
      <div className="grid-2" style={{ gap: 20 }}>
        {/* Upcoming Calendar Events */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Upcoming Events</h2>
            <Link to="/admin/calendar" style={{ fontSize: 12, color: "var(--primary)" }}>View calendar →</Link>
          </div>
          <div>
            {calendarEvents.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No upcoming events.</p>
            ) : calendarEvents.map((ev) => (
              <div key={ev.calendar_id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: EVENT_COLORS[ev.event_type] ?? "var(--text-muted)", flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>{ev.title}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{new Date(ev.due_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}</div>
                </div>
                <span className="badge badge-draft" style={{ fontSize: 10 }}>{ev.event_type.replace(/_/g, " ")}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="card-header"><h2 className="card-title">Recent Activity</h2></div>
          <div>
            {recentActivity.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No recent activity.</p>
            ) : recentActivity.slice(0, 10).map((log) => (
              <div key={log.audit_log_id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>{log.user_name ?? "System"}</span>
                  <span style={{ fontSize: 12, color: "var(--text-muted)", marginLeft: 8 }}>{ACTION_LABELS[log.action_type] ?? log.action_type}</span>
                </div>
                <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                  {new Date(log.created_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageShell>
  );
}
