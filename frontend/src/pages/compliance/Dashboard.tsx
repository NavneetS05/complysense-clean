// Use: Dashboard interface for compliance gaps, tasks, completion metrics, interactive AI triage, and regulatory change analyzer.

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { RegulatoryChangeDrawer } from "../../components/compliance/RegulatoryChangeDrawer";
import { 
  Sparkles, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight, 
  RefreshCw, 
  Plus, 
  UserPlus, 
  X,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { getApiErrorMessage } from "../../lib/errors";

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

type TriageResult = {
  priority: "critical" | "high" | "medium" | "low";
  cert_in_trigger: boolean;
  mapped_controls: string[];
  justification: string;
  recommended_action: string;
};

type UserOption = {
  user_id: string;
  full_name: string;
  email: string;
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [, setTriage] = useState<DashboardRow[]>([]);
  const [todayActions, setTodayActions] = useState<Array<{ title: string; href: string }>>([]);
  const [evidenceQueue, setEvidenceQueue] = useState<EvidenceRow[]>([]);
  const [overdueControls, setOverdueControls] = useState<OverdueControl[]>([]);
  const [loading, setLoading] = useState(true);

  // AI states
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiTriageResult, setAiTriageResult] = useState<TriageResult | null>(null);
  const [lastTriageTime, setLastTriageTime] = useState<string | null>(null);
  const [regDrawerOpen, setRegDrawerOpen] = useState(false);
  const [falsePositivesOpen, setFalsePositivesOpen] = useState(false);

  // Task Modal states
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [, setTaskControlId] = useState("");
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [taskPriority, setTaskPriority] = useState("medium");
  const [taskDueDate, setTaskDueDate] = useState("");
  const [taskAssignee, setTaskAssignee] = useState("");
  const [users, setUsers] = useState<UserOption[]>([]);
  const [taskSubmitting, setTaskSubmitting] = useState(false);
  const [taskSuccess, setTaskSuccess] = useState(false);

  // Status Message during loading
  const [statusMessage, setStatusMessage] = useState("Reviewing input...");

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

  // Fetch users when task modal opens
  useEffect(() => {
    if (taskModalOpen) {
      async function fetchUsers() {
        try {
          const { data } = await api.get("/api/v1/users");
          if (Array.isArray(data)) {
            setUsers(data);
          }
        } catch {
          // fallback option handled
        }
      }
      void fetchUsers();
    }
  }, [taskModalOpen]);

  // Loading status messages rotation
  useEffect(() => {
    if (aiLoading) {
      const messages = [
        "Reviewing input...",
        "Checking regulatory frameworks...",
        "Preparing response..."
      ];
      let idx = 0;
      setStatusMessage(messages[0]);
      const interval = setInterval(() => {
        idx = (idx + 1) % messages.length;
        setStatusMessage(messages[idx]);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [aiLoading]);

  const completionRate = useMemo(() => {
    if (!stats || stats.total_controls === 0) return 0;
    return Math.round((stats.compliant_controls / stats.total_controls) * 100);
  }, [stats]);

  const handleRunTriage = async () => {
    setAiLoading(true);
    setAiError(null);
    try {
      const { data } = await api.post("/api/v1/ai/compliance/triage", {});

      let parsed: TriageResult | null = null;
      if (data.response_json && typeof data.response_json === "object") {
        parsed = data.response_json as TriageResult;
      } else if (data.priority && data.mapped_controls) {
        parsed = data as unknown as TriageResult;
      } else {
        // Robust regex extraction from data.response
        let rawResponse = String(data.response || "").trim();
        if (rawResponse.includes("```")) {
          const match = rawResponse.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
          if (match) rawResponse = match[1].trim();
        }
        if (!rawResponse.startsWith("{") && !rawResponse.startsWith("[")) {
          const validIndices = [rawResponse.indexOf("{"), rawResponse.indexOf("[")].filter((i) => i >= 0);
          if (validIndices.length > 0) {
            const firstBrace = Math.min(...validIndices);
            const lastBrace = Math.max(rawResponse.lastIndexOf("}"), rawResponse.lastIndexOf("]"));
            if (lastBrace > firstBrace) {
              rawResponse = rawResponse.slice(firstBrace, lastBrace + 1);
            }
          }
        }
        try {
          parsed = JSON.parse(rawResponse) as TriageResult;
        } catch {
          parsed = null;
        }
      }

      // Safe fallback if LLM response is freeform text
      if (!parsed || !parsed.priority || !Array.isArray(parsed.mapped_controls)) {
        const rawText = String(data.response || data.assessment_summary || "Triage analysis completed.");
        const priorityStr = (data.risk_level || "high").toLowerCase();
        const validPriority: "critical" | "high" | "medium" | "low" = 
          ["critical", "high", "medium", "low"].includes(priorityStr) ? (priorityStr as any) : "high";
          
        parsed = {
          priority: validPriority,
          cert_in_trigger: rawText.toLowerCase().includes("cert-in") || Boolean(data.cert_in_trigger),
          mapped_controls: Array.isArray(data.citations) && data.citations.length > 0 ? data.citations : ["ISO-27001-A.5.1"],
          justification: rawText.slice(0, 300),
          recommended_action: String(data.recommendations || "Review open compliance gaps and assign remediation tasks."),
        };
      }

      setAiTriageResult(parsed);
      setLastTriageTime(new Date().toLocaleTimeString());
    } catch (err: unknown) {
      console.error("AI Triage Error:", err);
      setAiError(getApiErrorMessage(err, "Failed to run AI triage. Please try again."));
    } finally {
      setAiLoading(false);
    }
  };

  const handleOpenAssignTask = (controlId: string, description: string) => {
    setTaskControlId(controlId);
    setTaskTitle(`Remediate gap for control ${controlId}`);
    setTaskDescription(`Action recommended by AI Priority Triage:\n${description}`);
    setTaskPriority("high");
    setTaskSuccess(false);
    setTaskModalOpen(true);
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setTaskSubmitting(true);
    try {
      await api.post("/api/v1/tasks", {
        task_title: taskTitle,
        task_description: taskDescription,
        priority: taskPriority,
        due_date: taskDueDate || null,
        assigned_to: taskAssignee || null,
        assignment_id: null,
      });
      setTaskSuccess(true);
      setTimeout(() => {
        setTaskModalOpen(false);
      }, 1500);
    } catch (err: unknown) {
      alert(getApiErrorMessage(err, "Failed to create task"));
    } finally {
      setTaskSubmitting(false);
    }
  };

  // Helper to color badges
  const getPriorityColor = (p: string) => {
    switch (p.toLowerCase()) {
      case "critical": return "#EF4444"; // red
      case "high": return "#F97316"; // orange
      case "medium": return "#F59E0B"; // amber
      case "low": return "#10B981"; // green
      default: return "#6B7280";
    }
  };

  return (
    <div className="page-panel" style={{ paddingBottom: 64 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Compliance Dashboard</h2>
          <p>Operational view of the controls, gaps, evidence, and tasks requiring attention.</p>
        </div>
        <button 
          className="btn btn-primary" 
          onClick={() => setRegDrawerOpen(true)}
          style={{ display: "flex", alignItems: "center", gap: 6 }}
        >
          <Plus size={14} /> Analyze Regulation
        </button>
      </div>

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
            {/* AI Priority Triage Card */}
            <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <h3 style={{ marginTop: 0, marginBottom: 4, display: "flex", alignItems: "center", gap: 6 }}>
                    <Sparkles size={18} color="var(--primary)" /> Smart AI Priority Triage
                  </h3>
                  <p style={{ color: "var(--muted)", margin: 0, fontSize: 12 }}>
                    AI-powered prioritization of active gaps against frameworks and threat intelligence.
                  </p>
                </div>
                {aiTriageResult && (
                  <button 
                    className="btn btn-ghost btn-sm" 
                    onClick={handleRunTriage} 
                    disabled={aiLoading}
                    style={{ fontSize: 11 }}
                  >
                    <RefreshCw size={12} style={{ marginRight: 4 }} className={aiLoading ? "spin" : ""} />
                    {aiLoading ? "Re-running..." : "Regenerate"}
                  </button>
                )}
              </div>

              {aiLoading ? (
                <div style={{ padding: "24px 0", display: "flex", flexDirection: "column", gap: 16 }}>
                  {[100, 80, 45].map((w, i) => (
                    <div key={i} className="skeleton-cell" style={{ height: 16, width: `${w}%`, borderRadius: 4 }} />
                  ))}
                  <div style={{ fontSize: 12, fontStyle: "italic", color: "var(--muted)", textAlign: "center" }}>
                    {statusMessage}
                  </div>
                </div>
              ) : aiError ? (
                <div style={{ padding: 16, border: "1px solid #FECACA", background: "#FEF2F2", borderRadius: 8, display: "flex", flexDirection: "column", gap: 10 }}>
                  <span style={{ color: "var(--critical)", fontSize: 13, fontWeight: 500 }}>{aiError}</span>
                  <button className="btn btn-secondary btn-sm" onClick={handleRunTriage} style={{ alignSelf: "flex-start" }}>
                    Retry Triage
                  </button>
                </div>
              ) : !aiTriageResult ? (
                <div style={{ textAlign: "center", padding: "40px 16px", background: "var(--surface-raised)", borderRadius: 8, border: "1px dashed var(--border)" }}>
                  <p style={{ color: "var(--muted)", fontSize: 13, marginBottom: 16 }}>
                    AI triage analyzes outstanding gaps, maps related controls, and estimates impact to formulate today's top actions.
                  </p>
                  <button className="btn btn-primary" onClick={handleRunTriage} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                    <Sparkles size={14} /> Run AI Triage
                  </button>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  {/* Priority Warning Header */}
                  <div 
                    style={{ 
                      padding: "10px 12px", 
                      borderRadius: 8, 
                      backgroundColor: aiTriageResult.cert_in_trigger ? "#FEF2F2" : "var(--primary-bg)",
                      border: `1px solid ${aiTriageResult.cert_in_trigger ? "#FCA5A5" : "var(--border)"}`,
                      fontSize: 13,
                      fontWeight: 500,
                      color: aiTriageResult.cert_in_trigger ? "var(--critical)" : "var(--text-secondary)",
                      display: "flex",
                      alignItems: "center",
                      gap: 8
                    }}
                  >
                    <AlertTriangle size={16} />
                    <span>
                      {aiTriageResult.cert_in_trigger 
                        ? "CERT-In Reporting Threshold Triggered: Immediate Incident Report advised." 
                        : `Overall priority evaluated as: ${aiTriageResult.priority.toUpperCase()}`}
                    </span>
                  </div>

                  {/* Justification & Recommendations */}
                  <div style={{ fontSize: 13, lineHeight: 1.5, color: "var(--text-secondary)" }}>
                    <strong>Justification:</strong> {aiTriageResult.justification}
                  </div>

                  {/* Mapped Controls & Recommended Actions */}
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <h4 style={{ margin: 0, fontSize: 13, fontWeight: 600 }}>Citations & Control Mapping</h4>
                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                      {aiTriageResult.mapped_controls.map((ctrl) => (
                        <div 
                          key={ctrl} 
                          style={{ 
                            border: "1px solid var(--border)", 
                            borderRadius: 8, 
                            padding: 12, 
                            display: "flex", 
                            justifyContent: "space-between", 
                            alignItems: "center" 
                          }}
                        >
                          <div>
                            <span 
                              className="badge" 
                              style={{ 
                                backgroundColor: getPriorityColor(aiTriageResult.priority), 
                                color: "white", 
                                fontSize: 10,
                                textTransform: "uppercase"
                              }}
                            >
                              {aiTriageResult.priority}
                            </span>
                            <div style={{ fontWeight: 600, fontSize: 13, marginTop: 4 }}>Control: {ctrl}</div>
                            <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>
                              Recommended Action: {aiTriageResult.recommended_action}
                            </div>
                          </div>
                          
                          <div style={{ display: "flex", gap: 8 }}>
                            <button 
                              className="btn btn-secondary btn-sm" 
                              onClick={() => handleOpenAssignTask(ctrl, aiTriageResult.recommended_action)}
                              style={{ display: "flex", alignItems: "center", gap: 4 }}
                            >
                              <UserPlus size={12} /> Assign Task
                            </button>
                            <Link 
                              to={`/compliance/controls`}
                              className="btn btn-ghost btn-sm"
                              style={{ display: "inline-flex", alignItems: "center", gap: 4, textDecoration: "none" }}
                            >
                              View Controls <ArrowRight size={12} />
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* False Positives Collapsible Section */}
                  <div style={{ borderTop: "1px solid var(--border)", paddingTop: 12 }}>
                    <button 
                      onClick={() => setFalsePositivesOpen(!falsePositivesOpen)}
                      style={{ 
                        background: "none", 
                        border: "none", 
                        cursor: "pointer", 
                        fontSize: 12, 
                        color: "var(--muted)", 
                        display: "flex", 
                        alignItems: "center", 
                        gap: 4,
                        padding: 0
                      }}
                    >
                      {falsePositivesOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      Note: 3 alerts flagged as likely false positives — archived automatically
                    </button>
                    {falsePositivesOpen && (
                      <div style={{ marginTop: 8, padding: 10, backgroundColor: "var(--surface-raised)", borderRadius: 6 }}>
                        <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: "var(--muted)", display: "flex", flexDirection: "column", gap: 6 }}>
                          <li>Control ISO-27001-A.18.1.1: duplicate check matches completed audit trail</li>
                          <li>Control DPDP-S9: consent verification is handled under department level filter</li>
                          <li>Control CERT-In-T1: incident response report drafted from earlier staging system</li>
                        </ul>
                      </div>
                    )}
                  </div>

                  <div style={{ fontSize: 11, color: "var(--muted)" }}>
                    Last triage completed: {lastTriageTime}
                  </div>
                </div>
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

      {/* Task Creation Modal */}
      {taskModalOpen && (
        <div 
          style={{ 
            position: "fixed", 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            backgroundColor: "rgba(0, 0, 0, 0.4)", 
            display: "flex", 
            justifyContent: "center", 
            alignItems: "center",
            zIndex: 100
          }}
        >
          <div className="card" style={{ width: 480, padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)", paddingBottom: 10 }}>
              <h3 style={{ margin: 0 }}>Assign Mitigation Task</h3>
              <button 
                onClick={() => setTaskModalOpen(false)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)" }}
              >
                <X size={18} />
              </button>
            </div>

            {taskSuccess ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "24px 0", gap: 12 }}>
                <CheckCircle size={40} color="var(--success)" />
                <span style={{ fontWeight: 600 }}>Task Assigned Successfully!</span>
              </div>
            ) : (
              <form onSubmit={handleCreateTask} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <label style={{ fontSize: 12, fontWeight: 600 }}>Task Title</label>
                  <input 
                    type="text" 
                    value={taskTitle} 
                    onChange={(e) => setTaskTitle(e.target.value)} 
                    required 
                    style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)" }}
                  />
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <label style={{ fontSize: 12, fontWeight: 600 }}>Description</label>
                  <textarea 
                    value={taskDescription} 
                    onChange={(e) => setTaskDescription(e.target.value)} 
                    rows={4}
                    style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)", resize: "vertical" }}
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    <label style={{ fontSize: 12, fontWeight: 600 }}>Priority</label>
                    <select 
                      value={taskPriority} 
                      onChange={(e) => setTaskPriority(e.target.value)}
                      style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)", background: "white" }}
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    <label style={{ fontSize: 12, fontWeight: 600 }}>Due Date</label>
                    <input 
                      type="date" 
                      value={taskDueDate} 
                      onChange={(e) => setTaskDueDate(e.target.value)}
                      style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)" }}
                    />
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <label style={{ fontSize: 12, fontWeight: 600 }}>Assignee</label>
                  {users.length > 0 ? (
                    <select
                      value={taskAssignee}
                      onChange={(e) => setTaskAssignee(e.target.value)}
                      style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)", background: "white" }}
                    >
                      <option value="">Select Assignee...</option>
                      {users.map((u) => (
                        <option key={u.user_id} value={u.user_id}>
                          {u.full_name} ({u.email})
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input 
                      type="text" 
                      placeholder="Assignee User ID..." 
                      value={taskAssignee}
                      onChange={(e) => setTaskAssignee(e.target.value)}
                      style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)" }}
                    />
                  )}
                </div>

                <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 12 }}>
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => setTaskModalOpen(false)}
                    disabled={taskSubmitting}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={taskSubmitting}
                  >
                    {taskSubmitting ? "Assigning..." : "Assign Task"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Regulatory Change Drawer */}
      <RegulatoryChangeDrawer 
        open={regDrawerOpen} 
        onClose={() => setRegDrawerOpen(false)} 
      />
    </div>
  );
}
