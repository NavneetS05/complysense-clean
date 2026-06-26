// Use: Detail view for a single control, assignees, linked evidence, and audit logs.

import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../lib/api";

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
  const { id } = useParams();
  const [control, setControl] = useState<ControlDetailData | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [noteText, setNoteText] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!id) return;
      try {
        const [{ data: detail }, { data: evidenceData }] = await Promise.all([
          api.get(`/api/v1/controls/${id}`),
          api.get(`/api/v1/evidence`),
        ]);
        setControl(detail);
        setEvidence((Array.isArray(evidenceData) ? evidenceData : []).filter((item: EvidenceItem) => item.file_name));
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [id]);

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
      const { data } = await api.patch(`/api/v1/controls/${id}/notes`, { note: noteText.trim() });
      setControl((current) => current ? { ...current, notes: data.notes } : current);
      setNoteText("");
    } catch {
      // swallow for now
    }
  };

  if (loading) return <div className="page-panel"><h2>Control Detail</h2><p>Loading control details…</p></div>;

  return (
    <div className="page-panel">
      <h2>{control?.control_id ?? "Control Detail"}</h2>
      <p>{control?.framework_name ?? "Assigned control"}</p>
      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 0.7fr", gap: 16, marginTop: 16 }}>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ fontSize: 12, color: "var(--muted)" }}>Status</div>
          <div style={{ fontWeight: 700, marginTop: 4 }}>{control?.status ?? "unknown"}</div>
          {dueBadge ? <div style={{ marginTop: 8, color: "var(--muted)" }}>{dueBadge}</div> : null}
          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: 12, color: "var(--muted)" }}>Assigned to</div>
            <div>{control?.assigned_name ?? "Unassigned"}</div>
          </div>
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 12, color: "var(--muted)" }}>Department</div>
            <div>{control?.department_name ?? "—"}</div>
          </div>
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 12, color: "var(--muted)" }}>Assigned by</div>
            <div>{control?.assigned_by_name ?? "—"}</div>
          </div>
          <div style={{ marginTop: 16 }}>
            <h3 style={{ marginBottom: 8 }}>Evidence Documents</h3>
            {evidence.length === 0 ? <p>No evidence uploaded yet.</p> : (
              <ul style={{ paddingLeft: 18 }}>
                {evidence.map((item) => (
                  <li key={item.evidence_id} style={{ marginBottom: 6 }}>
                    <strong>{item.file_name}</strong> — {item.approval_status}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="card" style={{ padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Notes</h3>
          <textarea value={noteText} onChange={(event) => setNoteText(event.target.value)} rows={4} style={{ width: "100%", padding: 8 }} />
          <button onClick={addNote} style={{ marginTop: 8 }}>Add Note</button>
          <pre style={{ whiteSpace: "pre-wrap", marginTop: 12, fontSize: 12 }}>{control?.notes ?? "No notes yet."}</pre>
        </div>
      </div>
    </div>
  );
}
