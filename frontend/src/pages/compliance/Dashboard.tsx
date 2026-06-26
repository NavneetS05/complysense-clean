// Use: Dashboard interface for compliance gaps, tasks, and completion metrics.

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";

type DashboardStats = {
  total_controls: number;
  compliant_controls: number;
  non_compliant_controls: number;
  active_gaps: number;
  critical_gaps: number;
  high_gaps: number;
  pending_evidence: number;
  overdue_tasks: number;
  active_assessments: number;
};

type DashboardRow = {
  title: string;
  severity: string;
  framework_name: string;
  control_id?: string;
  remediation_status: string;
};

type EvidenceRow = {
  evidence_id: string;
  file_name: string;
  control_id?: string;
  approval_status: string;
  uploaded_at?: string;
};

type OverdueControl = {
  assignment_id: string;
  control_id: string;
  framework_name: string;
  due_date?: string;
  status: string;
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [triage, setTriage] = useState<DashboardRow[]>([]);
  const [todayActions, setTodayActions] = useState<Array<{ title: string; href: string }>>([]);
  const [evidenceQueue, setEvidenceQueue] = useState<EvidenceRow[]>([]);
  const [overdueControls, setOverdueControls] = useState<OverdueControl[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/compliance/dashboard");
        setStats(data.stats);
        setTriage(data.triage || []);
        setTodayActions(data.today_actions || []);
        setEvidenceQueue(data.evidence_queue || []);
        setOverdueControls(data.overdue_controls || []);
      } catch {
        setStats({
          total_controls: 0,
          compliant_controls: 0,
          non_compliant_controls: 0,
          active_gaps: 0,
          critical_gaps: 0,
          high_gaps: 0,
          pending_evidence: 0,
          overdue_tasks: 0,
          active_assessments: 0,
        });
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const completionRate = useMemo(() => {
    if (!stats || stats.total_controls === 0) return 0;
    return Math.round((stats.compliant_controls / stats.total_controls) * 100);
  }, [stats]);

  return (
    <div className="page-panel">
      <h2>Compliance Dashboard</h2>
      <p>Operational view of the controls, gaps, evidence, and tasks requiring attention.</p>

      {loading ? (
        <p>Loading compliance workspace…</p>
      ) : (
        <>
          <div className="stat-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16, marginTop: 16 }}>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Controls Compliant</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats?.compliant_controls ?? 0} / {stats?.total_controls ?? 0}</div>
              <div style={{ color: "var(--success)", fontSize: 12 }}>{completionRate}% complete</div>
            </div>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Active Gaps</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats?.active_gaps ?? 0}</div>
              <div style={{ fontSize: 12 }}>Critical: {stats?.critical_gaps ?? 0} · High: {stats?.high_gaps ?? 0}</div>
            </div>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Evidence Pending</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats?.pending_evidence ?? 0}</div>
              <Link to="/compliance/evidence-queue" style={{ color: "var(--primary)", fontSize: 12 }}>View queue →</Link>
            </div>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Tasks Overdue</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats?.overdue_tasks ?? 0}</div>
              <Link to="/compliance/tasks" style={{ color: "var(--primary)", fontSize: 12 }}>View tasks →</Link>
            </div>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Assessments Active</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats?.active_assessments ?? 0}</div>
              <Link to="/compliance/assessments" style={{ color: "var(--primary)", fontSize: 12 }}>Open assessments →</Link>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 16, marginTop: 16 }}>
            <div className="card" style={{ padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>AI Priority Triage</h3>
              <p style={{ color: "var(--muted)", marginTop: -4 }}>Top items requiring attention today.</p>
              {triage.length === 0 ? (
                <p>No open gaps requiring immediate review.</p>
              ) : (
                <ul style={{ paddingLeft: 18 }}>
                  {triage.map((item, idx) => (
                    <li key={`${item.title}-${idx}`} style={{ marginBottom: 10 }}>
                      <strong>{idx + 1}. {item.title}</strong>
                      <div style={{ fontSize: 12, color: "var(--muted)" }}>{item.framework_name} · {item.severity.toUpperCase()}</div>
                      {item.control_id ? <div style={{ fontSize: 12 }}>Control: {item.control_id}</div> : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="card" style={{ padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>Your Actions Today</h3>
              <ul style={{ paddingLeft: 18 }}>
                {todayActions.map((item) => (
                  <li key={item.title} style={{ marginBottom: 8 }}>
                    <Link to={item.href}>{item.title}</Link>
                  </li>
                ))}
                {todayActions.length === 0 ? <li>No actions derived from current records.</li> : null}
              </ul>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
            <div className="card" style={{ padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>Evidence Queue</h3>
              {evidenceQueue.length === 0 ? <p>No pending evidence at the moment.</p> : (
                <ul style={{ paddingLeft: 18 }}>
                  {evidenceQueue.map((item) => (
                    <li key={item.evidence_id} style={{ marginBottom: 8 }}>
                      <strong>{item.file_name}</strong>
                      <div style={{ fontSize: 12, color: "var(--muted)" }}>{item.control_id ?? "Unassigned"} · {item.approval_status}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="card" style={{ padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>Overdue Controls</h3>
              {overdueControls.length === 0 ? <p>No overdue controls confirmed.</p> : (
                <ul style={{ paddingLeft: 18 }}>
                  {overdueControls.map((item) => (
                    <li key={item.assignment_id} style={{ marginBottom: 8 }}>
                      <strong>{item.control_id}</strong>
                      <div style={{ fontSize: 12, color: "var(--muted)" }}>{item.framework_name} · {item.status}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
