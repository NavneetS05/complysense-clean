// Use: Vendor detail and contract analysis workspace. Shows vendor profile, risk history, and AI contract analyzer drawer.

import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { AIPanel } from "../../components/shared/AIPanel";
import { CitationChip } from "../../components/shared/CitationChip";
import {
  Sparkles,
  ArrowLeft,
  Building2,
  MapPin,
  FileCheck,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Shield,
  Clock,
} from "lucide-react";

type RiskAssessment = {
  vendor_risk_id: string;
  risk_level: string;
  assessment_summary?: string | null;
  recommendations?: string | null;
  dpdp_compliant?: boolean | null;
  created_at?: string | null;
};

type Vendor = {
  vendor_id: string;
  vendor_name: string;
  product_name?: string | null;
  vendor_category?: string | null;
  processing_location?: string | null;
  dpa_available: boolean;
  model_training_allowed: boolean;
  contract_expiry_date?: string | null;
  contact_email?: string | null;
  created_at?: string | null;
  risk_assessments: RiskAssessment[];
};

const RISK_COLORS: Record<string, string> = {
  critical: "#EF4444",
  high: "#F97316",
  medium: "#F59E0B",
  low: "#10B981",
};

export default function VendorDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [loading, setLoading] = useState(true);

  // Contract Analyzer AI drawer
  const [analyzerOpen, setAnalyzerOpen] = useState(false);
  const [contractText, setContractText] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiResult, setAiResult] = useState<any>(null);
  const [lastRunAt, setLastRunAt] = useState<string | null>(null);

  async function load() {
    if (!id) return;
    try {
      const { data } = await api.get<Vendor>(`/api/v1/vendors/${id}`);
      setVendor(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [id]);

  const handleAnalyzeContract = async () => {
    if (!id || !contractText.trim()) return;
    setAiLoading(true);
    setAiError(null);
    try {
      const { data } = await api.post("/api/v1/ai/vendor/analyze-contract", {
        vendor_id: id,
        contract_text: contractText,
      });
      setAiResult(data);
      setLastRunAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      setAiError(err.response?.data?.detail || "Failed to analyze contract.");
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <div className="page-panel">Loading vendor details…</div>;
  if (!vendor) return <div className="page-panel">Vendor not found.</div>;

  const latestRisk = vendor.risk_assessments[0];
  const riskColor = latestRisk?.risk_level ? RISK_COLORS[latestRisk.risk_level] || "#6B7280" : "#6B7280";

  const isExpiringSoon = vendor.contract_expiry_date
    ? new Date(vendor.contract_expiry_date).getTime() - Date.now() < 90 * 24 * 3600 * 1000
    : false;

  return (
    <PageShell
      title={vendor.vendor_name}
      subtitle="Vendor contract analysis and compliance assessment workspace."
      breadcrumbs={[
        { label: "Vendors", href: "/vendor/dashboard" },
        { label: vendor.vendor_name }
      ]}
    >
      <div className="page-panel" style={{ paddingBottom: 64 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 16 }}>
        {/* Left: Vendor profile */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 48, height: 48, borderRadius: 12, background: "var(--primary-bg)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Building2 size={24} color="var(--primary)" />
                </div>
                <div>
                  <h3 style={{ margin: 0 }}>{vendor.vendor_name}</h3>
                  <span style={{ fontSize: 13, color: "var(--muted)" }}>{vendor.product_name || "No product specified"}</span>
                </div>
              </div>
              {latestRisk && (
                <span className="badge" style={{ backgroundColor: `${riskColor}1A`, color: riskColor, fontWeight: 700, fontSize: 12 }}>
                  {latestRisk.risk_level.toUpperCase()} RISK
                </span>
              )}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              {[
                { label: "Category", value: vendor.vendor_category || "—" },
                { label: "Processing Location", value: vendor.processing_location || "—" },
                { label: "Contact", value: vendor.contact_email || "—" },
                { label: "Contract Expiry", value: vendor.contract_expiry_date ? new Date(vendor.contract_expiry_date).toLocaleDateString() : "—" },
              ].map(({ label, value }) => (
                <div key={label} style={{ padding: 12, background: "var(--surface-raised)", borderRadius: 8 }}>
                  <div style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, textTransform: "uppercase" }}>{label}</div>
                  <div style={{ fontSize: 14, marginTop: 4, fontWeight: 500 }}>{value}</div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 16, display: "flex", gap: 12, flexWrap: "wrap" }}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, padding: "6px 12px", borderRadius: 20, background: vendor.dpa_available ? "#ECFDF5" : "#FEF2F2", color: vendor.dpa_available ? "#10B981" : "#EF4444", fontWeight: 500 }}>
                {vendor.dpa_available ? <CheckCircle size={12} /> : <AlertTriangle size={12} />}
                DPA {vendor.dpa_available ? "Available" : "Missing"}
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, padding: "6px 12px", borderRadius: 20, background: vendor.model_training_allowed ? "#FEF2F2" : "#ECFDF5", color: vendor.model_training_allowed ? "#EF4444" : "#10B981", fontWeight: 500 }}>
                <Shield size={12} />
                Model Training {vendor.model_training_allowed ? "Allowed" : "Prohibited"}
              </span>
              {isExpiringSoon && (
                <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, padding: "6px 12px", borderRadius: 20, background: "#FFFBEB", color: "#D97706", fontWeight: 500 }}>
                  <Clock size={12} /> Contract Expiring Soon
                </span>
              )}
            </div>
          </div>

          {/* Risk Assessment History */}
          <div className="card" style={{ padding: 20 }}>
            <h4 style={{ margin: "0 0 16px 0", fontSize: 14 }}>Risk Assessment History</h4>
            {vendor.risk_assessments.length === 0 ? (
              <p style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>No formal risk assessments recorded yet.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {vendor.risk_assessments.map((ra) => (
                  <div key={ra.vendor_risk_id} style={{ border: "1px solid var(--border)", borderRadius: 10, padding: 14 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span className="badge" style={{ backgroundColor: `${RISK_COLORS[ra.risk_level] || "#6B7280"}1A`, color: RISK_COLORS[ra.risk_level] || "#6B7280", fontWeight: 600, fontSize: 11 }}>
                        {ra.risk_level?.toUpperCase() || "UNKNOWN"} RISK
                      </span>
                      <span style={{ fontSize: 11, color: "var(--muted)" }}>
                        {ra.created_at ? new Date(ra.created_at).toLocaleDateString() : "—"}
                      </span>
                    </div>
                    {ra.assessment_summary && (
                      <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "0 0 8px 0", lineHeight: 1.5 }}>
                        {ra.assessment_summary}
                      </p>
                    )}
                    {ra.recommendations && (
                      <p style={{ fontSize: 12, color: "var(--muted)", margin: 0, fontStyle: "italic" }}>
                        Recommendations: {ra.recommendations}
                      </p>
                    )}
                    <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 6 }}>
                      {ra.dpdp_compliant === true && <CheckCircle size={12} color="var(--success)" />}
                      {ra.dpdp_compliant === false && <AlertTriangle size={12} color="var(--critical)" />}
                      <span style={{ fontSize: 11, color: "var(--muted)" }}>
                        DPDP: {ra.dpdp_compliant === true ? "Compliant" : ra.dpdp_compliant === false ? "Non-compliant" : "Not assessed"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: AI Contract Analyzer trigger */}
        <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
          <div>
            <h3 style={{ margin: "0 0 8px 0", display: "flex", alignItems: "center", gap: 8 }}>
              <Sparkles size={18} color="var(--primary)" /> Contract Compliance Analyzer
            </h3>
            <p style={{ margin: 0, fontSize: 13, color: "var(--muted)", lineHeight: 1.5 }}>
              Paste vendor contract text to run an AI-powered DPDP Act 2023 and ISO 27001 compliance check. Identifies data processing obligations, liability gaps, and missing clauses.
            </p>
          </div>

          <div style={{ background: "var(--surface-raised)", borderRadius: 10, padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>The analyzer will check for:</div>
            {[
              "Data processing agreement clauses",
              "DPDP Act obligations and consent provisions",
              "Data breach notification requirements",
              "Sub-processor disclosure requirements",
              "Data retention and deletion policies",
              "Liability and indemnification gaps",
            ].map((item) => (
              <div key={item} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "var(--text-secondary)" }}>
                <CheckCircle size={12} color="var(--success)" />
                {item}
              </div>
            ))}
          </div>

          <button
            className="btn btn-primary"
            onClick={() => setAnalyzerOpen(true)}
            style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}
          >
            <Sparkles size={16} /> Open Contract Analyzer
          </button>

          {latestRisk && (
            <div style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--muted)", marginBottom: 8 }}>LATEST RISK VERDICT</div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }}>
                {latestRisk.assessment_summary || "No summary available."}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Contract Analyzer AI Drawer */}
      <AIPanel
        open={analyzerOpen}
        onClose={() => setAnalyzerOpen(false)}
        title="Contract Compliance Analysis"
        loading={aiLoading}
        error={aiError}
        onRetry={handleAnalyzeContract}
        hasResult={!!aiResult}
        emptyTitle="Paste Contract Text"
        emptyDescription="Provide the full or partial contract text to run AI-powered compliance checks against DPDP Act 2023, ISO 27001, and standard DPA requirements."
        emptyActionLabel="Analyze Contract"
        onEmptyAction={contractText.trim().length >= 100 ? handleAnalyzeContract : undefined}
        lastRunAt={lastRunAt}
        onRegenerate={handleAnalyzeContract}
        regenerateLoading={aiLoading}
      >
        {!aiResult ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12, width: "100%" }}>
            <label style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>
              Contract text or clause extract
            </label>
            <textarea
              style={{
                width: "100%",
                minHeight: 200,
                padding: 10,
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border)",
                background: "var(--surface)",
                color: "var(--text-primary)",
                fontFamily: "monospace",
                fontSize: 12,
                resize: "vertical",
              }}
              placeholder="Paste the contract text, DPA clauses, or data processing agreement sections here... (min 100 characters)"
              value={contractText}
              onChange={(e) => setContractText(e.target.value)}
              maxLength={5000}
            />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--muted)" }}>
              <span>Minimum 100 characters required</span>
              <span>{contractText.length} / 5000</span>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleAnalyzeContract}
              disabled={contractText.trim().length < 100 || aiLoading}
              style={{ alignSelf: "flex-end", display: "flex", alignItems: "center", gap: 6 }}
            >
              <Sparkles size={14} /> Analyze Contract
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--success)", display: "flex", alignItems: "center", gap: 4 }}>
                <CheckCircle size={14} /> Analysis Complete
              </span>
              <button className="btn btn-ghost btn-sm" onClick={() => setAiResult(null)} style={{ fontSize: 11 }}>
                New Analysis
              </button>
            </div>

            {/* Render citations */}
            {Array.isArray(aiResult.citations) && aiResult.citations.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                {aiResult.citations.map((c: string, i: number) => (
                  <CitationChip key={i} framework={c} />
                ))}
              </div>
            )}

            {/* Analysis content */}
            <div style={{ whiteSpace: "pre-wrap", fontSize: 13, lineHeight: 1.6, color: "var(--text-primary)" }}>
              {aiResult.response}
            </div>

            <div style={{ fontSize: 11, color: "var(--muted)", fontStyle: "italic" }}>
              Contract analysis is AI-generated. Verify critical legal interpretations with your data privacy counsel before relying on findings.
            </div>
          </div>
        )}
      </AIPanel>
    </div>
  </PageShell>
);
}
