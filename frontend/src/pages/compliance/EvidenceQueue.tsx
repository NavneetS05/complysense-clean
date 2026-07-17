// Use: Approval queue for verification of uploaded evidence documents.

import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type EvidenceItem = {
  evidence_id: string;
  file_name: string;
  control_id?: string;
  approval_status: string;
  uploaded_at?: string;
  file_size_kb?: number;
};

export default function EvidenceQueue() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/evidence");
    return Array.isArray(res.data) ? res.data : res.data?.evidence ?? [];
  }, []);

  const evidence: EvidenceItem[] = data ?? [];

  return (
    <div className="page-panel">
      <h2>Evidence Queue</h2>
      <p>Pending evidence submissions requiring review.</p>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : evidence.length === 0 ? (
        <EmptyState title="No evidence" description="No pending evidence submissions." actionLabel="Refresh" onAction={() => void refetch()} />
      ) : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>File</th>
                <th style={{ padding: "8px 6px" }}>Control</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Size</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((item) => (
                <tr key={item.evidence_id}>
                  <td style={{ padding: "8px 6px" }}>{item.file_name}</td>
                  <td style={{ padding: "8px 6px" }}>{item.control_id ?? "—"}</td>
                  <td style={{ padding: "8px 6px" }}>{item.approval_status}</td>
                  <td style={{ padding: "8px 6px" }}>{item.file_size_kb ? `${item.file_size_kb} KB` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
