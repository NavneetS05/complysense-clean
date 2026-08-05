// Use: AIPanel — right-side drawer for AI-powered results, loading skeletons, empty/not-run states, and error handling.

import { useEffect, useState } from "react";
import { X, RefreshCw, Sparkles, AlertCircle } from "lucide-react";

interface AIPanelProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  footer?: React.ReactNode;
  children: React.ReactNode;
  
  // Specs additions
  hasResult?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyActionLabel?: string;
  onEmptyAction?: () => void;
  lastRunAt?: string | null;
  onRegenerate?: () => void;
  regenerateLoading?: boolean;
}

export function AIPanel({
  open,
  onClose,
  title = "AI Assistant",
  loading = false,
  error = null,
  onRetry,
  footer,
  children,
  
  hasResult = false,
  emptyTitle = "Run AI Assistant",
  emptyDescription = "Trigger AI to analyze context and generate results.",
  emptyActionLabel = "Run AI",
  onEmptyAction,
  lastRunAt = null,
  onRegenerate,
  regenerateLoading = false,
}: AIPanelProps) {
  if (!open) return null;

  return (
    <>
      {/* Overlay - clicking outside does NOT close it per spec */}
      <div className="ai-drawer-overlay" />
      <div className="ai-drawer" role="dialog" aria-label={title} aria-modal="true">
        {/* Header */}
        <div className="ai-drawer-header">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                width: 28,
                height: 28,
                background: "linear-gradient(135deg, #2563EB, #7C3AED)",
                borderRadius: "var(--radius-md)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Sparkles size={14} color="white" />
            </div>
            <span className="ai-drawer-title">{title}</span>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close AI panel">
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="ai-drawer-body">
          {loading ? (
            <AIPanelSkeleton />
          ) : error ? (
            <div
              style={{
                textAlign: "center",
                padding: "32px 16px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 16,
              }}
            >
              <AlertCircle size={36} color="var(--critical)" />
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                Failed to generate response
              </div>
              <div style={{ fontSize: 13, color: "var(--muted)", maxWidth: 300 }}>
                {error}
              </div>
              <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
                {onRetry && (
                  <button className="btn btn-primary btn-sm" onClick={onRetry}>
                    <RefreshCw size={12} style={{ marginRight: 4 }} /> Retry
                  </button>
                )}
                <a
                  href="mailto:support@complysense.com"
                  className="btn btn-secondary btn-sm"
                  style={{ textDecoration: "none", display: "inline-flex", alignItems: "center" }}
                >
                  Report Issue
                </a>
              </div>
            </div>
          ) : !hasResult ? (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                textAlign: "center",
                padding: "32px 16px",
                gap: 16,
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  background: "var(--primary-bg)",
                  color: "var(--primary)",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Sparkles size={24} />
              </div>
              <div style={{ fontWeight: 600, fontSize: 16 }}>{emptyTitle}</div>
              <div style={{ fontSize: 13, color: "var(--muted)", maxWidth: 280 }}>
                {emptyDescription}
              </div>
              {onEmptyAction && (
                <button
                  className="btn btn-primary"
                  onClick={onEmptyAction}
                  style={{ marginTop: 8 }}
                >
                  {emptyActionLabel}
                </button>
              )}
            </div>
          ) : (
            children
          )}
        </div>

        {/* Footer */}
        {(footer || onRegenerate || lastRunAt) && (
          <div className="ai-drawer-footer" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {footer}
            
            {(onRegenerate || lastRunAt) && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  width: "100%",
                  borderTop: footer ? "1px solid var(--border)" : "none",
                  paddingTop: footer ? 12 : 0,
                }}
              >
                <span style={{ fontSize: 11, color: "var(--muted)" }}>
                  {lastRunAt ? `Last run: ${lastRunAt}` : ""}
                </span>
                {onRegenerate && hasResult && !loading && (
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={onRegenerate}
                    disabled={regenerateLoading}
                    style={{ fontSize: 12, padding: "4px 8px" }}
                  >
                    <RefreshCw
                      size={12}
                      style={{ marginRight: 4 }}
                      className={regenerateLoading ? "spin" : ""}
                    />
                    {regenerateLoading ? "Regenerating..." : "Regenerate"}
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

function AIPanelSkeleton() {
  const [statusMessage, setStatusMessage] = useState("Reviewing input...");
  
  useEffect(() => {
    const messages = [
      "Reviewing input...",
      "Checking regulatory frameworks...",
      "Preparing response..."
    ];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % messages.length;
      setStatusMessage(messages[idx]);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {[85, 65, 90].map((w, i) => (
        <div key={i} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div
            className="skeleton-cell"
            style={{ width: "40%", height: 12, borderRadius: 4 }}
          />
          <div
            className="skeleton-cell"
            style={{ width: `${w}%`, height: 48, borderRadius: 6 }}
          />
        </div>
      ))}
      <div
        style={{
          marginTop: 16,
          fontSize: 12,
          color: "var(--muted)",
          textAlign: "center",
          fontStyle: "italic",
        }}
      >
        {statusMessage}
      </div>
    </div>
  );
}
