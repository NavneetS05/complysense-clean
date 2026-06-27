// Use: Step-by-step help wizard for completing compliance tasks with plain-English instructions.

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../../lib/api";

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
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      const { data } = await api.get(`/api/v1/tasks/${id}`);
      setTask(data);
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

  if (!task) {
    return <div className="page-panel">Loading task…</div>;
  }

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>{task.task_title}</h2>
        <p>{task.task_description || "Use this guided view to confirm the evidence and task status before submission."}</p>
      </div>
      <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, display: "grid", gap: 12 }}>
        <div><strong>Status:</strong> {task.task_status}</div>
        <div><strong>Priority:</strong> {task.priority || "medium"}</div>
        <div><strong>Due:</strong> {task.due_date ? new Date(task.due_date).toLocaleDateString() : "—"}</div>
        <div style={{ border: "1px dashed #cbd5e1", borderRadius: 10, padding: 12, background: "#f8fafc" }}>
          <strong>Suggested completion checklist</strong>
          <ul style={{ margin: "8px 0 0 20px" }}>
            <li>Confirm the control evidence is attached and current.</li>
            <li>Capture the remediation note or rationale for reviewers.</li>
            <li>Submit the task only when all required evidence is available.</li>
          </ul>
        </div>
        <button onClick={handleSubmit} disabled={submitting} style={{ padding: "10px 12px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", width: 200 }}>
          {submitting ? "Submitting…" : "Submit Task"}
        </button>
      </div>
    </div>
  );
}
