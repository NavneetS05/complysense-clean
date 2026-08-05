// Use: Lists technical security controls assigned to the IT security officer.

import { useEffect, useState, useMemo } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import { DataTable, Column } from "../../components/shared/DataTable";
import { getFrameworkColor } from "../../lib/frameworkColors";
import ErrorState from "../../components/shared/ErrorState";

interface ControlItem {
  assignment_id: string;
  control_id: string;
  framework_name: string;
  status: string;
  due_date?: string | null;
  assigned_name?: string | null;
  [key: string]: unknown;
}

export default function Controls() {
  const [controls, setControls] = useState<ControlItem[]>([]);

  // Filter states
  const [filters, setFilters] = useState({ search: "", framework: "", status: "" });

  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/controls");
    const payload = res.data as ControlItem[] | { controls?: ControlItem[] };
    return Array.isArray(payload) ? payload : payload.controls ?? [];
  }, []);

  useEffect(() => {
    if (!data) return;
    setControls(data as ControlItem[]);
  }, [data]);

  // Unique frameworks and statuses for filters
  const frameworks = useMemo(() => {
    return Array.from(new Set(controls.map((c) => c.framework_name).filter(Boolean)));
  }, [controls]);

  const statuses = useMemo(() => {
    return Array.from(new Set(controls.map((c) => c.status).filter(Boolean)));
  }, [controls]);

  // Client-side filtering
  const filteredControls = useMemo(() => {
    return controls.filter((ctrl) => {
      const cid = (ctrl.control_id || "").toLowerCase();
      const name = (ctrl.assigned_name || "").toLowerCase();
      const matchesSearch =
        !filters.search ||
        cid.includes(filters.search.toLowerCase()) ||
        name.includes(filters.search.toLowerCase());
      const matchesFramework = !filters.framework || ctrl.framework_name === filters.framework;
      const matchesStatus = !filters.status || ctrl.status === filters.status;
      return matchesSearch && matchesFramework && matchesStatus;
    });
  }, [controls, filters]);

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case "compliant":
      case "implemented":
        return "badge-compliant";
      case "non_compliant":
      case "not_implemented":
        return "badge-non_compliant";
      case "in_progress":
        return "badge-in_progress";
      default:
        return "badge-info";
    }
  };

  const columns: Column<ControlItem>[] = [
    {
      key: "control_id",
      label: "Control",
      sortable: true,
      render: (val) => <span className="font-mono" style={{ fontWeight: 600 }}>{String(val || "—")}</span>
    },
    {
      key: "framework_name",
      label: "Framework",
      sortable: true,
      render: (val) => {
        const name = String(val || "General");
        const colors = getFrameworkColor(name);
        return (
          <span 
            className="badge" 
            style={{ 
              backgroundColor: colors.bg, 
              color: colors.text, 
              border: `1px solid ${colors.border}` 
            }}
          >
            {name}
          </span>
        );
      }
    },
    {
      key: "status",
      label: "Status",
      sortable: true,
      render: (val) => {
        const status = String(val || "unknown");
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
      key: "assigned_name",
      label: "Owner",
      sortable: true,
      render: (val) => String(val || "Unassigned")
    }
  ];

  if (error) {
    return (
      <div className="page-panel">
        <PageShell title="IT Control Assignments" subtitle="Technical control assignments and due dates." />
        <div style={{ marginTop: 16 }}>
          <ErrorState message={error.message} onRetry={() => void refetch()} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="IT Control Assignments" 
        subtitle="Technical control assignments and due dates." 
      />

      <section className="card" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12, padding: 12 }}>
        <input 
          className="form-input" 
          placeholder="Search by Control ID or Owner..." 
          value={filters.search} 
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
        />
        <select 
          className="form-input" 
          value={filters.framework} 
          onChange={(e) => setFilters((f) => ({ ...f, framework: e.target.value }))}
        >
          <option value="">All Frameworks</option>
          {frameworks.map((fw) => (
            <option key={fw} value={fw}>{fw}</option>
          ))}
        </select>
        <select 
          className="form-input" 
          value={filters.status} 
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
        >
          <option value="">All Statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>{status.replace("_", " ")}</option>
          ))}
        </select>
      </section>

      <DataTable 
        columns={columns} 
        data={filteredControls} 
        loading={loading}
        emptyTitle="No controls found"
        emptyDesc="No IT control assignments match the active filter criteria."
        keyField="assignment_id"
        pageSize={10}
      />
    </div>
  );
}
