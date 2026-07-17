// Use: Lists technical security controls assigned to the IT security officer.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

interface ControlItem {
  assignment_id: string;
  control_id: string;
  framework_name: string;
  status: string;
  due_date?: string | null;
  assigned_name?: string | null;
}

export default function Controls() {
  const [controls, setControls] = useState<ControlItem[]>([]);
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get<ControlItem[]>("/api/v1/controls");
    return Array.isArray(res.data) ? res.data : res.data?.controls ?? [];
  }, []);

  useEffect(() => {
    if (!data) return;
    setControls(data as ControlItem[]);
  }, [data]);

  return (
    <div className="page-panel">
      <PageShell title="IT Control Assignments" context="Technical control assignments and due dates." />
      <div style={{ overflowX: "auto", marginTop: 16 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb" }}>
              <th style={{ padding: 10 }}>Control</th>
              <th style={{ padding: 10 }}>Framework</th>
              <th style={{ padding: 10 }}>Status</th>
              <th style={{ padding: 10 }}>Due</th>
              <th style={{ padding: 10 }}>Owner</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} style={{ padding: 16 }}><Loading /></td></tr>
            ) : error ? (
              <tr><td colSpan={5} style={{ padding: 16 }}><ErrorState message={error.message} onRetry={() => void refetch()} /></td></tr>
            ) : controls.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: 16 }}><EmptyState title="No controls" description="No control assignments found." /></td></tr>
            ) : controls.map((item) => (
              <tr key={item.assignment_id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                <td style={{ padding: 10 }}>{item.control_id}</td>
                <td style={{ padding: 10 }}>{item.framework_name}</td>
                <td style={{ padding: 10 }}>{item.status}</td>
                <td style={{ padding: 10 }}>{item.due_date ? new Date(item.due_date).toLocaleDateString() : "—"}</td>
                <td style={{ padding: 10 }}>{item.assigned_name ?? "Unassigned"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
