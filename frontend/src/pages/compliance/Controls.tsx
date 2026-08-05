// Use: Kanban board and list view for managing institution control assignments.

import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { Search, X, Filter, Kanban as KanbanIcon, ArrowRight } from "lucide-react";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import { PageShell } from "../../components/shared/PageShell";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type ControlAssignment = {
  assignment_id: string;
  control_id: string;
  control_title?: string;
  framework_name: string;
  status: string;
  due_date?: string;
  assigned_to?: string;
  assigned_name?: string;
  department_name?: string;
};

const COLUMN_META = [
  { key: "not_started", title: "Not Started", color: "#64748B", bg: "#F8FAFC" },
  { key: "in_progress", title: "In Progress", color: "#2563EB", bg: "#EFF6FF" },
  { key: "submitted", title: "Submitted", color: "#7C3AED", bg: "#F5F3FF" },
  { key: "compliant", title: "Compliant", color: "#059669", bg: "#ECFDF5" },
  { key: "non_compliant", title: "Non-Compliant", color: "#DC2626", bg: "#FEF2F2" },
];

export default function Controls() {
  const [search, setSearch] = useState("");
  const [frameworkFilter, setFrameworkFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/controls");
    return Array.isArray(res.data) ? res.data : res.data?.controls ?? [];
  }, []);

  const controls = useMemo<ControlAssignment[]>(() => data ?? [], [data]);

  const frameworks = useMemo(() => {
    const set = new Set<string>();
    controls.forEach((c) => { if (c.framework_name) set.add(c.framework_name); });
    return Array.from(set);
  }, [controls]);

  const filteredControls = useMemo(() => {
    return controls.filter((item) => {
      const matchSearch =
        !search.trim() ||
        item.control_id.toLowerCase().includes(search.toLowerCase()) ||
        (item.control_title && item.control_title.toLowerCase().includes(search.toLowerCase())) ||
        (item.department_name && item.department_name.toLowerCase().includes(search.toLowerCase()));

      const matchFramework = frameworkFilter === "All" || item.framework_name === frameworkFilter;
      const matchStatus = statusFilter === "All" || item.status === statusFilter;

      return matchSearch && matchFramework && matchStatus;
    });
  }, [controls, search, frameworkFilter, statusFilter]);

  const grouped = useMemo(() => {
    return COLUMN_META.reduce((acc, column) => {
      acc[column.key] = filteredControls.filter((item) => item.status === column.key);
      return acc;
    }, {} as Record<string, ControlAssignment[]>);
  }, [filteredControls]);

  const hasFilters = search.trim() !== "" || frameworkFilter !== "All" || statusFilter !== "All";

  function clearFilters() {
    setSearch("");
    setFrameworkFilter("All");
    setStatusFilter("All");
  }

  return (
    <PageShell
      title="Control Assignments"
      subtitle="Track institutional compliance controls across frameworks, status columns, and responsible departments."
    >
      {/* Standard Filter Toolbar */}
      <div className="filter-toolbar">
        <div className="filter-search-wrapper">
          <Search size={16} className="filter-search-icon" />
          <input
            type="text"
            className="filter-search-input"
            placeholder="Search by Control ID, title, or department..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="filter-clear-icon" onClick={() => setSearch("")}>
              <X size={14} />
            </button>
          )}
        </div>

        <select
          className="filter-select"
          value={frameworkFilter}
          onChange={(e) => setFrameworkFilter(e.target.value)}
        >
          <option value="All">All Frameworks ({frameworks.length})</option>
          {frameworks.map((fw) => (
            <option key={fw} value={fw}>{fw}</option>
          ))}
        </select>

        <select
          className="filter-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="All">All Statuses</option>
          {COLUMN_META.map((col) => (
            <option key={col.key} value={col.key}>{col.title}</option>
          ))}
        </select>

        {hasFilters && (
          <button className="btn btn-ghost btn-sm" onClick={clearFilters} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <Filter size={13} /> Clear Filters
          </button>
        )}
      </div>

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : filteredControls.length === 0 ? (
        <EmptyState
          title="No control assignments"
          description={hasFilters ? "No controls match your filter search." : "No control assignments found."}
          actionLabel={hasFilters ? "Clear Filters" : "Refresh"}
          onAction={hasFilters ? clearFilters : () => void refetch()}
        />
      ) : (
        <div className="table-container">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(240px, 1fr))", gap: 14, minWidth: 1200 }}>
            {COLUMN_META.map((column) => {
              const colItems = grouped[column.key] ?? [];
              return (
                <div
                  key={column.key}
                  className="card"
                  style={{
                    padding: 14,
                    minHeight: 400,
                    background: "var(--surface)",
                    borderTop: `3px solid ${column.color}`,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                    <span style={{ fontWeight: 700, fontSize: 13, color: column.color }}>{column.title}</span>
                    <span className="badge" style={{ background: column.bg, color: column.color, fontWeight: 700 }}>
                      {colItems.length}
                    </span>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {colItems.map((item) => (
                      <div
                        key={item.assignment_id}
                        style={{
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius-md)",
                          padding: 12,
                          background: "var(--surface)",
                          boxShadow: "var(--shadow-sm)",
                          transition: "all var(--transition-fast)",
                        }}
                      >
                        <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)" }}>
                          {item.framework_name}
                        </div>
                        <div style={{ fontWeight: 700, fontSize: 14, color: "var(--text-primary)", marginTop: 2 }}>
                          {item.control_id}
                        </div>
                        {item.control_title && (
                          <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                            {item.control_title}
                          </div>
                        )}
                        <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 6 }}>
                          {item.department_name ?? "Institution-wide"}
                        </div>
                        {item.due_date && (
                          <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 4 }}>
                            Due: {new Date(item.due_date).toLocaleDateString()}
                          </div>
                        )}
                        <div style={{ marginTop: 10, paddingTop: 8, borderTop: "1px solid var(--border)", display: "flex", justifyContent: "flex-end" }}>
                          <Link
                            to={`/compliance/controls/${item.assignment_id}`}
                            className="btn btn-ghost btn-sm"
                            style={{ fontSize: 11, color: "var(--primary)", padding: "2px 6px" }}
                          >
                            Details <ArrowRight size={12} />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </PageShell>
  );
}
