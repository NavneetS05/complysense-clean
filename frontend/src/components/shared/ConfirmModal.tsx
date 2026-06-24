// Use: ConfirmModal — accessible alert dialog for destructive/confirmation actions.

import { AlertTriangle } from "lucide-react";

interface ConfirmModalProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  confirmVariant?: "default" | "destructive";
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmModal({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  confirmVariant = "default",
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-modal-title"
        aria-describedby="confirm-modal-desc"
      >
        <div className="modal-header" style={{ alignItems: "flex-start", gap: 14 }}>
          {confirmVariant === "destructive" && (
            <div
              style={{
                width: 40,
                height: 40,
                background: "#FEE2E2",
                borderRadius: "var(--radius-lg)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <AlertTriangle size={20} color="var(--critical)" />
            </div>
          )}
          <div>
            <div id="confirm-modal-title" className="modal-title">
              {title}
            </div>
            <p id="confirm-modal-desc" className="modal-description">
              {description}
            </p>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button
            className={`btn ${confirmVariant === "destructive" ? "btn-danger" : "btn-primary"}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading && <span className="btn-spinner" />}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
