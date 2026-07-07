// Use: Lists control tasks assigned specifically to the department in card view.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { Calendar, AlertCircle, ArrowRight, CheckCircle2, ShieldAlert } from "lucide-react";

type TaskItem = {
  task_id: string;
  task_title: string;
  task_description?: string;
  task_status: string;
  priority: string;
  due_date?: string;
  assignment_id?: string;
};

const PRIORITY_COLORS: Record<string, { bg: string; text: string }> = {
  critical: { bg: "#FEF2F2", text: "#EF4444" },
  high:     { bg: "#FFF7ED", text: "#F97316" },
  medium:   { bg: "#FFFBEB", text: "#F59E0B" },
  low:      { bg: "#ECFDF5", text: "#10B981" },
};

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"all" | "pending" | "completed">("pending");

  async function load() {
    try {
      const { data } = await api.get("/api/v1/tasks");
      setTasks(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const filteredTasks = tasks.filter((t) => {
    if (activeTab === "pending") return t.task_status !== "completed";
    if (activeTab === "completed") return t.task_status === "completed";
    return true;
  });

  const getDueDateLabel = (dateStr?: string) => {
    if (!dateStr) return { label: "No due date", color: "var(--muted)" };
    const diff = new Date(dateStr).getTime() - Date.now();
    const days = Math.ceil(diff / (24 * 3600 * 1000));
    if (days < 0) return { label: `Overdue by ${Math.abs(days)}d`, color: "var(--critical)" };
    if (days === 0) return { label: "Due today", color: "var(--warning)" };
    if (days < 2) return { label: "Due tomorrow", color: "var(--warning)" };
    if (days <= 5) return { label: `Due in ${days} days`, color: "var(--warning)" };
    return { label: `Due in ${days} days`, color: "var(--success)" };
  };

  return (
    <PageShell
      title="My Tasks"
      subtitle="Track and complete control requirements assigned to your department. Use the guides to upload evidence."
    >
      <div className="page-panel" style={{ paddingBottom: 48 }}>
        {/* Tabs */}
        <div style={{ display: "flex", gap: 8, margin: "20px 0 16px 0", borderBottom: "1px solid var(--border)", paddingBottom: 8 }}>
        {[
          { id: "pending", label: `Pending Tasks (${tasks.filter((t) => t.task_status !== "completed").length})` },
          { id: "completed", label: `Completed (${tasks.filter((t) => t.task_status === "completed").length})` },
          { id: "all", label: "All Tasks" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              border: "none",
              background: activeTab === tab.id ? "var(--primary-bg)" : "transparent",
              color: activeTab === tab.id ? "var(--primary)" : "var(--muted)",
              fontWeight: 600,
              fontSize: 13,
              cursor: "pointer",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ padding: 32, textAlign: "center", color: "var(--muted)" }}>Loading your tasks…</div>
      ) : filteredTasks.length === 0 ? (
        <div className="card" style={{ padding: 32, textAlign: "center", color: "var(--muted)" }}>
          <CheckCircle2 size={32} color="var(--success)" style={{ marginBottom: 8 }} />
          <div>{activeTab === "pending" ? "All caught up! No pending tasks." : "No tasks found."}</div>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          {filteredTasks.map((t) => {
            const prio = PRIORITY_COLORS[t.priority.toLowerCase()] || PRIORITY_COLORS.medium;
            const due = getDueDateLabel(t.due_date);
            return (
              <div className="card" key={t.task_id} style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", padding: 18 }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                    <span className="badge" style={{ backgroundColor: prio.bg, color: prio.text, fontWeight: 700, fontSize: 11 }}>
                      {t.priority.toUpperCase()}
                    </span>
                    <span style={{ fontSize: 12, color: due.color, display: "flex", alignItems: "center", gap: 4, fontWeight: 500 }}>
                      <Calendar size={13} />
                      {due.label}
                    </span>
                  </div>
                  <h4 style={{ margin: "0 0 6px 0", fontSize: 15, fontWeight: 600 }}>{t.task_title}</h4>
                  <p style={{ margin: 0, fontSize: 13, color: "var(--muted)", lineHeight: 1.4 }}>
                    {t.task_description || "Guided response task to satisfy organizational controls."}
                  </p>
                </div>

                <div style={{ borderTop: "1px solid var(--border)", marginTop: 16, paddingTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 12, color: "var(--muted)", textTransform: "capitalize" }}>
                    Status: <strong>{t.task_status.replace("_", " ")}</strong>
                  </span>
                  <Link
                    to={`/dept/tasks/${t.task_id}`}
                    className="btn btn-ghost btn-sm"
                    style={{ textDecoration: "none", color: "var(--primary)", display: "flex", alignItems: "center", gap: 4, padding: "4px 8px" }}
                  >
                    View & Complete <ArrowRight size={13} />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  </PageShell>
);
}
