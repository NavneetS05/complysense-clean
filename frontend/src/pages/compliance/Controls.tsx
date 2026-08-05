// Use: Kanban board for managing institution control assignments.

import { useMemo } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type ControlAssignment = {
  assignment_id: string;
  control_id: string;
  framework_name: string;
  status: string;
  due_date?: string;
  assigned_to?: string;
  department_name?: string;
};

const COLUMN_META = [
  { key: "not_started", title: "Not Started", color: "#64748b" },
  { key: "in_progress", title: "In Progress", color: "#2563eb" },
  { key: "submitted", title: "Submitted", color: "#7c3aed" },
  { key: "compliant", title: "Compliant", color: "#16a34a" },
  { key: "non_compliant", title: "Non-Compliant", color: "#dc2626" },
];

export default function Controls() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/controls");
    return Array.isArray(res.data) ? res.data : res.data?.controls ?? [];
  }, []);

  const controls = useMemo<ControlAssignment[]>(() => data ?? [], [data]);

  const grouped = useMemo(() => {
    return COLUMN_META.reduce((acc, column) => {
      acc[column.key] = controls.filter((item) => item.status === column.key);
      return acc;
    }, {} as Record<string, ControlAssignment[]>);
  }, [controls]);

  return (
    <div className="page-panel">
      <h2>Controls</h2>
      <p>Operational control assignments grouped by status.</p>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : controls.length === 0 ? (
        <EmptyState title="No controls" description="No control assignments found." actionLabel="Refresh" onAction={() => void refetch()} />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(220px, 1fr))", gap: 12, overflowX: "auto", marginTop: 16 }}>
          {COLUMN_META.map((column) => (
            <div key={column.key} className="card" style={{ padding: 12, minHeight: 320 }}>
              <div style={{ fontWeight: 700, color: column.color, marginBottom: 10 }}>{column.title} ({grouped[column.key]?.length ?? 0})</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {(grouped[column.key] ?? []).map((item) => (
                  <div key={item.assignment_id} style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}>
                    <div style={{ fontSize: 12, color: "var(--muted)" }}>{item.framework_name}</div>
                    <div style={{ fontWeight: 600, marginTop: 4 }}>{item.control_id}</div>
                    <div style={{ fontSize: 12, marginTop: 4 }}>{item.department_name ?? "Institution-wide"}</div>
                    {item.due_date ? <div style={{ fontSize: 12, marginTop: 4 }}>Due {new Date(item.due_date).toLocaleDateString()}</div> : null}
                    <Link to={`/compliance/controls/${item.assignment_id}`} style={{ fontSize: 12, color: "var(--primary)" }}>View detail →</Link>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
