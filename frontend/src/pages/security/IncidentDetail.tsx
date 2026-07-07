// Use: Incident control center with a 6-hour CERT-In countdown, AI draft report panel, clipboard copy, text download, and status updates.

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../PageShell";
import { AIPanel } from "../../components/shared/AIPanel";
import { 
  Sparkles, 
  Copy, 
  Download, 
  CheckCircle, 
  AlertTriangle, 
  ShieldAlert, 
  Activity, 
  FileText,
  Clock
} from "lucide-react";

interface TimelineItem {
  action_taken: string;
  action_at?: string | null;
}

interface IncidentDetailData {
  incident_id: string;
  title: string;
  description?: string | null;
  severity: string;
  status: string;
  incident_type?: string | null;
  detected_at?: string | null;
  cert_in_deadline?: string | null;
  cert_in_reported: boolean;
  cert_in_reported_at?: string | null;
  dpdp_notification_required: boolean;
  affected_systems?: string | null;
  affected_data_categories?: string | null;
  resolution_notes?: string | null;
  timeline: TimelineItem[];
}

function countdownLabel(deadline?: string | null) {
  if (!deadline) return "—";
  const diff = new Date(deadline).getTime() - Date.now();
  if (diff <= 0) return "OVERDUE";
  const hours = Math.max(1, Math.round(diff / 3600000));
  return `${hours}h remaining`;
}

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<IncidentDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  // AI Drawer States
  const [certDrawerOpen, setCertDrawerOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [reportDraft, setReportDraft] = useState<string>("");
  const [lastRunAt, setLastRunAt] = useState<string | null>(null);
  const [confirmReportModal, setConfirmReportModal] = useState(false);

  async function load() {
    if (!id) return;
    try {
      const { data } = await api.get<IncidentDetailData>(`/api/v1/incidents/${id}`);
      setIncident(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [id]);

  const deadlineHint = useMemo(() => countdownLabel(incident?.cert_in_deadline), [incident]);

  async function updateStatus(nextStatus: string) {
    if (!id) return;
    await api.patch(`/api/v1/incidents/${id}`, { status: nextStatus });
    await load();
  }

  const handleGenerateReport = async () => {
    if (!id) return;
    setAiLoading(true);
    setAiError(null);
    try {
      const { data } = await api.post(`/api/v1/ai/security/cert-in-draft/${id}`, {});
      setReportDraft(data.response || "");
      setLastRunAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      setAiError(err.response?.data?.detail || "Failed to generate report draft.");
    } finally {
      setAiLoading(false);
    }
  };

  const handleCopyClipboard = () => {
    navigator.clipboard.writeText(reportDraft);
    alert("Report draft copied to clipboard.");
  };

  const handleDownloadTxt = () => {
    const blob = new Blob([reportDraft], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `CERT_In_Report_${id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleMarkAsReported = async () => {
    if (!id) return;
    try {
      await api.patch(`/api/v1/incidents/${id}`, { cert_in_reported: true });
      setConfirmReportModal(false);
      setCertDrawerOpen(false);
      await load();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to mark as reported.");
    }
  };

  // Helper to count [FILL IN:] placeholders
  const fillInCount = useMemo(() => {
    if (!reportDraft) return 0;
    const matches = reportDraft.match(/\[FILL IN:[^\]]*\]/g);
    return matches ? matches.length : 0;
  }, [reportDraft]);

  if (loading) return <div className="page-panel">Loading…</div>;
  if (!incident) return <div className="page-panel">Incident not found.</div>;

  return (
    <div className="page-panel" style={{ paddingBottom: 64 }}>
      <PageShell title="Incident Command Center" context="CERT-In countdown and response workspace." />
      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 0.7fr", gap: 16, marginTop: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
            <div>
              <h3 style={{ margin: 0 }}>{incident.title}</h3>
              <div style={{ color: "#6b7280", fontSize: 13 }}>{incident.incident_type ?? "Incident"} • {incident.severity}</div>
            </div>
            <span style={{ padding: "6px 10px", borderRadius: 999, background: "#f3f4f6", fontWeight: 600, fontSize: 12 }}>
              {incident.status.toUpperCase()}
            </span>
          </div>
          <p style={{ marginTop: 12, fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.5 }}>
            {incident.description}
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12, marginTop: 12 }}>
            <div style={{ background: "#f9fafb", borderRadius: 10, padding: 10 }}>
              <div style={{ fontSize: 12, color: "#6b7280" }}>Detected</div>
              <div style={{ fontSize: 14, fontWeight: 500 }}>{incident.detected_at ? new Date(incident.detected_at).toLocaleString() : "—"}</div>
            </div>
            <div style={{ background: "#f9fafb", borderRadius: 10, padding: 10 }}>
              <div style={{ fontSize: 12, color: "#6b7280" }}>CERT-In Deadline</div>
              <div style={{ fontSize: 14, fontWeight: 500 }}>{incident.cert_in_deadline ? new Date(incident.cert_in_deadline).toLocaleString() : "—"}</div>
            </div>
          </div>

          {/* CERT-In Status Checklist Card */}
          <div 
            style={{ 
              marginTop: 16, 
              background: incident.cert_in_reported ? "#ecfdf3" : "#fffbeb", 
              border: `1px solid ${incident.cert_in_reported ? "#86efac" : "#fde68a"}`, 
              borderRadius: 12, 
              padding: 16 
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <strong style={{ display: "block", fontSize: 14, color: incident.cert_in_reported ? "#15803d" : "#92400E" }}>
                  CERT-In Compliance
                </strong>
                <span style={{ fontSize: 12, color: incident.cert_in_reported ? "#166534" : "#b45309" }}>
                  {incident.cert_in_reported 
                    ? `Report filed on ${incident.cert_in_reported_at ? new Date(incident.cert_in_reported_at).toLocaleString() : "System"}` 
                    : `Mandatory reporting deadline: ${deadlineHint}`}
                </span>
              </div>
              {!incident.cert_in_reported && (
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={() => {
                    setCertDrawerOpen(true);
                    if (!reportDraft) void handleGenerateReport();
                  }}
                  style={{ display: "flex", alignItems: "center", gap: 4, padding: "6px 12px" }}
                >
                  <Sparkles size={12} /> AI Draft Report
                </button>
              )}
            </div>
          </div>
        </div>

        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Actions</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <button onClick={() => void updateStatus("investigating")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff", cursor: "pointer" }}>Mark Investigating</button>
            <button onClick={() => void updateStatus("contained")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff", cursor: "pointer" }}>Mark Contained</button>
            <button onClick={() => void updateStatus("resolved")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff", cursor: "pointer" }}>Resolve</button>
            <button onClick={() => void updateStatus("closed")} style={{ padding: 10, borderRadius: 8, border: "1px solid #d1d5db", background: "#fff", cursor: "pointer" }}>Close</button>
            <button onClick={() => navigate(-1)} style={{ padding: 10, borderRadius: 8, border: 0, background: "#2563eb", color: "#fff", cursor: "pointer", fontWeight: 500 }}>Back to register</button>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Incident Details</h3>
          <div style={{ color: "#4b5563", fontSize: 14, margin: "6px 0" }}><strong>Affected systems:</strong> {incident.affected_systems || "—"}</div>
          <div style={{ color: "#4b5563", fontSize: 14, margin: "6px 0" }}><strong>Data categories:</strong> {incident.affected_data_categories || "—"}</div>
          <div style={{ color: "#4b5563", fontSize: 14, margin: "6px 0" }}><strong>DPDP notification:</strong> {incident.dpdp_notification_required ? "Required" : "Not required"}</div>
          <div style={{ color: "#4b5563", fontSize: 14, margin: "6px 0" }}><strong>Resolution notes:</strong> {incident.resolution_notes || "—"}</div>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Timeline</h3>
          {incident.timeline.length === 0 ? <div style={{ fontSize: 13, color: "var(--muted)" }}>No timeline entries yet.</div> : incident.timeline.map((entry, index) => (
            <div key={`${entry.action_taken}-${index}`} style={{ borderTop: index === 0 ? "0" : "1px solid #f3f4f6", paddingTop: index === 0 ? 0 : 8, marginTop: index === 0 ? 0 : 8 }}>
              <div style={{ fontSize: 13, color: "var(--text-primary)" }}>{entry.action_taken}</div>
              <div style={{ color: "#6b7280", fontSize: 11, marginTop: 2 }}>{entry.action_at ? new Date(entry.action_at).toLocaleString() : "—"}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CERT-In Report Drafter Drawer */}
      <AIPanel
        open={certDrawerOpen}
        onClose={() => setCertDrawerOpen(false)}
        title="CERT-In Report Draft"
        loading={aiLoading}
        error={aiError}
        onRetry={handleGenerateReport}
        hasResult={!!reportDraft}
        emptyTitle="Draft CERT-In Compliance Report"
        emptyDescription="Review timeline events and create a structured Incident Report matching government directives."
        emptyActionLabel="Generate Draft"
        onEmptyAction={handleGenerateReport}
        lastRunAt={lastRunAt}
        onRegenerate={handleGenerateReport}
        regenerateLoading={aiLoading}
      >
        {reportDraft && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Amber warning for [FILL IN:] placeholders */}
            {fillInCount > 0 && (
              <div
                style={{
                  background: "#FEF3C7",
                  border: "1px solid #FCD34D",
                  color: "#92400E",
                  padding: 10,
                  borderRadius: 8,
                  fontSize: 12,
                  fontWeight: 500,
                  display: "flex",
                  alignItems: "center",
                  gap: 6
                }}
              >
                <AlertTriangle size={14} />
                <span>{fillInCount} field(s) need manual completion. Search "[FILL IN:]" below.</span>
              </div>
            )}

            {/* Monospace draft container */}
            <div
              style={{
                fontFamily: "monospace",
                whiteSpace: "pre-wrap",
                background: "#FAFAF7",
                border: "1px solid var(--border)",
                borderRadius: 8,
                padding: 16,
                fontSize: 12,
                color: "#1F2937",
                lineHeight: 1.5,
                maxHeight: 400,
                overflowY: "auto"
              }}
            >
              {/* Highlight [FILL IN:] tags in amber */}
              {reportDraft.split(/(\[FILL IN:[^\]]*\])/g).map((chunk, idx) => {
                if (chunk.startsWith("[FILL IN:")) {
                  return (
                    <mark 
                      key={idx} 
                      style={{ 
                        background: "#FDE68A", 
                        color: "#92400E", 
                        padding: "0 2px", 
                        borderRadius: 3,
                        fontWeight: 600
                      }}
                    >
                      {chunk}
                    </mark>
                  );
                }
                return chunk;
              })}
            </div>

            {/* Quick Actions Panel */}
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", gap: 8 }}>
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={handleCopyClipboard}
                  style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}
                >
                  <Copy size={12} /> Copy to Clipboard
                </button>
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={handleDownloadTxt}
                  style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}
                >
                  <Download size={12} /> Download .txt
                </button>
              </div>

              <button 
                className="btn btn-primary" 
                onClick={() => setConfirmReportModal(true)}
                style={{ width: "100%", backgroundColor: "#10B981", borderColor: "#10B981", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
              >
                <CheckCircle size={14} /> Mark CERT-In as Reported
              </button>
            </div>
          </div>
        )}
      </AIPanel>

      {/* Confirmation Modal */}
      {confirmReportModal && (
        <div 
          style={{ 
            position: "fixed", 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            backgroundColor: "rgba(0, 0, 0, 0.4)", 
            display: "flex", 
            justifyContent: "center", 
            alignItems: "center",
            zIndex: 110
          }}
        >
          <div className="card" style={{ width: 400, padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
            <h3 style={{ margin: 0 }}>Confirm CERT-In Submission</h3>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0, lineHeight: 1.5 }}>
              Have you submitted this incident report to the official CERT-In portal? Marking this as reported will permanently close the compliance countdown checklist for this incident.
            </p>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 8 }}>
              <button className="btn btn-secondary" onClick={() => setConfirmReportModal(false)}>
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleMarkAsReported}
                style={{ backgroundColor: "#10B981", borderColor: "#10B981" }}
              >
                Yes, Reported
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
