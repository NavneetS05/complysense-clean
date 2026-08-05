// Use: Lists control tasks assigned specifically to the department.

import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { DataTable, Column } from "../../components/shared/DataTable";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";

type TaskItem = {
  task_id: string;
  task_title: string;
  task_status: string;
  priority: string;
  due_date?: string;
  assignment_id?: string;
  [key: string]: unknown;
};

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [filters, setFilters] = useState({ search: "", status: "" });

  const toast = useToast();

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
    try {
      await api.post(`/api/v1/tasks/${taskId}/submit`);
      toast.success("Task submitted successfully.");
      await load();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to submit task."));
    }
  }

  // Get unique statuses
  const statuses = useMemo(() => {
    return Array.from(new Set(tasks.map((t) => t.task_status).filter(Boolean)));
  }, [tasks]);

  // Client-side filtering
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const title = (task.task_title || "").toLowerCase();
      const matchesSearch = !filters.search || title.includes(filters.search.toLowerCase());
      const matchesStatus = !filters.status || task.task_status === filters.status;
      return matchesSearch && matchesStatus;
    });
  }, [tasks, filters]);

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "critical": return "badge-critical";
      case "high": return "badge-high";
      case "medium": return "badge-medium";
      case "low": return "badge-low";
      default: return "badge-info";
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
      case "submitted":
        return "badge-compliant";
      case "in_progress":
        return "badge-in_progress";
      case "not_started":
        return "badge-not_started";
      default:
        return "badge-info";
    }
  };

  const columns: Column<TaskItem>[] = [
    {
      key: "task_title",
      label: "Task",
      sortable: true,
      render: (val) => <span style={{ fontWeight: 600 }}>{String(val || "Unnamed Task")}</span>
    },
    {
      key: "priority",
      label: "Priority",
      sortable: true,
      render: (val) => {
        const priority = String(val || "medium");
        return (
          <span className={`badge ${getPriorityBadgeClass(priority)}`}>
            {priority}
          </span>
        );
      }
    },
    {
      key: "task_status",
      label: "Status",
      sortable: true,
      render: (val) => {
        const status = String(val || "not_started");
        return (
          <span className={`badge ${getStatusBadgeClass(status)}`}>
            {status.replace("_", " ")}
          </span>
        );
      }
    },
    {
      key: "due_date",
      label: "Due Date",
      sortable: true,
      render: (val) => (val ? new Date(String(val)).toLocaleDateString() : "—")
    },
    {
      key: "actions",
      label: "Actions",
      render: (_, row) => (
        <div style={{ display: "flex", gap: 8 }}>
          <Link to={`/dept/tasks/${row.task_id}`} className="btn btn-secondary btn-sm">
            Open
          </Link>
          {row.task_status !== "completed" && row.task_status !== "submitted" ? (
            <button 
              onClick={() => void handleSubmit(row.task_id)} 
              className="btn btn-secondary btn-sm"
              style={{ borderColor: "var(--success)", color: "var(--success)" }}
            >
              Submit
            </button>
          ) : null}
        </div>
      )
    }
  ];

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Task List" 
        subtitle="Review assigned remediation work and submit completed tasks back to the compliance workflow." 
      />

      <section className="card" style={{ display: "flex", gap: 12, padding: 12 }}>
        <input 
          className="form-input" 
          placeholder="Search by task title..." 
          value={filters.search} 
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
        />
        <select 
          className="form-input" 
          value={filters.status} 
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
          style={{ minWidth: 160 }}
        >
          <option value="">All Statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>{status.replace("_", " ")}</option>
          ))}
        </select>
      </section>

      <DataTable 
        columns={columns} 
        data={filteredTasks} 
        loading={loading}
        emptyTitle="No tasks found"
        emptyDesc="No tasks match the active filter criteria."
        keyField="task_id"
        pageSize={10}
      />
    </div>
  );
}
