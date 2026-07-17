// Use: Matrix view of identified compliance gaps sorted by framework.

import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type GapRow = {
  gap_id: string;
  control_id?: string;
  framework_name: string;
  severity: string;
  title: string;
  remediation_status: string;
  created_at?: string;
};

export default function Gaps() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/gaps");
    return Array.isArray(res.data) ? res.data : res.data?.gaps ?? [];
  }, []);

  const gaps: GapRow[] = data ?? [];

  return (
    <div className="page-panel">
      <h2>Compliance Gaps</h2>
      <p>Open and in-progress remediation items across the institution.</p>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : gaps.length === 0 ? (
        <EmptyState title="No gaps" description="No compliance gaps found." actionLabel="Refresh" onAction={() => void refetch()} />
      ) : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>Severity</th>
                <th style={{ padding: "8px 6px" }}>Framework</th>
                <th style={{ padding: "8px 6px" }}>Control</th>
                <th style={{ padding: "8px 6px" }}>Gap</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {gaps.map((gap) => (
                <tr key={gap.gap_id}>
                  <td style={{ padding: "8px 6px" }}>{gap.severity}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.framework_name}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.control_id ?? "—"}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.title}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.remediation_status}</td>
                  <td style={{ padding: "8px 6px" }}><Link to="/compliance/tasks">Create task</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
