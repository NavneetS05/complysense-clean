// Use: Step-by-step help wizard for completing compliance tasks with plain-English instructions.

import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { Info, CheckCircle2, ArrowLeft, Send } from "lucide-react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import Loading from "../../components/shared/Loading";

type TaskItem = {
  task_id: string;
  task_title: string;
  task_description?: string;
  task_status?: string;
  due_date?: string;
  priority?: string;
};

export default function TaskWizard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState<TaskItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const { data } = await api.get(`/api/v1/tasks/${id}`);
        setTask(data);
      } catch {
        setTask(null);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [id]);

  async function handleSubmit() {
    setSubmitting(true);
    try {
      await api.post(`/api/v1/tasks/${id}/submit`);
      navigate("/dept/tasks");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <Loading />;
  }

  if (!task) {
    return (
      <PageShell title="Task Not Found" subtitle="The requested mitigation task could not be found.">
        <Link to="/dept/tasks" className="btn btn-secondary">
          <ArrowLeft size={14} /> Back to My Tasks
        </Link>
      </PageShell>
    );
  }

  return (
    <PageShell
      title={task.task_title}
      subtitle="Complete step-by-step remediation task instructions and submit for compliance review."
      actions={
        <Link to="/dept/tasks" className="btn btn-secondary">
          <ArrowLeft size={14} /> Back to Tasks
        </Link>
      }
    >
      {/* 3-step guidance banner */}
      <div className="guidance-banner">
        <div className="guidance-header">
          <Info size={18} /> Guided 3-Step Task Completion Process
        </div>
        <div className="guidance-steps">
          <div className="guidance-step">
            <div className="guidance-step-num">1</div>
            <div>
              <strong style={{ display: "block", color: "var(--text-primary)" }}>Review Guidelines</strong>
              Read the task details and required compliance evidence requirements below.
            </div>
          </div>
          <div className="guidance-step">
            <div className="guidance-step-num">2</div>
            <div>
              <strong style={{ display: "block", color: "var(--text-primary)" }}>Attach Evidence</strong>
              Ensure supporting documentation is uploaded in the Evidence Vault.
            </div>
          </div>
          <div className="guidance-step">
            <div className="guidance-step-num">3</div>
            <div>
              <strong style={{ display: "block", color: "var(--text-primary)" }}>Submit Task</strong>
              Click Submit to send the completed task to the Compliance Officer.
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 4px" }}>Task Specification</h3>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0 }}>
            {task.task_description || "Use this guided view to confirm evidence and task status before submission."}
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, background: "var(--surface-secondary)", padding: 14, borderRadius: "var(--radius-md)" }}>
          <div>
            <span style={{ fontSize: 11, color: "var(--text-secondary)", textTransform: "uppercase" }}>Status</span>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", marginTop: 2 }}>
              <span className="badge badge-in_progress">{task.task_status ?? "in_progress"}</span>
            </div>
          </div>
          <div>
            <span style={{ fontSize: 11, color: "var(--text-secondary)", textTransform: "uppercase" }}>Priority</span>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", marginTop: 2 }}>
              <span className="badge badge-warning">{task.priority ?? "medium"}</span>
            </div>
          </div>
          <div>
            <span style={{ fontSize: 11, color: "var(--text-secondary)", textTransform: "uppercase" }}>Due Date</span>
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)", marginTop: 2 }}>
              {task.due_date ? new Date(task.due_date).toLocaleDateString() : "—"}
            </div>
          </div>
        </div>

        <div className="guidance-banner" style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
          <strong style={{ color: "var(--text-primary)", fontSize: 13 }}>General Submission Checklist</strong>
          <ul style={{ margin: "8px 0 0 20px", fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>
            <li>Confirm control evidence is attached and up to date in the Evidence Vault.</li>
            <li>Include remediation rationale notes for the reviewing Compliance Officer.</li>
            <li>Submit the task only when all required documentation is complete.</li>
          </ul>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
            <Send size={14} /> {submitting ? "Submitting Task..." : "Submit Task for Verification"}
          </button>
        </div>
      </div>
    </PageShell>
  );
}
