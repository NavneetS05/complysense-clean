// Use: Technical evidence upload dashboard for server logs and scan files.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import { useToast } from "../../components/shared/ToastContext";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";
import { FileUpload } from "../../components/shared/FileUpload";
import { UploadPreviewPanel } from "../../components/shared/UploadPreviewPanel";
import { getApiErrorMessage } from "../../lib/errors";

interface EvidenceItem {
  evidence_id: string;
  file_name: string;
  approval_status: string;
  description?: string | null;
  uploaded_at?: string | null;
}

export default function Evidence() {
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [controlId, setControlId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  // Upload Progress Drawer States
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadPanelOpen, setUploadPanelOpen] = useState(false);

  const toast = useToast();

  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/evidence");
    const payload = res.data as EvidenceItem[] | { evidence?: EvidenceItem[] };
    return Array.isArray(payload) ? payload : payload.evidence ?? [];
  }, []);

  useEffect(() => {
    if (!data) return;
    setItems(data as EvidenceItem[]);
  }, [data]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) {
      toast.error("Please select a file first.");
      return;
    }
    setSubmitting(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadPanelOpen(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("control_id", controlId);
      formData.append("description", description);

      await api.post("/api/v1/evidence", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const pct = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            setUploadProgress(pct);
          }
        },
      });

      setFile(null);
      setDescription("");
      setControlId("");
      toast.success("Evidence uploaded successfully.");
      await refetch();
    } catch (err: unknown) {
      const msg = getApiErrorMessage(err, "Upload failed");
      setUploadError(msg);
      toast.error("Failed to upload evidence.");
    } finally {
      setSubmitting(false);
    }
  }

  const handleDownload = async (evidenceId: string, filename?: string) => {
    try {
      setDownloadingId(evidenceId);
      const res = await api.get(`/api/v1/evidence/${evidenceId}/download`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data as Blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || "evidence.bin";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed", err);
      toast.error("Failed to download file.");
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="page-panel">
      <PageShell title="Technical Evidence Upload" subtitle="Security evidence submission for controls and investigations." />
      <div style={{ display: "grid", gridTemplateColumns: "0.9fr 1.1fr", gap: 16, marginTop: 16 }}>
        <form onSubmit={handleSubmit} className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <h3 style={{ marginTop: 0, marginBottom: 4 }}>Upload Evidence</h3>
          
          <div className="form-group">
            <label className="form-label">Control ID</label>
            <input 
              value={controlId} 
              onChange={(event) => setControlId(event.target.value)} 
              className="form-input"
              placeholder="e.g. ISO-27001-A.12.1.1"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              value={description} 
              onChange={(event) => setDescription(event.target.value)} 
              rows={3} 
              className="form-textarea"
              placeholder="Describe the uploaded evidence..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Evidence Document</label>
            <FileUpload 
              onFile={(f) => setFile(f)} 
              disabled={submitting} 
              label="Drop evidence file here" 
            />
          </div>

          <div style={{ marginTop: 8 }}>
            <button 
              type="submit" 
              disabled={submitting || !file} 
              className="btn btn-primary"
              style={{ minWidth: 120 }}
            >
              {submitting ? "Uploading…" : "Upload"}
            </button>
          </div>
        </form>

        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <h3 style={{ marginTop: 0, marginBottom: 12 }}>Recent Evidence</h3>
          {loading ? (
            <Loading />
          ) : error ? (
            <ErrorState message={error.message} onRetry={() => void refetch()} />
          ) : items.length === 0 ? (
            <EmptyState title="No evidence" description="No evidence uploaded yet." />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8, overflowY: "auto", maxHeight: 450 }}>
              {items.map((item) => (
                <div key={item.evidence_id} style={{ borderTop: "1px solid var(--border)", paddingTop: 8, paddingBottom: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 13 }}>{item.file_name}</div>
                      <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{item.description || "No description"}</div>
                      <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                        <span className={`badge badge-${item.approval_status === "approved" ? "compliant" : item.approval_status === "rejected" ? "non_compliant" : "pending"}`}>
                          {item.approval_status}
                        </span>
                        {" • "}{item.uploaded_at ? new Date(item.uploaded_at).toLocaleString() : "—"}
                      </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center" }}>
                      <button 
                        className="btn btn-secondary btn-sm"
                        onClick={() => void handleDownload(item.evidence_id, item.file_name)} 
                        disabled={downloadingId === item.evidence_id}
                      >
                        {downloadingId === item.evidence_id ? "Downloading…" : "Download"}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <UploadPreviewPanel 
        file={file} 
        progress={uploadProgress} 
        open={uploadPanelOpen} 
        error={uploadError} 
        onClose={() => setUploadPanelOpen(false)} 
      />
    </div>
  );
}

