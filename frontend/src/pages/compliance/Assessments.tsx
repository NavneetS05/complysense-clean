// Use: List of active and historical compliance assessments.

import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type AssessmentItem = {
  assessment_id: string;
  assessment_name: string;
  framework_name: string;
  assessment_status: string;
  started_at?: string;
};

export default function Assessments() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/assessments");
    return Array.isArray(res.data) ? res.data : res.data?.assessments ?? [];
  }, []);

  const assessments: AssessmentItem[] = data ?? [];

  return (
    <div className="page-panel">
      <h2>Assessments</h2>
      <p>Operational assessment runs and their current status.</p>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : assessments.length === 0 ? (
        <EmptyState title="No assessments" description="No assessment runs found for your institution." actionLabel="Refresh" onAction={() => void refetch()} />
      ) : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>Assessment</th>
                <th style={{ padding: "8px 6px" }}>Framework</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((item) => (
                <tr key={item.assessment_id}>
                  <td style={{ padding: "8px 6px" }}>{item.assessment_name}</td>
                  <td style={{ padding: "8px 6px" }}>{item.framework_name}</td>
                  <td style={{ padding: "8px 6px" }}>{item.assessment_status}</td>
                  <td style={{ padding: "8px 6px" }}><Link to={`/compliance/assessments/${item.assessment_id}`}>Open</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
