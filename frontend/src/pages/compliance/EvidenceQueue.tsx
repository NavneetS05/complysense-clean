// Use: Approval queue for verification of uploaded evidence documents.

import { useMemo, useState } from "react";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import { DataTable, Column } from "../../components/shared/DataTable";
import { PageShell } from "../../components/shared/PageShell";
import ErrorState from "../../components/shared/ErrorState";

type EvidenceItem = {
  evidence_id: string;
  file_name: string;
  control_id?: string;
  approval_status: string;
  uploaded_at?: string;
  file_size_kb?: number;
  [key: string]: unknown;
};

export default function EvidenceQueue() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/evidence");
    return Array.isArray(res.data) ? res.data : res.data?.evidence ?? [];
  }, []);

  const evidence = useMemo<EvidenceItem[]>(() => data ?? [], [data]);

  // Filter states
  const [filters, setFilters] = useState({ search: "", status: "" });

  // Get unique statuses
  const statuses = useMemo(() => {
    return Array.from(new Set(evidence.map((e) => e.approval_status).filter(Boolean)));
  }, [evidence]);

  // Client-side filtering
  const filteredEvidence = useMemo(() => {
    return evidence.filter((item) => {
      const name = (item.file_name || "").toLowerCase();
      const matchesSearch = !filters.search || name.includes(filters.search.toLowerCase());
      const matchesStatus = !filters.status || item.approval_status === filters.status;
      return matchesSearch && matchesStatus;
    });
  }, [evidence, filters]);

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
        return "badge-compliant";
      case "rejected":
        return "badge-non_compliant";
      case "pending":
      default:
        return "badge-pending";
    }
  };

  const columns: Column<EvidenceItem>[] = [
    {
      key: "file_name",
      label: "File",
      sortable: true,
      render: (val) => <span style={{ fontWeight: 600 }}>{String(val || "Evidence document")}</span>
    },
    {
      key: "control_id",
      label: "Control",
      sortable: true,
      render: (val) => <span className="font-mono">{String(val || "—")}</span>
    },
    {
      key: "approval_status",
      label: "Status",
      sortable: true,
      render: (val) => {
        const status = String(val || "pending");
        return (
          <span className={`badge ${getStatusBadgeClass(status)}`}>
            {status}
          </span>
        );
      }
    },
    {
      key: "file_size_kb",
      label: "Size",
      sortable: true,
      render: (val) => (val ? `${val} KB` : "—")
    }
  ];

  if (error) {
    return (
      <div className="page-panel">
        <PageShell title="Evidence Queue" subtitle="Pending evidence submissions requiring review." />
        <div style={{ marginTop: 16 }}>
          <ErrorState message={error.message} onRetry={() => void refetch()} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Evidence Queue" 
        subtitle="Pending evidence submissions requiring review." 
      />

      <section className="card" style={{ display: "flex", gap: 12, padding: 12 }}>
        <input 
          className="form-input" 
          placeholder="Search by file name..." 
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
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </section>

      <DataTable 
        columns={columns} 
        data={filteredEvidence} 
        loading={loading}
        emptyTitle="No evidence found"
        emptyDesc="No evidence submissions match the active filter criteria."
        keyField="evidence_id"
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
