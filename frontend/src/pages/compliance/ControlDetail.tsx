// Use: Detail view for a single control, assignees, linked evidence, and audit logs.

import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import { useToast } from "../../components/shared/ToastContext";
import { PageShell } from "../../components/shared/PageShell";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";

type ControlDetailData = {
  assignment_id: string;
  control_id: string;
  framework_name: string;
  status: string;
  due_date?: string;
  notes?: string;
  assigned_name?: string;
  assigned_by_name?: string;
  department_name?: string;
};

type EvidenceItem = {
  evidence_id: string;
  file_name: string;
  approval_status: string;
  uploaded_at?: string;
};

export default function ControlDetail() {
  const toast = useToast();
  const { id } = useParams();
  const [noteText, setNoteText] = useState("");

  const { data: control, loading: loadingControl, error: controlError, refetch: refetchControl } = useApi<ControlDetailData | null>(async () => {
    if (!id) return null;
    const res = await api.get(`/api/v1/controls/${id}`);
    return res.data as ControlDetailData;
  }, [id]);

  const { data: evidenceData, loading: loadingEvidence } = useApi<EvidenceItem[]>(async () => {
    const res = await api.get<EvidenceItem[] | { evidence?: EvidenceItem[] }>(`/api/v1/evidence`);
    const arr = Array.isArray(res.data) ? res.data : res.data?.evidence ?? [];
    return arr.filter((item) => item.file_name);
  }, [id]);

  const evidence: EvidenceItem[] = evidenceData ?? [];

  const dueBadge = useMemo(() => {
    if (!control?.due_date) return null;
    const due = new Date(control.due_date);
    const diff = Math.ceil((due.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (diff < 0) return `Overdue by ${Math.abs(diff)} day(s)`;
    if (diff === 0) return "Due today";
    return `${diff} day(s) remaining`;
  }, [control]);

  const addNote = async () => {
    if (!id || !noteText.trim()) return;
    try {
      await api.patch(`/api/v1/controls/${id}/notes`, { note: noteText.trim() });
      await refetchControl();
      setNoteText("");
    } catch {
      // swallow for now
    }
  };

  const handleDownload = async (evidenceId: string, filename?: string) => {
    try {
      const res = await api.get(`/api/v1/evidence/${evidenceId}/download`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data as Blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || "evidence.bin";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      // simple feedback; could be improved
      toast.error("Failed to download file.");
    }
  };
  if (loadingControl || loadingEvidence) return (
    <PageShell title="Control Detail">
      <div className="page-panel"><Loading /></div>
    </PageShell>
  );

  if (controlError) return (
    <PageShell title="Control Detail">
      <div className="page-panel"><ErrorState message={controlError.message} onRetry={() => void refetchControl()} /></div>
    </PageShell>
  );

  return (
    <PageShell title={control?.control_id ?? "Control Detail"} subtitle={control?.framework_name ?? "Assigned control"}>
      <div className="page-panel">
        <div className="control-detail-grid">
          <section className="card control-detail-summary">
            <div className="detail-row">
              <span className="detail-label">Status</span>
              <span className="detail-value">{control?.status ?? "Unknown"}</span>
            </div>
            {dueBadge && (
              <div className="detail-row">
                <span className="detail-label">Due</span>
                <span className="detail-value muted">{dueBadge}</span>
              </div>
            )}
            <div className="divider" />
            <div className="detail-row">
              <span className="detail-label">Assigned to</span>
              <span className="detail-value">{control?.assigned_name ?? "Unassigned"}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Department</span>
              <span className="detail-value">{control?.department_name ?? "—"}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Assigned by</span>
              <span className="detail-value">{control?.assigned_by_name ?? "—"}</span>
            </div>
            <div className="section-block">
              <h3>Evidence Documents</h3>
              {evidence.length === 0 ? (
                <p className="muted">No evidence uploaded yet.</p>
              ) : (
                <ul className="evidence-list">
                  {evidence.map((item) => (
                    <li key={item.evidence_id} className="evidence-item">
                      <div>
                        <strong>{item.file_name}</strong>
                        <div className="muted small">{item.approval_status}</div>
                      </div>
                      <button className="btn btn-secondary btn-sm" onClick={() => void handleDownload(item.evidence_id, item.file_name)}>
                        Download
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <section className="card control-detail-notes">
            <div className="section-block">
              <h3>Notes</h3>
              <textarea
                className="form-textarea"
                value={noteText}
                onChange={(event) => setNoteText(event.target.value)}
                rows={5}
                placeholder="Add a note or update status details..."
              />
              <button className="btn btn-primary btn-sm" onClick={addNote} style={{ marginTop: 10 }}>
                Add Note
              </button>
            </div>
            <div className="section-block">
              <h4>Latest notes</h4>
              <pre className="notes-panel">{control?.notes ?? "No notes yet."}</pre>
            </div>
          </section>
        </div>
      </div>
    </PageShell>
  );
}
