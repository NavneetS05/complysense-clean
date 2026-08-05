// Use: Generates PDF executive briefing reports using AI summaries.

import { useState, useEffect, useCallback } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";
import { FileText, Plus, Sparkles, Download, Calendar } from "lucide-react";

interface AuditReport {
  report_id: string;
  report_name: string;
  report_type: string;
  file_path: string;
  generated_at: string;
}

const REPORT_TYPE_LABELS: Record<string, string> = {
  naac: "NAAC Criteria 4 & 6 Verification Briefing",
  iso_readiness: "ISO 27001 Gap Analysis Executive Report",
  dpdp_assessment: "DPDP Section 8 Compliance Assessment",
  custom: "Compliance Status Custom Executive Briefing",
};

export default function Reports() {
  const toast = useToast();
  const [reports, setReports] = useState<AuditReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [reportType, setReportType] = useState("iso_readiness");
  const [periodFrom, setPeriodFrom] = useState("");
  const [periodTo, setPeriodTo] = useState("");

  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/policies/reports");
      setReports(res.data);
    } catch {
      toast.error("Failed to load reports");
    }
    setLoading(false);
  }, [toast]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  async function handleGenerate() {
    setModalLoading(true);
    try {
      await api.post("/api/v1/policies/reports/generate", {
        report_type: reportType,
        period_from: periodFrom || null,
        period_to: periodTo || null,
      });
      toast.success("Report generated successfully");
      setModalOpen(false);
      fetchReports();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to generate report"));
    }
    setModalLoading(false);
  }

  return (
    <PageShell
      title="Executive Briefings"
      subtitle="Generate and review compliance executive briefing reports"
      actions={
        <button
          className="btn btn-primary"
          onClick={() => setModalOpen(true)}
          style={{ display: "flex", alignItems: "center", gap: 6 }}
        >
          <Plus size={16} /> New Briefing
        </button>
      }
    >
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Generated Briefings</h2>
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Report Name</th>
                <th>Type</th>
                <th>Generated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 4 }).map((_, j) => (
                      <td key={j}>
                        <div className="skeleton" style={{ height: 18, borderRadius: 4 }} />
                      </td>
                    ))}
                  </tr>
                ))
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", padding: "48px 16px" }}>
                    <FileText
                      size={36}
                      style={{
                        color: "var(--text-muted)",
                        marginBottom: 10,
                        display: "block",
                        margin: "0 auto 10px",
                      }}
                    />
                    <p style={{ color: "var(--text-muted)", margin: 0, fontSize: 14 }}>
                      No reports generated yet.
                    </p>
                  </td>
                </tr>
              ) : (
                reports.map((report) => (
                  <tr key={report.report_id}>
                    <td style={{ fontWeight: 600 }}>{report.report_name}</td>
                    <td>
                      <span className="badge badge-draft">
                        {REPORT_TYPE_LABELS[report.report_type] ?? report.report_type}
                      </span>
                    </td>
                    <td
                      style={{
                        fontSize: 12,
                        color: "var(--text-muted)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {new Date(report.generated_at).toLocaleString("en-IN")}
                    </td>
                    <td>
                      <a
                        href={`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}${
                          report.file_path
                        }`}
                        download
                        className="btn btn-ghost"
                        style={{
                          padding: "4px 10px",
                          fontSize: 12,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 4,
                        }}
                      >
                        <Download size={13} /> Download PDF
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal" style={{ maxWidth: 500 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Sparkles size={18} style={{ color: "var(--primary)" }} /> Generate Executive Briefing
              </h2>
              <button className="modal-close" onClick={() => setModalOpen(false)}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Report Type *</label>
                  <select
                    className="form-input"
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                  >
                    {Object.entries(REPORT_TYPE_LABELS).map(([k, v]) => (
                      <option key={k} value={k}>
                        {v}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid-2" style={{ gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">Period From</label>
                    <div style={{ position: "relative" }}>
                      <Calendar
                        size={14}
                        style={{
                          position: "absolute",
                          left: 10,
                          top: "50%",
                          transform: "translateY(-50%)",
                          color: "var(--text-muted)",
                        }}
                      />
                      <input
                        type="date"
                        className="form-input"
                        value={periodFrom}
                        onChange={(e) => setPeriodFrom(e.target.value)}
                        style={{ paddingLeft: 30 }}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Period To</label>
                    <div style={{ position: "relative" }}>
                      <Calendar
                        size={14}
                        style={{
                          position: "absolute",
                          left: 10,
                          top: "50%",
                          transform: "translateY(-50%)",
                          color: "var(--text-muted)",
                        }}
                      />
                      <input
                        type="date"
                        className="form-input"
                        value={periodTo}
                        onChange={(e) => setPeriodTo(e.target.value)}
                        style={{ paddingLeft: 30 }}
                      />
                    </div>
                  </div>
                </div>
                <p style={{ fontSize: 12, color: "var(--text-muted)", margin: 0 }}>
                  Generating this briefing will compile compliance readiness data and trigger AI model summaries.
                </p>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setModalOpen(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleGenerate}
                disabled={modalLoading}
                style={{ display: "flex", alignItems: "center", gap: 6 }}
              >
                {modalLoading ? (
                  <>
                    <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles size={14} /> Generate
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </PageShell>
  );
}
