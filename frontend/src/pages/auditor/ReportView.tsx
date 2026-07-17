// Use: View screen for compiled PDF audit reports.

import { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";

type ReportDetail = {
  report_id: string;
  report_name: string;
  report_type?: string;
  generated_at?: string;
  assessment?: {
    assessment_name?: string;
    framework_name?: string;
    assessment_status?: string;
  };
  summary?: {
    observation_count?: number;
    gaps?: Array<{ title?: string; severity?: string; remediation_status?: string }>;
    observations?: Array<{ observation_text?: string; severity?: string; status?: string }>;
  };
};

export default function ReportView() {
  const { id } = useParams();
  const { data: report, loading, error, refetch } = useApi(async () => {
    const res = await api.get(`/api/v1/audit/reports/${id}`);
    return res.data as ReportDetail;
  }, [id]);

  if (loading) return <div className="page-panel"><Loading /></div>;
  if (error) return <div className="page-panel"><ErrorState message={error.message} onRetry={() => void refetch()} /></div>;
  if (!report) return <div className="page-panel">Report not found.</div>;

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>{report.report_name}</h2>
        <p>{report.report_type || "Custom"} • Generated {report.generated_at ? new Date(report.generated_at).toLocaleString() : "—"}</p>
      </div>
      <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16 }}>
        <div><strong>Assessment:</strong> {report.assessment?.assessment_name || "—"}</div>
        <div><strong>Framework:</strong> {report.assessment?.framework_name || "—"}</div>
        <div><strong>Status:</strong> {report.assessment?.assessment_status || "—"}</div>
        <div><strong>Observations:</strong> {report.summary?.observation_count || 0}</div>
      </div>
      <div style={{ display: "grid", gap: 12 }}>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Gaps</h3>
          {(report.summary?.gaps ?? []).map((gap, index) => (
            <div key={`${gap.title}-${index}`} style={{ borderTop: "1px solid #f1f5f9", paddingTop: 8, marginTop: 8 }}>
              <div style={{ fontWeight: 700 }}>{gap.title || "Gap"}</div>
              <div style={{ color: "#64748b", fontSize: 13 }}>{gap.severity || "—"} • {gap.remediation_status || "—"}</div>
            </div>
          ))}
        </div>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Observations</h3>
          {(report.summary?.observations ?? []).map((observation, index) => (
            <div key={`${observation.observation_text}-${index}`} style={{ borderTop: "1px solid #f1f5f9", paddingTop: 8, marginTop: 8 }}>
              <div style={{ fontWeight: 700 }}>{observation.observation_text || "Observation"}</div>
              <div style={{ color: "#64748b", fontSize: 13 }}>{observation.severity || "—"} • {observation.status || "—"}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
