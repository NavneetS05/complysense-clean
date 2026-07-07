// Use: RegulatoryChangeDrawer — Right-side drawer for pasting new regulatory circulars, triggering RAG gap analysis, and displaying impact lists.

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AIPanel } from "../shared/AIPanel";
import { api } from "../../lib/api";
import { Sparkles, ArrowRight, AlertTriangle, AlertCircle, CheckCircle, FileText } from "lucide-react";

interface RegulatoryChangeDrawerProps {
  open: boolean;
  onClose: () => void;
}

export function RegulatoryChangeDrawer({ open, onClose }: RegulatoryChangeDrawerProps) {
  const [circularText, setCircularText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [lastRunAt, setLastRunAt] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (circularText.trim().length < 200) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post("/api/v1/ai/compliance/regulatory-change", {
        circular_text: circularText,
      });
      setResult(data);
      setLastRunAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to analyze regulation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setCircularText("");
    setError(null);
  };

  // Helper to parse sections out of the AI response
  const renderSections = () => {
    if (!result || !result.response) return null;
    const text = result.response;

    // Search for a deadline date or risk keywords
    const deadlineMatch = text.match(/(deadline|by|due date|target date|before|effective from)\s*[:\-\s]*([A-Za-z0-9\s,\-\/]{6,25})/i);
    const deadlineText = deadlineMatch ? deadlineMatch[2].trim() : null;

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {/* Timeline Risk Banner */}
        <div
          style={{
            background: deadlineText ? "#FEF3C7" : "#F3F4F6",
            border: `1px solid ${deadlineText ? "#FCD34D" : "#E5E7EB"}`,
            borderRadius: "var(--radius-lg)",
            padding: 12,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <AlertTriangle size={16} color={deadlineText ? "#D97706" : "var(--text-muted)"} />
          <span style={{ fontSize: 13, fontWeight: 500, color: deadlineText ? "#92400E" : "var(--text-secondary)" }}>
            {deadlineText ? `Hard Deadline Found: ${deadlineText}` : "No hard deadline identified"}
          </span>
        </div>

        {/* Render raw output formatted neatly */}
        <div style={{ whiteSpace: "pre-wrap", fontSize: 13, lineHeight: 1.6, color: "var(--text-primary)" }}>
          {text}
        </div>

        {/* Quick Actions Panel */}
        <div style={{ borderTop: "1px solid var(--border)", paddingTop: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          <h4 style={{ margin: 0, fontSize: 13, fontWeight: 600 }}>Suggested Actions</h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                onClose();
                navigate("/compliance/controls");
              }}
              style={{ display: "flex", alignItems: "center", gap: 4 }}
            >
              Update Existing Controls <ArrowRight size={12} />
            </button>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                onClose();
                navigate("/compliance/gaps");
              }}
              style={{ display: "flex", alignItems: "center", gap: 4 }}
            >
              Create Control Assignment <ArrowRight size={12} />
            </button>
          </div>
        </div>

        <div style={{ fontSize: 11, color: "var(--muted)", fontStyle: "italic", marginTop: 8 }}>
          Based on ComplySense knowledge base (DPDP Act 2023, ISO 27001:2022, etc.). Verify critical regulatory interpretations with your legal team.
        </div>
      </div>
    );
  };

  return (
    <AIPanel
      open={open}
      onClose={onClose}
      title="Regulatory Change Analysis"
      loading={loading}
      error={error}
      onRetry={handleAnalyze}
      hasResult={!!result}
      emptyTitle="Analyze Regulation Text"
      emptyDescription="Paste the text of a new regulation, amendment, or government circular to run a gap impact analysis."
      emptyActionLabel="Analyze Gap Impact"
      onEmptyAction={circularText.trim().length >= 200 ? handleAnalyze : undefined}
      lastRunAt={lastRunAt}
      onRegenerate={handleAnalyze}
      regenerateLoading={loading}
    >
      {!result ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 12, width: "100%" }}>
          <label style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>
            Paste regulation text or amendment
          </label>
          <textarea
            style={{
              width: "100%",
              minHeight: 180,
              padding: 10,
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border)",
              background: "var(--surface)",
              color: "var(--text-primary)",
              fontFamily: "var(--font-sans)",
              fontSize: 13,
              resize: "vertical",
            }}
            placeholder="Paste the text of a new regulation, amendment, or government circular... (min 200 chars)"
            value={circularText}
            onChange={(e) => setCircularText(e.target.value)}
            maxLength={3000}
          />
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--muted)" }}>
            <span>Minimum 200 characters</span>
            <span>{circularText.length} / 3000</span>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={circularText.trim().length < 200 || loading}
            style={{ alignSelf: "flex-end", marginTop: 8, display: "flex", alignItems: "center", gap: 6 }}
          >
            <Sparkles size={14} />
            {loading ? "Analyzing..." : "Analyze Gap Impact"}
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--success)", display: "flex", alignItems: "center", gap: 4 }}>
              <CheckCircle size={14} /> Analysis Complete
            </span>
            <button className="btn btn-ghost btn-sm" onClick={handleReset} style={{ fontSize: 11 }}>
              Start Over
            </button>
          </div>
          {renderSections()}
        </div>
      )}
    </AIPanel>
  );
}
