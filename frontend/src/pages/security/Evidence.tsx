// Use: Technical evidence upload dashboard for server logs and scan files.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

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
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get<EvidenceItem[]>("/api/v1/evidence");
    return Array.isArray(res.data) ? res.data : res.data?.evidence ?? [];
  }, []);

  useEffect(() => {
    if (!data) return;
    setItems(data as EvidenceItem[]);
  }, [data]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) return;
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("control_id", controlId);
      formData.append("description", description);
      await api.post("/api/v1/evidence", formData, { headers: { "Content-Type": "multipart/form-data" } });
      setFile(null);
      setDescription("");
      setControlId("");
      await refetch();
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
      // eslint-disable-next-line no-console
      console.error("Download failed", err);
      alert("Failed to download file.");
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="page-panel">
      <PageShell title="Technical Evidence Upload" context="Security evidence submission for controls and investigations." />
      <div style={{ display: "grid", gridTemplateColumns: "0.9fr 1.1fr", gap: 16, marginTop: 16 }}>
        <form onSubmit={handleSubmit} style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Upload Evidence</h3>
          <label style={{ display: "block", marginBottom: 8 }}>
            Control ID
            <input value={controlId} onChange={(event) => setControlId(event.target.value)} style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
          <label style={{ display: "block", marginBottom: 8 }}>
            Description
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={4} style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
          <input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <div style={{ marginTop: 12 }}>
            <button type="submit" disabled={submitting} style={{ padding: "10px 14px", borderRadius: 8, border: 0, background: "#2563eb", color: "#fff" }}>{submitting ? "Uploading…" : "Upload"}</button>
          </div>
        </form>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Recent Evidence</h3>
          {loading ? (
            <Loading />
          ) : error ? (
            <ErrorState message={error.message} onRetry={() => void refetch()} />
          ) : items.length === 0 ? (
            <EmptyState title="No evidence" description="No evidence uploaded yet." />
          ) : (
            items.map((item) => (
              <div key={item.evidence_id} style={{ borderTop: "1px solid #f3f4f6", padding: "8px 0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{item.file_name}</div>
                    <div style={{ fontSize: 12, color: "#6b7280" }}>{item.description || "No description"}</div>
                    <div style={{ fontSize: 12, color: "#6b7280" }}>{item.approval_status} • {item.uploaded_at ? new Date(item.uploaded_at).toLocaleString() : "—"}</div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <button onClick={() => void handleDownload(item.evidence_id, item.file_name)} disabled={downloadingId === item.evidence_id}>{downloadingId === item.evidence_id ? "Downloading…" : "Download"}</button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
