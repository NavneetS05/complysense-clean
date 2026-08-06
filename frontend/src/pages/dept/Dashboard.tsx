// Use: Overview of department tasks, evidence status, and local risk level.

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";

type TaskItem = {
  task_id: string;
  task_title: string;
  task_status: string;
  priority: string;
  due_date?: string;
};

type EvidenceItem = {
  evidence_id: string;
  file_name?: string;
  approval_status?: string;
  uploaded_at?: string;
};

export default function Dashboard() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [{ data: taskData }, { data: evidenceData }] = await Promise.all([
          api.get("/api/v1/tasks"),
          api.get("/api/v1/evidence"),
        ]);
        setTasks(Array.isArray(taskData) ? taskData : []);
        setEvidence(Array.isArray(evidenceData) ? evidenceData : []);
      } catch {
        // errors handled by loading state clearing
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const summary = useMemo(() => ({
    pending: tasks.filter((task) => task.task_status !== "completed").length,
    highPriority: tasks.filter((task) => task.priority === "high").length,
    pendingEvidence: evidence.filter((item) => item.approval_status !== "approved").length,
  }), [tasks, evidence]);

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>My Department Dashboard</h2>
        <p>Stay on top of remediation work, evidence readiness, and upcoming review deadlines.</p>
      </div>
      {loading ? <p>Loading dashboard…</p> : (
        <>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, minWidth: 180 }}>
              <div style={{ color: "#64748b", fontSize: 13 }}>Open Tasks</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{summary.pending}</div>
            </div>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, minWidth: 180 }}>
              <div style={{ color: "#64748b", fontSize: 13 }}>High Priority</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{summary.highPriority}</div>
            </div>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, minWidth: 180 }}>
              <div style={{ color: "#64748b", fontSize: 13 }}>Evidence Pending</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{summary.pendingEvidence}</div>
            </div>
          </div>

          <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>Upcoming Tasks</h3>
              {tasks.length === 0 ? <p>No tasks assigned.</p> : tasks.slice(0, 4).map((task) => (
                <div key={task.task_id} style={{ borderTop: "1px solid #f1f5f9", paddingTop: 8, marginTop: 8 }}>
                  <div style={{ fontWeight: 700 }}>{task.task_title}</div>
                  <div style={{ color: "#64748b", fontSize: 13 }}>{task.priority} • {task.task_status}</div>
                  <div style={{ marginTop: 6 }}><Link to={`/dept/tasks/${task.task_id}`}>Open task</Link></div>
                </div>
              ))}
            </div>
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>Latest Evidence</h3>
              {evidence.length === 0 ? <p>No evidence uploaded yet.</p> : evidence.slice(0, 4).map((item) => (
                <div key={item.evidence_id} style={{ borderTop: "1px solid #f1f5f9", paddingTop: 8, marginTop: 8 }}>
                  <div style={{ fontWeight: 700 }}>{item.file_name || "Evidence file"}</div>
                  <div style={{ color: "#64748b", fontSize: 13 }}>{item.approval_status || "pending"}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
