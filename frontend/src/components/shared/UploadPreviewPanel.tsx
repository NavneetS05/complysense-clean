// Use: Slide-in panel displaying file upload details and progress bar.
import { File, FileText, FileSpreadsheet, FileArchive, X, AlertCircle } from "lucide-react";
import { useEffect } from "react";

interface UploadPreviewPanelProps {
  file: File | null;
  progress: number;
  open: boolean;
  error: string | null;
  onClose: () => void;
}

function FileTypeIcon({ name }: { name: string }) {
  const ext = name.split(".").pop()?.toLowerCase();
  const iconSize = 40;
  if (ext === "pdf") {
    return <FileText size={iconSize} color="#EF4444" />;
  }
  if (["xls", "xlsx", "csv"].includes(ext || "")) {
    return <FileSpreadsheet size={iconSize} color="#10B981" />;
  }
  if (["zip", "rar", "tar", "gz"].includes(ext || "")) {
    return <FileArchive size={iconSize} color="#F59E0B" />;
  }
  if (["jpg", "jpeg", "png", "gif", "webp"].includes(ext || "")) {
    return <File size={iconSize} color="#3B82F6" />;
  }
  return <File size={iconSize} color="#6B7280" />;
}

export function UploadPreviewPanel({
  file,
  progress,
  open,
  error,
  onClose,
}: UploadPreviewPanelProps) {
  useEffect(() => {
    if (progress === 100 && open && !error) {
      const timer = setTimeout(() => {
        onClose();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [progress, open, error, onClose]);

  if (!open || !file) return null;

  const sizeLabel =
    file.size > 1024 * 1024
      ? `${(file.size / 1024 / 1024).toFixed(1)} MB`
      : `${(file.size / 1024).toFixed(0)} KB`;

  return (
    <>
      <div className="ai-drawer-overlay" onClick={onClose} />
      <div className="ai-drawer" role="dialog" aria-modal="true" aria-label="Upload Progress">
        <div className="ai-drawer-header">
          <span className="ai-drawer-title">Uploading File</span>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--text-secondary)",
              display: "flex",
            }}
            aria-label="Close panel"
          >
            <X size={18} />
          </button>
        </div>

        <div className="ai-drawer-body" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              background: "var(--surface-secondary)",
              padding: 16,
              borderRadius: "var(--radius-lg)",
              border: "1px solid var(--border)",
            }}
          >
            <FileTypeIcon name={file.name} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  fontWeight: 600,
                  fontSize: 14,
                  color: "var(--text-primary)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {file.name}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{sizeLabel}</div>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, fontWeight: 500 }}>
              <span>{error ? "Upload failed" : progress === 100 ? "Processing..." : "Uploading..."}</span>
              <span>{progress}%</span>
            </div>

            <div className="progress-bar-wrapper">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${progress}%`,
                  background: error ? "var(--critical)" : "var(--primary)",
                }}
              />
            </div>
          </div>

          {error && (
            <div
              className="inline-error"
              style={{
                background: "#FEF2F2",
                border: "1px solid #FECACA",
                borderRadius: "var(--radius-md)",
                padding: 12,
                color: "#B91C1C",
                display: "flex",
                alignItems: "flex-start",
                gap: 8,
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
              <div style={{ fontSize: 13, fontWeight: 500 }}>{error}</div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
