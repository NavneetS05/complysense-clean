// Use: Mitigation task board to track action items across departments.

import { useEffect, useState, useMemo } from "react";
import { api } from "../../lib/api";
import { DataTable, Column } from "../../components/shared/DataTable";
import { PageShell } from "../../components/shared/PageShell";

type TaskItem = {
  task_id: string;
  task_title: string;
  priority: string;
  task_status: string;
  due_date?: string;
  assigned_to?: string;
  [key: string]: unknown;
};

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [filters, setFilters] = useState({ search: "", priority: "", status: "" });

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
      case "completed": return "badge-compliant";
      case "in_progress": return "badge-in_progress";
      case "not_started": return "badge-not_started";
      default: return "badge-info";
    }
  };

  // Client-side filtering
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const title = (task.task_title || "").toLowerCase();
      const matchesSearch = !filters.search || title.includes(filters.search.toLowerCase());
      const matchesPriority = !filters.priority || task.priority.toLowerCase() === filters.priority.toLowerCase();
      const matchesStatus = !filters.status || task.task_status.toLowerCase() === filters.status.toLowerCase();
      return matchesSearch && matchesPriority && matchesStatus;
    });
  }, [tasks, filters]);

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
      key: "assigned_to",
      label: "Assigned To",
      sortable: true,
      render: (val) => <span className="text-xs text-secondary-color font-mono">{String(val || "Unassigned")}</span>
    }
  ];

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Mitigation Tasks" 
        subtitle="Remediation work assigned to the institution team." 
      />

      <section className="card" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12, padding: 12 }}>
        <input 
          className="form-input" 
          placeholder="Search by task title..." 
          value={filters.search} 
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
        />
        <select 
          className="form-input" 
          value={filters.priority} 
          onChange={(e) => setFilters((f) => ({ ...f, priority: e.target.value }))}
        >
          <option value="">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select 
          className="form-input" 
          value={filters.status} 
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
        >
          <option value="">All Statuses</option>
          <option value="not_started">Not Started</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
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
