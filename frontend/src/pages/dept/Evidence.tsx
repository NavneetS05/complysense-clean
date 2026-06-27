// Use: Lists uploaded files and approval history for the department.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

type EvidenceItem = {
  evidence_id: string;
  file_name?: string;
  approval_status?: string;
  uploaded_at?: string;
  description?: string;
  control_id?: string;
};

export default function Evidence() {
  const [rows, setRows] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ control_id: "", assignment_id: "", description: "", file: null as File | null });
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    try {
      setError(null);
      const { data } = await api.get("/api/v1/evidence");
      setRows(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load evidence");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function handleUpload(event: React.FormEvent) {
    event.preventDefault();
    if (!form.file) {
      return;
    }
    setSubmitting(true);
    try {
      setError(null);
      const payload = new FormData();
      payload.append("file", form.file);
      payload.append("control_id", form.control_id);
      if (form.assignment_id) payload.append("assignment_id", form.assignment_id);
      if (form.description) payload.append("description", form.description);
      await api.post("/api/v1/evidence", payload);
      setForm({ control_id: "", assignment_id: "", description: "", file: null });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>Evidence Vault</h2>
        <p>Upload supporting evidence for control assignments and review status at a glance.</p>
      </div>
      {error ? <div style={{ color: "#b91c1c", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: 10 }}>{error}</div> : null}
      <form onSubmit={handleUpload} style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, display: "grid", gap: 12 }}>
        <h3 style={{ margin: 0 }}>Upload Evidence</h3>
        <input type="file" onChange={(event) => setForm((current) => ({ ...current, file: event.target.files?.[0] ?? null }))} required />
        <input value={form.control_id} onChange={(event) => setForm((current) => ({ ...current, control_id: event.target.value }))} placeholder="Control ID" required style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
        <input value={form.assignment_id} onChange={(event) => setForm((current) => ({ ...current, assignment_id: event.target.value }))} placeholder="Assignment ID (optional)" style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
        <textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} placeholder="Evidence description" rows={3} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
        <button type="submit" disabled={submitting} style={{ padding: "8px 12px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", width: 180 }}>{submitting ? "Uploading…" : "Upload Evidence"}</button>
      </form>
      {loading ? <p>Loading evidence…</p> : (
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", background: "#f8fafc" }}>
                <th style={{ padding: 10 }}>File</th>
                <th style={{ padding: 10 }}>Control</th>
                <th style={{ padding: 10 }}>Status</th>
                <th style={{ padding: 10 }}>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.evidence_id} style={{ borderTop: "1px solid #e2e8f0" }}>
                  <td style={{ padding: 10 }}>{row.file_name || "Evidence file"}</td>
                  <td style={{ padding: 10 }}>{row.control_id || "—"}</td>
                  <td style={{ padding: 10 }}>{row.approval_status || "pending"}</td>
                  <td style={{ padding: 10 }}>{row.uploaded_at ? new Date(row.uploaded_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
