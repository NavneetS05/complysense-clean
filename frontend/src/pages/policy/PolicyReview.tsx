// Use: Policy diff and approval workspace. Integrates AI conflict detection and executive summary parallel queries.

import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { 
  Sparkles, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  ArrowLeft,
  RefreshCw,
  TrendingUp
} from "lucide-react";
import { getApiErrorMessage } from "../../lib/errors";

type Policy = {
  policy_id: string;
  policy_name: string;
  version_number: number;
  policy_status: string;
  related_control_id?: string | null;
  policy_content?: string | null;
  submitted_to?: string | null;
  created_at: string;
};

export default function PolicyReview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [loading, setLoading] = useState(true);

  // AI Analysis States
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [aiConflicts, setAiConflicts] = useState<string | null>(null);
  const [hasRunAnalysis, setHasRunAnalysis] = useState(false);

  // Decision States
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [decisionLoading, setDecisionLoading] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const { data } = await api.get<Policy>(`/api/v1/policies/${id}`);
      setPolicy(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleRunAnalysis = async () => {
    if (!id) return;
    setAiLoading(true);
    setAiError(null);
    try {
      const { data } = await api.post(`/api/v1/ai/policy/analyze/${id}`, {});
      
      // Separate summary and conflicts responses
      setAiSummary(data.executive_summary?.response || "No summary available.");
      setAiConflicts(data.conflicts?.response || "No conflict analysis returned.");
      setHasRunAnalysis(true);
    } catch (err: unknown) {
      setAiError(getApiErrorMessage(err, "Failed to analyze policy document."));
    } finally {
      setAiLoading(false);
    }
  };

  const handleDecision = async (status: "approved" | "rejected") => {
    if (!id) return;
    setDecisionLoading(true);
    try {
      if (status === "approved") {
        await api.post(`/api/v1/policies/${id}/approve`);
      } else {
        await api.post(`/api/v1/policies/${id}/reject`, { rejection_reason: rejectionReason });
      }
      alert(`Policy ${status} successfully.`);
      navigate("/policy/inbox");
    } catch (err: unknown) {
      alert(getApiErrorMessage(err, "Failed to submit decision."));
    } finally {
      setDecisionLoading(false);
    }
  };

  if (loading) return <div className="page-panel">Loading policy details…</div>;
  if (!policy) return <div className="page-panel">Policy not found.</div>;

  const isPending = policy.policy_status === "pending_approval" || policy.policy_status === "draft";
  const hasConflicts = aiConflicts && (
    aiConflicts.toLowerCase().includes("conflict") || 
    aiConflicts.toLowerCase().includes("contradiction") || 
    aiConflicts.toLowerCase().includes("violation")
  );

  return (
    <div className="page-panel" style={{ paddingBottom: 64 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <Link to="/policy/inbox" style={{ color: "var(--muted)", display: "flex", alignItems: "center" }}>
          <ArrowLeft size={16} />
        </Link>
        <PageShell title="Policy Approval Workspace" context={`Reviewing draft of ${policy.policy_name}`} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 16, marginTop: 16 }}>
        {/* Left Column: Draft content */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 24, minHeight: 450, background: "white" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", borderBottom: "1px solid var(--border)", paddingBottom: 12, marginBottom: 16 }}>
              <div>
                <h3 style={{ margin: 0 }}>{policy.policy_name}</h3>
                <span style={{ fontSize: 12, color: "var(--muted)" }}>
                  Version {policy.version_number} · Control ID: {policy.related_control_id || "Unlinked"}
                </span>
              </div>
              <span className="badge" style={{ textTransform: "uppercase", fontSize: 11, fontWeight: 600 }}>
                {policy.policy_status}
              </span>
            </div>

            <div 
              style={{ 
                whiteSpace: "pre-wrap", 
                fontSize: 14, 
                lineHeight: 1.6, 
                color: "var(--text-primary)", 
                fontFamily: "var(--font-sans)" 
              }}
            >
              {policy.policy_content || "No content has been written in this policy draft yet."}
            </div>
          </div>

          {/* Decision Panel */}
          {isPending && (
            <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
              <h4 style={{ margin: 0, fontSize: 14, fontWeight: 600 }}>Approver Decision Panel</h4>
              
              {showRejectForm ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  <label style={{ fontSize: 12, fontWeight: 600 }}>Reason for Change Request / Rejection</label>
                  <textarea
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Provide specific feedback or missing requirements for the compliance officer..."
                    rows={3}
                    style={{ padding: 8, borderRadius: 6, border: "1px solid var(--border)", width: "100%" }}
                  />
                  <div style={{ display: "flex", gap: 8, alignSelf: "flex-end" }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => setShowRejectForm(false)}>
                      Cancel
                    </button>
                    <button 
                      className="btn btn-primary btn-sm" 
                      onClick={() => handleDecision("rejected")}
                      disabled={decisionLoading || !rejectionReason.trim()}
                      style={{ backgroundColor: "var(--critical)", borderColor: "var(--critical)" }}
                    >
                      Submit Rejection
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{ display: "flex", gap: 12 }}>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => handleDecision("approved")}
                    disabled={decisionLoading}
                    style={{ flex: 1, backgroundColor: "var(--success)", borderColor: "var(--success)", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
                  >
                    <CheckCircle size={16} /> Approve & Sign-off Policy
                  </button>
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => setShowRejectForm(true)}
                    disabled={decisionLoading}
                    style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
                  >
                    <XCircle size={16} /> Request Changes
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: AI Analysis Card */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ margin: 0, fontSize: 15, display: "flex", alignItems: "center", gap: 6 }}>
                <Sparkles size={16} color="var(--primary)" /> AI Compliance Audit
              </h3>
              {hasRunAnalysis && (
                <button 
                  className="btn btn-ghost btn-sm" 
                  onClick={handleRunAnalysis} 
                  disabled={aiLoading}
                  style={{ fontSize: 11 }}
                >
                  <RefreshCw size={12} style={{ marginRight: 4 }} className={aiLoading ? "spin" : ""} />
                  {aiLoading ? "Analyzing..." : "Re-run"}
                </button>
              )}
            </div>

            {aiLoading ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 12, padding: "16px 0" }}>
                {[90, 75, 80, 50].map((w, i) => (
                  <div key={i} className="skeleton-cell" style={{ height: 14, width: `${w}%`, borderRadius: 4 }} />
                ))}
                <span style={{ fontSize: 12, color: "var(--muted)", fontStyle: "italic", textAlign: "center", marginTop: 8 }}>
                  Checking conflicts and generating summary...
                </span>
              </div>
            ) : aiError ? (
              <div style={{ padding: 12, background: "#FEF2F2", border: "1px solid #FECACA", borderRadius: 8, display: "flex", flexDirection: "column", gap: 10 }}>
                <span style={{ color: "var(--critical)", fontSize: 12 }}>{aiError}</span>
                <button className="btn btn-secondary btn-sm" onClick={handleRunAnalysis} style={{ alignSelf: "flex-start" }}>
                  Retry Analysis
                </button>
              </div>
            ) : !hasRunAnalysis ? (
              <div style={{ textAlign: "center", padding: "32px 16px", background: "var(--surface-raised)", borderRadius: 8, border: "1px dashed var(--border)" }}>
                <p style={{ color: "var(--muted)", fontSize: 12, marginBottom: 16 }}>
                  Run AI Analysis to detect overlaps, regulatory violations, and contradictions with other policies in the library.
                </p>
                <button className="btn btn-primary" onClick={handleRunAnalysis} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                  <Sparkles size={14} /> Run AI Analysis
                </button>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                {/* Executive Summary Card */}
                <div 
                  style={{ 
                    border: "1px solid var(--border)", 
                    borderRadius: 10, 
                    padding: 16, 
                    backgroundColor: "var(--surface-raised)" 
                  }}
                >
                  <h4 style={{ margin: "0 0 10px 0", fontSize: 13, fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
                    <TrendingUp size={14} color="var(--primary)" /> Executive Briefing
                  </h4>
                  <div style={{ fontSize: 12, lineHeight: 1.5, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                    {aiSummary}
                  </div>
                </div>

                {/* Conflicts Section */}
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  <h4 style={{ margin: 0, fontSize: 13, fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
                    <AlertTriangle size={14} color={hasConflicts ? "var(--critical)" : "var(--success)"} />
                    Conflict Detection
                  </h4>

                  {hasConflicts ? (
                    <div 
                      style={{ 
                        border: "1px solid #FCA5A5", 
                        borderRadius: 10, 
                        padding: 16, 
                        backgroundColor: "#FEF2F2" 
                      }}
                    >
                      <span 
                        className="badge" 
                        style={{ backgroundColor: "var(--critical)", color: "white", fontSize: 10, marginBottom: 8 }}
                      >
                        POLICY OVERLAP / CONFLICT DETECTED
                      </span>
                      <div style={{ fontSize: 12, lineHeight: 1.5, color: "#991B1B", whiteSpace: "pre-wrap" }}>
                        {aiConflicts}
                      </div>
                    </div>
                  ) : (
                    <div 
                      style={{ 
                        border: "1px solid #86EFAC", 
                        borderRadius: 10, 
                        padding: 16, 
                        backgroundColor: "#ECFDF5",
                        color: "#166534",
                        fontSize: 12,
                        fontWeight: 500,
                        display: "flex",
                        alignItems: "center",
                        gap: 6
                      }}
                    >
                      <CheckCircle size={14} />
                      <span>No policy conflicts or regulatory gaps detected. Draft is safe to sign off.</span>
                    </div>
                  )}
                </div>

                <div style={{ fontSize: 11, color: "var(--muted)", fontStyle: "italic" }}>
                  Regulatory analysis generated using seeded frameworks (DPDP, ISO 27001). Check interpretations before final approval.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
