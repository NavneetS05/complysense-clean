// Use: AIPanel — right-side drawer for AI-powered results, loading skeletons, and error states.

import { X, RefreshCw, Bot } from "lucide-react";

interface AIPanelProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  footer?: React.ReactNode;
  children: React.ReactNode;
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
}: AIPanelProps) {
  if (!open) return null;

  return (
    <>
      <div className="ai-drawer-overlay" onClick={onClose} />
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
              <Bot size={14} color="white" />
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
                background: "#FEF2F2",
                border: "1px solid #FECACA",
                borderRadius: "var(--radius-lg)",
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              <div style={{ fontSize: 13, color: "var(--critical)", fontWeight: 500 }}>
                {error}
              </div>
              {onRetry && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={onRetry}
                  style={{ alignSelf: "flex-start" }}
                >
                  <RefreshCw size={12} /> Retry
                </button>
              )}
            </div>
          ) : (
            children
          )}
        </div>

        {/* Footer */}
        {footer && <div className="ai-drawer-footer">{footer}</div>}
      </div>
    </>
  );
}

function AIPanelSkeleton() {
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
    </div>
  );
}
