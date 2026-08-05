// Use: Drag-and-drop tool to assemble and compile audit reports.

import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";

type Assessment = {
  assessment_id: string;
  assessment_name: string;
  framework_name?: string;
  assessment_status?: string;
};

type ReportItem = {
  report_id: string;
  report_name: string;
  report_type?: string;
  generated_at?: string;
  assessment_id?: string;
};

export default function ReportBuilder() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ assessment_id: "", report_name: "", report_type: "Custom" });
  const [submitting, setSubmitting] = useState(false);
  const [filters, setFilters] = useState({ search: "", type: "" });

  const { data, loading, error, refetch } = useApi(async () => {
    const [{ data: assessmentData }, { data: reportData }] = await Promise.all([
      api.get("/api/v1/assessments"),
      api.get("/api/v1/audit/reports"),
    ]);
    const assessmentsList = Array.isArray(assessmentData) ? assessmentData : assessmentData?.assessments ?? [];
    const reportsList = Array.isArray(reportData) ? reportData : reportData?.reports ?? [];
    return { assessmentsList, reportsList };
  }, []);

  useEffect(() => {
    if (!data) return;
    setAssessments((data.assessmentsList as Assessment[]).filter((item) => item.assessment_status === "completed"));
    setReports(data.reportsList as ReportItem[]);
  }, [data]);

  async function handleGenerate(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/api/v1/audit/reports/generate", {
        assessment_id: form.assessment_id,
        report_name: form.report_name || "Audit Report",
        report_type: form.report_type,
        sections: ["Executive Summary", "Findings Summary", "Evidence Index"],
      });
      setShowForm(false);
      setForm({ assessment_id: "", report_name: "", report_type: "Custom" });
      await refetch();
    } finally {
      setSubmitting(false);
    }
  }

  const filteredReports = useMemo(() => {
    return reports.filter((report) => {
      const name = (report.report_name || "").toLowerCase();
      const matchesSearch = !filters.search || name.includes(filters.search.toLowerCase());
      const matchesType = !filters.type || report.report_type === filters.type;
      return matchesSearch && matchesType;
    });
  }, [reports, filters]);

  const reportTypes = useMemo(() => {
    return Array.from(new Set(reports.map((r) => r.report_type).filter(Boolean)));
  }, [reports]);

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h2>Audit Reports</h2>
          <p>Create and review audit reports from completed assessments.</p>
        </div>
        <button onClick={() => setShowForm((current) => !current)} className="btn btn-primary">+ Generate New Report</button>
      </div>

      {showForm ? (
        <form onSubmit={handleGenerate} style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, display: "grid", gap: 12 }}>
          <h3 style={{ margin: 0 }}>Generate Audit Report</h3>
          <label style={{ display: "grid", gap: 4 }}>
            <span>Assessment</span>
            <select value={form.assessment_id} onChange={(event) => setForm((current) => ({ ...current, assessment_id: event.target.value }))} required style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }}>
              <option value="">Select assessment</option>
              {assessments.map((item) => (
                <option key={item.assessment_id} value={item.assessment_id}>{item.assessment_name} — {item.framework_name}</option>
              ))}
            </select>
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span>Report Name</span>
            <input value={form.report_name} onChange={(event) => setForm((current) => ({ ...current, report_name: event.target.value }))} placeholder="Framework Audit Report" style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span>Report Type</span>
            <select value={form.report_type} onChange={(event) => setForm((current) => ({ ...current, report_type: event.target.value }))} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }}>
              <option value="NAAC">NAAC</option>
              <option value="ISO Readiness">ISO Readiness</option>
              <option value="DPDP Assessment">DPDP Assessment</option>
              <option value="Custom">Custom</option>
            </select>
          </label>
          <button type="submit" disabled={submitting} className="btn btn-primary" style={{ width: 180 }}>
            {submitting ? "Generating…" : "Generate Report"}
          </button>
        </form>
      ) : null}

      <section className="card" style={{ display: "flex", gap: 12, padding: 12 }}>
        <input 
          className="form-input" 
          placeholder="Search reports by name..." 
          value={filters.search} 
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
        />
        <select 
          className="form-input" 
          value={filters.type} 
          onChange={(e) => setFilters((f) => ({ ...f, type: e.target.value }))}
          style={{ minWidth: 160 }}
        >
          <option value="">All Types</option>
          {reportTypes.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </section>

      {loading ? <Loading /> : error ? <ErrorState message={error.message} onRetry={() => void refetch()} /> : (
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", background: "#f8fafc" }}>
                <th style={{ padding: 10 }}>Report Name</th>
                <th style={{ padding: 10 }}>Assessment</th>
                <th style={{ padding: 10 }}>Type</th>
                <th style={{ padding: 10 }}>Generated</th>
                <th style={{ padding: 10 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredReports.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: 24, color: "var(--text-secondary)", textAlign: "center" }}>
                    No reports match the filter criteria.
                  </td>
                </tr>
              ) : (
                filteredReports.map((report) => (
                  <tr key={report.report_id} style={{ borderTop: "1px solid #e2e8f0" }}>
                    <td style={{ padding: 10, fontWeight: 600 }}>{report.report_name}</td>
                    <td style={{ padding: 10 }}>{report.assessment_id || "—"}</td>
                    <td style={{ padding: 10 }}>
                      <span className="badge badge-info">{report.report_type || "Custom"}</span>
                    </td>
                    <td style={{ padding: 10 }}>{report.generated_at ? new Date(report.generated_at).toLocaleString() : "—"}</td>
                    <td style={{ padding: 10 }}>
                      <Link to={`/auditor/reports/${report.report_id}`} className="btn btn-secondary btn-sm">View</Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
