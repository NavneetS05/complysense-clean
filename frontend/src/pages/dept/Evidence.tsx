// Use: Lists uploaded files and approval history for the department.

import { useEffect, useState, useMemo } from "react";
import { Download } from "lucide-react";
import { api } from "../../lib/api";
import { FileUpload } from "../../components/shared/FileUpload";
import { UploadPreviewPanel } from "../../components/shared/UploadPreviewPanel";
import { DataTable, Column } from "../../components/shared/DataTable";
import { useToast } from "../../components/shared/ToastContext";
import { PageShell } from "../../components/shared/PageShell";
import { getApiErrorMessage } from "../../lib/errors";

type EvidenceItem = {
  evidence_id: string;
  file_name?: string;
  approval_status?: string;
  uploaded_at?: string;
  description?: string;
  control_id?: string;
  [key: string]: unknown;
};

export default function Evidence() {
  const [rows, setRows] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ control_id: "", assignment_id: "", description: "", file: null as File | null });
  const [submitting, setSubmitting] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  // Filters
  const [filters, setFilters] = useState({ search: "", status: "" });

  // Upload progress states
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadPanelOpen, setUploadPanelOpen] = useState(false);

  const toast = useToast();

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
      toast.error("Please select a file first.");
      return;
    }
    setSubmitting(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadPanelOpen(true);
    try {
      setError(null);
      const payload = new FormData();
      payload.append("file", form.file);
      payload.append("control_id", form.control_id);
      if (form.assignment_id) payload.append("assignment_id", form.assignment_id);
      if (form.description) payload.append("description", form.description);

      await api.post("/api/v1/evidence", payload, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const pct = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            setUploadProgress(pct);
          }
        },
      });

      setForm({ control_id: "", assignment_id: "", description: "", file: null });
      toast.success("Evidence uploaded successfully.");
      await load();
    } catch (err: unknown) {
      const msg = getApiErrorMessage(err, "Upload failed");
      setUploadError(msg);
      setError(msg);
      toast.error("Failed to upload evidence.");
    } finally {
      setSubmitting(false);
    }
  }

  async function downloadEvidence(evidenceId: string, fileName: string) {
    setDownloading(evidenceId);
    try {
      const response = await api.get(`/api/v1/evidence/${evidenceId}/download`, { responseType: "blob" });
      const url = URL.createObjectURL(response.data);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = fileName;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to download evidence.");
    } finally {
      setDownloading(null);
    }
  }

  // Client-side search and filter
  const filteredRows = useMemo(() => {
    return rows.filter((row) => {
      const name = (row.file_name || "").toLowerCase();
      const searchMatch = !filters.search || name.includes(filters.search.toLowerCase());
      const statusMatch = !filters.status || row.approval_status === filters.status;
      return searchMatch && statusMatch;
    });
  }, [rows, filters]);

  const columns: Column<EvidenceItem>[] = [
    {
      key: "file_name",
      label: "File",
      sortable: true,
      render: (val, row) => (
        <div>
          <div style={{ fontWeight: 600 }}>{String(val || "Evidence file")}</div>
          {row.description && (
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
              {row.description}
            </div>
          )}
        </div>
      ),
    },
    {
      key: "control_id",
      label: "Control",
      sortable: true,
      render: (val) => <span className="font-mono">{String(val || "—")}</span>,
    },
    {
      key: "approval_status",
      label: "Status",
      sortable: true,
      render: (val) => {
        const status = String(val || "pending");
        return (
          <span className={`badge badge-${status === "approved" ? "compliant" : status === "rejected" ? "non_compliant" : "pending"}`}>
            {status}
          </span>
        );
      },
    },
    {
      key: "uploaded_at",
      label: "Uploaded",
      sortable: true,
      render: (val) => (val ? new Date(String(val)).toLocaleString() : "—"),
    },
    {
      key: "actions",
      label: "Actions",
      render: (_, row) => (
        <button
          className="btn btn-secondary btn-sm"
          disabled={downloading === row.evidence_id}
          onClick={() => void downloadEvidence(row.evidence_id, row.file_name || "evidence")}
        >
          {downloading === row.evidence_id ? "Downloading…" : <><Download size={14} style={{ marginRight: 4 }} /> Download</>}
        </button>
      ),
    },
  ];

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Evidence Vault" 
        subtitle="Upload supporting evidence for control assignments and review status at a glance." 
      />

      {error ? (
        <div style={{ color: "#b91c1c", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: 10 }}>
          {error}
        </div>
      ) : null}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16, alignItems: "start" }}>
        <form onSubmit={handleUpload} className="card" style={{ display: "grid", gap: 12 }}>
          <h3 style={{ margin: 0, marginBottom: 4 }}>Upload Evidence</h3>
          
          <div className="form-group">
            <label className="form-label">Evidence File</label>
            <FileUpload 
              onFile={(f) => setForm((current) => ({ ...current, file: f }))} 
              disabled={submitting}
              label="Drop evidence file here"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Control ID</label>
            <input 
              value={form.control_id} 
              onChange={(event) => setForm((current) => ({ ...current, control_id: event.target.value }))} 
              placeholder="e.g. ISO-27001-A.12.1.1" 
              required 
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Assignment ID (optional)</label>
            <input 
              value={form.assignment_id} 
              onChange={(event) => setForm((current) => ({ ...current, assignment_id: event.target.value }))} 
              placeholder="Assignment ID" 
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              value={form.description} 
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} 
              placeholder="Evidence description..." 
              rows={3} 
              className="form-textarea"
            />
          </div>

          <button 
            type="submit" 
            disabled={submitting || !form.file} 
            className="btn btn-primary"
            style={{ width: 180, marginTop: 8 }}
          >
            {submitting ? "Uploading…" : "Upload Evidence"}
          </button>
        </form>

        <div style={{ display: "grid", gap: 12 }}>
          <section className="card" style={{ display: "flex", gap: 12, padding: 12 }}>
            <input 
              className="form-input" 
              placeholder="Search by file name" 
              value={filters.search} 
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
            />
            <select 
              className="form-input" 
              value={filters.status} 
              onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
              style={{ minWidth: 140 }}
            >
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </section>

          <DataTable 
            columns={columns} 
            data={filteredRows} 
            loading={loading}
            emptyTitle="No evidence found"
            emptyDesc="There are no evidence documents matching your criteria."
            keyField="evidence_id"
            pageSize={10}
          />
        </div>
      </div>

      <UploadPreviewPanel 
        file={form.file} 
        progress={uploadProgress} 
        open={uploadPanelOpen} 
        error={uploadError} 
        onClose={() => setUploadPanelOpen(false)} 
      />
    </div>
  );
}

