// Use: Audit workspace for assessing controls, uploaded evidence, and adding findings.

import { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import Loading from "../../components/shared/Loading";

type Assessment = {
  assessment_id: string;
  assessment_name: string;
  framework_name?: string;
  assessment_status?: string;
  created_at?: string;
};

type ControlItem = {
  control_id: string;
  control_title?: string;
  title?: string;
  framework_name?: string;
  status?: string;
  description?: string;
};

type EvidenceItem = {
  evidence_id: string;
  control_id?: string;
  file_name?: string;
  approval_status?: string;
  uploaded_at?: string;
  description?: string;
  uploaded_by?: string;
};

type ObservationItem = {
  observation_id: string;
  assessment_id?: string;
  control_id?: string;
  evidence_id?: string;
  evidence_file?: string;
  observation_text: string;
  severity: string;
  status: string;
  created_at?: string;
  added_by_name?: string;
};

export default function Workspace() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [controls, setControls] = useState<ControlItem[]>([]);
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([]);
  const [observations, setObservations] = useState<ObservationItem[]>([]);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState("");
  const [selectedControlId, setSelectedControlId] = useState("");
  const [priorityEvidenceIds, setPriorityEvidenceIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [smartLoading, setSmartLoading] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);
  const [draft, setDraft] = useState({ control_id: "", evidence_id: "", observation_text: "", severity: "observation" });
  const [submitting, setSubmitting] = useState(false);
  const { data, error: bulkError } = useApi(async () => {
    const [assessmentsRes, controlsRes, evidenceRes, observationsRes] = await Promise.all([
      api.get("/api/v1/assessments"),
      api.get("/api/v1/controls"),
      api.get("/api/v1/evidence"),
      api.get("/api/v1/audit/observations"),
    ]);

    const assessmentData = Array.isArray(assessmentsRes.data) ? assessmentsRes.data : assessmentsRes.data?.assessments ?? [];
    const controlData = Array.isArray(controlsRes.data) ? controlsRes.data : controlsRes.data?.controls ?? [];
    const evidenceData = Array.isArray(evidenceRes.data) ? evidenceRes.data : evidenceRes.data?.evidence ?? [];
    const observationData = Array.isArray(observationsRes.data) ? observationsRes.data : observationsRes.data?.observations ?? [];

    return { assessmentData, controlData, evidenceData, observationData };
  }, []);

  useEffect(() => {
    if (!data) return;
    setAssessments(data.assessmentData as Assessment[]);
    setControls(data.controlData as ControlItem[]);
    setEvidenceItems(data.evidenceData as EvidenceItem[]);
    setObservations(data.observationData as ObservationItem[]);

    const firstAssessment = (data.assessmentData as Assessment[]).find((item) => item.assessment_status === "in_progress" || item.assessment_status === "completed");
    const initialAssessmentId = firstAssessment?.assessment_id ?? "";
    setSelectedAssessmentId((current) => current || initialAssessmentId);
    setLoading(false);
  }, [data]);

  useEffect(() => {
    if (bulkError) setLoading(false);
  }, [bulkError]);

  useEffect(() => {
    if (!controls.length) {
      return;
    }
    if (!selectedControlId || !controls.some((item) => item.control_id === selectedControlId)) {
      setSelectedControlId(controls[0].control_id);
    }
    if (!draft.control_id && controls[0]) {
      setDraft((current) => ({ ...current, control_id: controls[0].control_id }));
    }
  }, [controls, selectedControlId, draft.control_id]);

  const selectedControl = useMemo(
    () => controls.find((item) => item.control_id === selectedControlId) ?? controls[0],
    [controls, selectedControlId],
  );

  const selectedEvidence = useMemo(
    () => evidenceItems.filter((item) => item.control_id === selectedControl?.control_id),
    [evidenceItems, selectedControl],
  );

  const selectedObservations = useMemo(
    () => observations.filter((item) => item.control_id === selectedControl?.control_id),
    [observations, selectedControl],
  );

  async function handleSmartSample() {
    if (!selectedAssessmentId) {
      return;
    }
    setSmartLoading(true);
    try {
      const { data } = await api.post("/api/v1/ai/audit/smart-sample", { assessment_id: selectedAssessmentId });
      setPriorityEvidenceIds(Array.isArray(data) ? data.map((item: { evidence_id: string }) => item.evidence_id) : []);
    } finally {
      setSmartLoading(false);
    }
  }

  async function handleDraftObservation() {
    setDraftLoading(true);
    try {
      const { data } = await api.post("/api/v1/ai/audit/draft-observation", {
        control_id: draft.control_id || selectedControl?.control_id,
        partial_text: draft.observation_text,
      });
      setDraft((current) => ({ ...current, observation_text: data.response ?? current.observation_text }));
    } finally {
      setDraftLoading(false);
    }
  }

  async function handleAddObservation(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      const body = {
        assessment_id: selectedAssessmentId,
        control_id: draft.control_id || selectedControl?.control_id,
        evidence_id: draft.evidence_id || undefined,
        observation_text: draft.observation_text.trim(),
        severity: draft.severity,
      };
      const { data } = await api.post("/api/v1/audit/observations", body);
      const fresh = {
        observation_id: data.observation_id,
        assessment_id: selectedAssessmentId,
        control_id: body.control_id,
        evidence_id: body.evidence_id,
        evidence_file: draft.evidence_id ? selectedEvidence.find((item) => item.evidence_id === draft.evidence_id)?.file_name : undefined,
        observation_text: body.observation_text,
        severity: body.severity,
        status: "open",
        created_at: new Date().toISOString(),
        added_by_name: "You",
      } as ObservationItem;
      setObservations((current) => [fresh, ...current]);
      setDraft({ control_id: body.control_id, evidence_id: "", observation_text: "", severity: body.severity });
      setPriorityEvidenceIds((current) => current);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "#f8fafc" }}>
      <div style={{ padding: "16px 20px", borderBottom: "1px solid #e2e8f0", background: "white", position: "sticky", top: 0, zIndex: 2 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div>
            <h2 style={{ margin: 0 }}>Audit Workspace</h2>
            <p style={{ margin: "4px 0 0", color: "#475569" }}>Review controls and evidence, then log findings for the selected assessment.</p>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <select value={selectedAssessmentId} onChange={(event) => setSelectedAssessmentId(event.target.value)} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }}>
              {assessments.map((assessment) => (
                <option key={assessment.assessment_id} value={assessment.assessment_id}>
                  {assessment.assessment_name} — {assessment.framework_name || "Framework"} — {assessment.assessment_status}
                </option>
              ))}
            </select>
            <button onClick={handleSmartSample} disabled={smartLoading || !selectedAssessmentId} style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #f59e0b", background: "#fffbeb", color: "#92400e", cursor: smartLoading ? "wait" : "pointer" }}>
              {smartLoading ? "Analyzing risk..." : "AI: Smart Sample"}
            </button>
          </div>
        </div>
        {!loading && selectedAssessmentId && (
          <div style={{ marginTop: 10, color: "#334155", fontSize: 13 }}>
            {controls.length} controls • {evidenceItems.length} evidence items • {observations.length} observations
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(240px, 28%) minmax(320px, 46%) minmax(280px, 26%)", gap: 12, padding: 16, flex: 1, minHeight: 0 }}>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div style={{ padding: 12, borderBottom: "1px solid #e2e8f0", fontWeight: 700 }}>Controls ({controls.length})</div>
          <div style={{ padding: 12, overflowY: "auto" }}>
            {loading ? <Loading /> : controls.map((control) => (
              <button key={control.control_id} onClick={() => { setSelectedControlId(control.control_id); setDraft((current) => ({ ...current, control_id: control.control_id })); }} style={{ width: "100%", textAlign: "left", border: selectedControl?.control_id === control.control_id ? "1px solid #2563eb" : "1px solid #e2e8f0", borderRadius: 10, padding: 10, marginBottom: 8, background: selectedControl?.control_id === control.control_id ? "#eff6ff" : "white", cursor: "pointer" }}>
                <div style={{ fontWeight: 700, fontSize: 13 }}>{control.control_id}</div>
                <div style={{ fontSize: 13, color: "#334155", marginTop: 4 }}>{control.control_title || control.title || "Untitled control"}</div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#64748b", marginTop: 6 }}>
                  <span>{control.framework_name || "Framework"}</span>
                  <span>{selectedEvidence.filter((item) => item.control_id === control.control_id).length} files</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div style={{ padding: 12, borderBottom: "1px solid #e2e8f0", fontWeight: 700 }}>
            {selectedControl ? `${selectedControl.control_id} — ${selectedControl.control_title || selectedControl.title || "Control"}` : "Evidence Viewer"}
          </div>
          <div style={{ padding: 12, overflowY: "auto" }}>
            {!selectedControl ? <p>Select a control to inspect evidence.</p> : (
              <>
                <div style={{ marginBottom: 12, color: "#475569", fontSize: 14 }}>{selectedControl.description || "No control description available yet."}</div>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>Evidence ({selectedEvidence.length})</div>
                {selectedEvidence.length === 0 ? <div style={{ border: "1px dashed #f59e0b", borderRadius: 10, padding: 12, background: "#fffbeb", color: "#92400e" }}>No evidence uploaded for this control.</div> : selectedEvidence.map((item) => (
                  <div key={item.evidence_id} style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 10, marginBottom: 10, background: priorityEvidenceIds.includes(item.evidence_id) ? "#fffbeb" : "#fff" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                      <strong>{item.file_name || "Evidence file"}</strong>
                      {priorityEvidenceIds.includes(item.evidence_id) ? <span style={{ background: "#fef3c7", color: "#92400e", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}>★ Priority</span> : null}
                    </div>
                    <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>{item.description || "No description provided."}</div>
                    <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>Status: {item.approval_status || "pending"}</div>
                    <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
                      <button onClick={() => setDraft((current) => ({ ...current, control_id: selectedControl.control_id, evidence_id: item.evidence_id }))} style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #2563eb", background: "white", color: "#2563eb" }}>Add Observation →</button>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>

        <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div style={{ padding: 12, borderBottom: "1px solid #e2e8f0", fontWeight: 700 }}>Observations</div>
          <div style={{ padding: 12, overflowY: "auto" }}>
            <div style={{ marginBottom: 12 }}>
              {selectedObservations.length === 0 ? <p style={{ margin: 0, color: "#64748b" }}>No observations yet for this control.</p> : selectedObservations.map((item) => (
                <div key={item.observation_id} style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 8, marginBottom: 8 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: item.severity === "finding" ? "#dc2626" : item.severity === "recommendation" ? "#d97706" : "#2563eb" }}>{item.severity}</div>
                  <div style={{ marginTop: 4, fontSize: 13 }}>{item.observation_text}</div>
                  <div style={{ marginTop: 6, fontSize: 12, color: "#64748b" }}>{item.status} • {item.added_by_name || "Auditor"}</div>
                </div>
              ))}
            </div>
            <form onSubmit={handleAddObservation} style={{ borderTop: "1px solid #e2e8f0", paddingTop: 12 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>Add Observation</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 8 }}>
                {draft.control_id ? <span style={{ background: "#eff6ff", color: "#1d4ed8", padding: "4px 8px", borderRadius: 999, fontSize: 12 }}>Control: {draft.control_id}</span> : null}
                {draft.evidence_id ? <span style={{ background: "#f5f3ff", color: "#6d28d9", padding: "4px 8px", borderRadius: 999, fontSize: 12 }}>Evidence: {draft.evidence_id}</span> : null}
              </div>
              <div style={{ marginBottom: 8 }}>
                <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Type</label>
                <div style={{ display: "flex", gap: 8 }}>
                  {(["finding", "observation", "recommendation"] as const).map((option) => (
                    <label key={option} style={{ fontSize: 13 }}>
                      <input type="radio" name="severity" checked={draft.severity === option} onChange={() => setDraft((current) => ({ ...current, severity: option }))} /> {option}
                    </label>
                  ))}
                </div>
              </div>
              <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Observation Text</label>
              <textarea value={draft.observation_text} onChange={(event) => setDraft((current) => ({ ...current, observation_text: event.target.value }))} rows={5} style={{ width: "100%", borderRadius: 8, border: "1px solid #cbd5e1", padding: 8, resize: "vertical" }} placeholder="Describe the finding and reference the evidence or requirement." />
              <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                <button type="button" onClick={handleDraftObservation} disabled={draftLoading} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1", background: "white" }}>
                  {draftLoading ? "Drafting…" : "AI: Draft Observation"}
                </button>
                <button type="submit" disabled={submitting || draft.observation_text.trim().length < 10} style={{ padding: "8px 10px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", cursor: submitting ? "wait" : "pointer" }}>
                  {submitting ? "Saving…" : "Add Observation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
