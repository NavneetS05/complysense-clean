// Use: List of active and historical compliance assessments.

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import { DataTable, Column } from "../../components/shared/DataTable";
import { PageShell } from "../../components/shared/PageShell";
import { getFrameworkColor } from "../../lib/frameworkColors";
import ErrorState from "../../components/shared/ErrorState";

type AssessmentItem = {
  assessment_id: string;
  assessment_name: string;
  framework_name: string;
  assessment_status: string;
  started_at?: string;
  [key: string]: unknown;
};

export default function Assessments() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/assessments");
    return Array.isArray(res.data) ? res.data : res.data?.assessments ?? [];
  }, []);

  const assessments = useMemo<AssessmentItem[]>(() => data ?? [], [data]);

  // Filter states
  const [filters, setFilters] = useState({ search: "", framework: "", status: "" });

  // Get unique frameworks and status for filters
  const frameworks = useMemo(() => {
    return Array.from(new Set(assessments.map((a) => a.framework_name).filter(Boolean)));
  }, [assessments]);

  const statuses = useMemo(() => {
    return Array.from(new Set(assessments.map((a) => a.assessment_status).filter(Boolean)));
  }, [assessments]);

  // Client-side filtering
  const filteredAssessments = useMemo(() => {
    return assessments.filter((item) => {
      const name = (item.assessment_name || "").toLowerCase();
      const matchesSearch = !filters.search || name.includes(filters.search.toLowerCase());
      const matchesFramework = !filters.framework || item.framework_name === filters.framework;
      const matchesStatus = !filters.status || item.assessment_status === filters.status;
      return matchesSearch && matchesFramework && matchesStatus;
    });
  }, [assessments, filters]);

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "badge-compliant";
      case "in_progress":
        return "badge-in_progress";
      case "not_started":
        return "badge-not_started";
      default:
        return "badge-info";
    }
  };

  const columns: Column<AssessmentItem>[] = [
    {
      key: "assessment_name",
      label: "Assessment",
      sortable: true,
      render: (val) => <span style={{ fontWeight: 600 }}>{String(val || "Unnamed Assessment")}</span>
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
      key: "assessment_status",
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
      key: "actions",
      label: "Action",
      render: (_, row) => (
        <Link to={`/compliance/assessments/${row.assessment_id}`} className="btn btn-secondary btn-sm">
          Open
        </Link>
      )
    }
  ];

  if (error) {
    return (
      <div className="page-panel">
        <PageShell title="Assessments" subtitle="Operational assessment runs and their current status." />
        <div style={{ marginTop: 16 }}>
          <ErrorState message={error.message} onRetry={() => void refetch()} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Assessments" 
        subtitle="Operational assessment runs and their current status." 
      />

      <section className="card" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12, padding: 12 }}>
        <input 
          className="form-input" 
          placeholder="Search by assessment name..." 
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
        data={filteredAssessments} 
        loading={loading}
        emptyTitle="No assessments found"
        emptyDesc="No assessments match the active filter criteria."
        keyField="assessment_id"
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
