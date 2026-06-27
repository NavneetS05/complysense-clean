// Use: Lists control tasks assigned specifically to the department.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";

type TaskItem = {
  task_id: string;
  task_title: string;
  task_status: string;
  priority: string;
  due_date?: string;
  assignment_id?: string;
};

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);

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

  async function handleSubmit(taskId: string) {
    await api.post(`/api/v1/tasks/${taskId}/submit`);
    await load();
  }

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>Task List</h2>
        <p>Review assigned remediation work and submit completed tasks back to the compliance workflow.</p>
      </div>
      {loading ? <p>Loading tasks…</p> : (
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", background: "#f8fafc" }}>
                <th style={{ padding: 10 }}>Task</th>
                <th style={{ padding: 10 }}>Priority</th>
                <th style={{ padding: 10 }}>Status</th>
                <th style={{ padding: 10 }}>Due</th>
                <th style={{ padding: 10 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.task_id} style={{ borderTop: "1px solid #e2e8f0" }}>
                  <td style={{ padding: 10 }}>{task.task_title}</td>
                  <td style={{ padding: 10 }}>{task.priority}</td>
                  <td style={{ padding: 10 }}>{task.task_status}</td>
                  <td style={{ padding: 10 }}>{task.due_date ? new Date(task.due_date).toLocaleDateString() : "—"}</td>
                  <td style={{ padding: 10, display: "flex", gap: 8 }}>
                    <Link to={`/dept/tasks/${task.task_id}`}>Open</Link>
                    {task.task_status !== "completed" ? <button onClick={() => void handleSubmit(task.task_id)} style={{ padding: "6px 8px", borderRadius: 8, border: "1px solid #16a34a", color: "#166534", background: "white" }}>Submit</button> : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
