// Use: Mitigation task board to track action items across departments.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

type TaskItem = {
  task_id: string;
  task_title: string;
  priority: string;
  task_status: string;
  due_date?: string;
  assigned_to?: string;
};

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/tasks");
        setTasks(Array.isArray(data) ? data : []);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  return (
    <div className="page-panel">
      <h2>Mitigation Tasks</h2>
      <p>Remediation work assigned to the institution team.</p>
      {loading ? <p>Loading tasks…</p> : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>Task</th>
                <th style={{ padding: "8px 6px" }}>Priority</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Due</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.task_id}>
                  <td style={{ padding: "8px 6px" }}>{task.task_title}</td>
                  <td style={{ padding: "8px 6px" }}>{task.priority}</td>
                  <td style={{ padding: "8px 6px" }}>{task.task_status}</td>
                  <td style={{ padding: "8px 6px" }}>{task.due_date ? new Date(task.due_date).toLocaleDateString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
