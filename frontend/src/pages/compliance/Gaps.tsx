// Use: Matrix view of identified compliance gaps sorted by framework.

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import { DataTable, Column } from "../../components/shared/DataTable";
import { PageShell } from "../../components/shared/PageShell";
import { getFrameworkColor } from "../../lib/frameworkColors";
import ErrorState from "../../components/shared/ErrorState";

type GapRow = {
  gap_id: string;
  control_id?: string;
  framework_name: string;
  severity: string;
  title: string;
  remediation_status: string;
  created_at?: string;
  [key: string]: unknown;
};

export default function Gaps() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/gaps");
    return Array.isArray(res.data) ? res.data : res.data?.gaps ?? [];
  }, []);

  const gaps = useMemo<GapRow[]>(() => data ?? [], [data]);

  // Filter states
  const [filters, setFilters] = useState({ search: "", severity: "", framework: "", status: "" });

  // Get unique frameworks and status for filters
  const frameworks = useMemo(() => {
    return Array.from(new Set(gaps.map((g) => g.framework_name).filter(Boolean)));
  }, [gaps]);

  const statuses = useMemo(() => {
    return Array.from(new Set(gaps.map((g) => g.remediation_status).filter(Boolean)));
  }, [gaps]);

  // Client-side filtering
  const filteredGaps = useMemo(() => {
    return gaps.filter((gap) => {
      const title = (gap.title || "").toLowerCase();
      const control = (gap.control_id || "").toLowerCase();
      const matchesSearch =
        !filters.search ||
        title.includes(filters.search.toLowerCase()) ||
        control.includes(filters.search.toLowerCase());
      const matchesSeverity = !filters.severity || gap.severity.toLowerCase() === filters.severity.toLowerCase();
      const matchesFramework = !filters.framework || gap.framework_name === filters.framework;
      const matchesStatus = !filters.status || gap.remediation_status === filters.status;
      return matchesSearch && matchesSeverity && matchesFramework && matchesStatus;
    });
  }, [gaps, filters]);

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical": return "badge-critical";
      case "high": return "badge-high";
      case "medium": return "badge-medium";
      case "low": return "badge-low";
      default: return "badge-info";
    }
  };

  const columns: Column<GapRow>[] = [
    {
      key: "severity",
      label: "Severity",
      sortable: true,
      render: (val) => {
        const severity = String(val || "medium");
        return (
          <span className={`badge ${getSeverityBadgeClass(severity)}`}>
            {severity}
          </span>
        );
      }
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
      key: "control_id",
      label: "Control",
      sortable: true,
      render: (val) => <span className="font-mono">{String(val || "—")}</span>
    },
    {
      key: "title",
      label: "Gap",
      sortable: true,
      render: (val) => <span style={{ fontWeight: 600 }}>{String(val || "Unnamed Gap")}</span>
    },
    {
      key: "remediation_status",
      label: "Status",
      sortable: true,
      render: (val) => {
        const status = String(val || "open");
        const statusClass = status === "closed" || status === "resolved" ? "badge-resolved" : "badge-open";
        return (
          <span className={`badge ${statusClass}`}>
            {status}
          </span>
        );
      }
    },
    {
      key: "actions",
      label: "Action",
      render: () => (
        <Link to="/compliance/tasks" className="btn btn-secondary btn-sm">
          Create task
        </Link>
      )
    }
  ];

  if (error) {
    return (
      <div className="page-panel">
        <PageShell title="Compliance Gaps" subtitle="Open and in-progress remediation items across the institution." />
        <div style={{ marginTop: 16 }}>
          <ErrorState message={error.message} onRetry={() => void refetch()} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Compliance Gaps" 
        subtitle="Open and in-progress remediation items across the institution." 
      />

      <div className="filter-toolbar">
        <div className="filter-search-wrapper">
          <input 
            className="filter-search-input" 
            placeholder="Search by gap title or control ID..." 
            value={filters.search} 
            onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
          />
        </div>
        <select 
          className="filter-select" 
          value={filters.severity} 
          onChange={(e) => setFilters((f) => ({ ...f, severity: e.target.value }))}
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select 
          className="filter-select" 
          value={filters.framework} 
          onChange={(e) => setFilters((f) => ({ ...f, framework: e.target.value }))}
        >
          <option value="">All Frameworks</option>
          {frameworks.map((fw) => (
            <option key={fw} value={fw}>{fw}</option>
          ))}
        </select>
        <select 
          className="filter-select" 
          value={filters.status} 
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
        >
          <option value="">All Statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </div>

      <DataTable 
        columns={columns} 
        data={filteredGaps} 
        loading={loading}
        emptyTitle="No compliance gaps found"
        emptyDesc="No compliance gaps match the active filter criteria."
        keyField="gap_id"
        pageSize={10}
        emptyAction={
          <button className="btn btn-primary btn-sm" onClick={() => void refetch()}>
            Refresh
          </button>
        }
      />
    </div>
  );
}
