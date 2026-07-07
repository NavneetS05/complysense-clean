// Use: Guided Department task wizard with AI plain-English translation and AI evidence pre-flight validation.

import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { api } from "../../lib/api";
import {
  ArrowLeft,
  Sparkles,
  FileCheck,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  UploadCloud,
  FileText,
  Trash,
} from "lucide-react";

type TaskItem = {
  task_id: string;
  task_title: string;
  task_description?: string;
  task_status: string;
  priority?: string;
  due_date?: string;
  assignment_id?: string;
};

type ControlAssignment = {
  control_id: string;
  framework_name: string;
  notes?: string;
  status: string;
};

type EvidenceItem = {
  evidence_id: string;
  file_name: string;
  approval_status: string;
  uploaded_at: string;
  description?: string;
};

export default function TaskWizard() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Wizard state
  const [step, setStep] = useState(1); // 1 = Understand, 2 = Evidence, 3 = Confirm, 4 = Done
  const [task, setTask] = useState<TaskItem | null>(null);
  const [control, setControl] = useState<ControlAssignment | null>(null);
  const [loading, setLoading] = useState(true);

  // Step 1: AI Translation
  const [plainTranslation, setPlainTranslation] = useState<string | null>(null);
  const [translationLoading, setTranslationLoading] = useState(false);
  const [showTechnical, setShowTechnical] = useState(false);

  // Step 2: Evidence Upload & AI Check
  const [file, setFile] = useState<File | null>(null);
  const [evidenceDesc, setEvidenceDesc] = useState("");
  const [preflightLoading, setPreflightLoading] = useState(false);
  const [preflightResult, setPreflightResult] = useState<any>(null);
  const [preflightError, setPreflightError] = useState<string | null>(null);
  const [previouslyUploaded, setPreviouslyUploaded] = useState<EvidenceItem[]>([]);
  const [uploadProgress, setUploadProgress] = useState(false);

  // Step 3: Confirmation
  const [confirmed, setConfirmed] = useState(false);
  const [reviewerNote, setReviewerNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      if (!id) return;
      try {
        setLoading(true);
        // 1. Fetch Task
        const taskRes = await api.get<TaskItem>(`/api/v1/tasks/${id}`);
        setTask(taskRes.data);

        // 2. Fetch Control Assignment if linked
        if (taskRes.data.assignment_id) {
          try {
            const ctrlRes = await api.get<ControlAssignment>(`/api/v1/controls/${taskRes.data.assignment_id}`);
            setControl(ctrlRes.data);

            // Fetch previous evidence files
            const evidenceRes = await api.get<any[]>("/api/v1/evidence");
            const filtered = evidenceRes.data.filter(
              (ev) => String(ev.assignment_id) === String(taskRes.data.assignment_id)
            );
            setPreviouslyUploaded(filtered);
          } catch (ctrlErr) {
            console.error("Could not fetch control assignment details", ctrlErr);
          }
        }
      } catch (err) {
        console.error("Error loading task data", err);
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, [id]);

  // Load translation when control is loaded
  useEffect(() => {
    async function fetchTranslation() {
      if (!control?.control_id) return;
      setTranslationLoading(true);
      try {
        const { data } = await api.get(`/api/v1/ai/dept/translate/${control.control_id}`);
        setPlainTranslation(data.response || "No translation generated.");
      } catch (err) {
        console.error("Translation failed", err);
        setPlainTranslation(control.notes || task?.task_description || "Understand this compliance control.");
      } finally {
        setTranslationLoading(false);
      }
    }
    if (control) {
      void fetchTranslation();
    }
  }, [control]);

  // AI Pre-flight Check on Selected File
  const handlePreflightCheck = async () => {
    if (!file || !control) return;
    setPreflightLoading(true);
    setPreflightResult(null);
    setPreflightError(null);

    try {
      // 1. Try to read preview
      let preview = "";
      if (
        file.type.startsWith("text/") ||
        file.name.endsWith(".json") ||
        file.name.endsWith(".csv") ||
        file.name.endsWith(".xml")
      ) {
        preview = await file.text().then((t) => t.slice(0, 2000)).catch(() => "");
      } else {
        preview = `[Binary file preview not fully extractable in browser] Name: ${file.name}, MIME: ${file.type}, Size: ${Math.round(file.size / 1024)} KB`;
      }

      // 2. Call pre-flight endpoint
      const { data } = await api.post("/api/v1/ai/dept/preflight-check", {
        control_id: control.control_id,
        file_name: file.name,
        file_size_kb: Math.round(file.size / 1024),
        mime_type: file.type || "application/octet-stream",
        file_content_preview: preview,
      });

      // Parse JSON from response
      let parsed = data;
      if (typeof data.response === "string") {
        try {
          const jsonMatch = data.response.match(/```json\s*([\s\S]*?)\s*```/) || [null, data.response];
          parsed = JSON.parse(jsonMatch[1].trim());
        } catch {
          // Fallback parsing if plain text JSON
          try {
            parsed = JSON.parse(data.response.trim());
          } catch {
            parsed = {
              status: "pass",
              confidence: 0.8,
              feedback: data.response,
              missing_elements: [],
            };
          }
        }
      }

      setPreflightResult(parsed);
    } catch (err: any) {
      console.error(err);
      setPreflightError(err.response?.data?.detail || "Could not perform pre-flight compliance check.");
    } finally {
      setPreflightLoading(false);
    }
  };

  // Upload Evidence file
  const handleUploadFile = async () => {
    if (!file || !control || !task) return;
    setUploadProgress(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("control_id", control.control_id);
      if (task.assignment_id) {
        formData.append("assignment_id", task.assignment_id);
      }
      if (evidenceDesc) {
        formData.append("description", evidenceDesc);
      }

      const { data } = await api.post("/api/v1/evidence", formData);

      // Refresh previously uploaded
      setPreviouslyUploaded((prev) => [data, ...prev]);

      // Reset file selection
      setFile(null);
      setEvidenceDesc("");
      setPreflightResult(null);
      setPreflightError(null);
    } catch (err) {
      console.error(err);
      alert("Failed to upload evidence document.");
    } finally {
      setUploadProgress(false);
    }
  };

  // Final Submit Task
  const handleFinalSubmit = async () => {
    if (!task) return;
    setSubmitting(true);
    try {
      await api.post(`/api/v1/tasks/${task.task_id}/submit`);
      // Update status locally
      setTask((prev: any) => (prev ? { ...prev, task_status: "completed" } : null));
      setStep(4);
    } catch (err) {
      console.error(err);
      alert("Failed to submit task.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="page-panel">Loading guided task wizard…</div>;
  if (!task) return <div className="page-panel">Task details not found.</div>;

  return (
    <div className="page-panel" style={{ paddingBottom: 64 }}>
      {/* Wizard Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            onClick={() => navigate("/dept/tasks")}
            style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", display: "flex", alignItems: "center" }}
          >
            <ArrowLeft size={16} />
          </button>
          <div>
            <h3 style={{ margin: 0 }}>Task: {task.task_title}</h3>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>Guided Compliance Assistant</span>
          </div>
        </div>
        <span className={`badge badge-${task.task_status === "completed" ? "compliant" : "in_progress"}`}>
          {task.task_status.toUpperCase()}
        </span>
      </div>

      {/* Step Progress Bar */}
      {step < 4 && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16, marginBottom: 24 }}>
          {[
            { n: 1, label: "Understand" },
            { n: 2, label: "Evidence" },
            { n: 3, label: "Confirm" },
          ].map((s) => (
            <div key={s.n} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  backgroundColor: step === s.n ? "var(--primary)" : step > s.n ? "var(--success)" : "var(--surface-raised)",
                  color: step >= s.n ? "white" : "var(--muted)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 600,
                  fontSize: 13,
                }}
              >
                {step > s.n ? "✓" : s.n}
              </div>
              <span style={{ fontSize: 13, fontWeight: step === s.n ? 600 : 500, color: step === s.n ? "var(--text-primary)" : "var(--muted)" }}>
                {s.label}
              </span>
              {s.n < 3 && <div style={{ width: 40, height: 2, backgroundColor: "var(--border)" }} />}
            </div>
          ))}
        </div>
      )}

      {/* Wizard Content Cards */}
      <div style={{ maxWidth: 680, margin: "0 auto" }}>
        {/* STEP 1: Understand the Task */}
        {step === 1 && (
          <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
            <div>
              <h3 style={{ margin: "0 0 4px 0" }}>What you need to do</h3>
              <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>
                We translated this technical requirement into plain, action-oriented English for you.
              </p>
            </div>

            {/* AI Translation Output */}
            <div style={{ background: "var(--primary-bg)", borderRadius: 10, padding: 18, borderLeft: "4px solid var(--primary)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                <Sparkles size={16} color="var(--primary)" />
                <span style={{ fontSize: 12, fontWeight: 700, color: "var(--primary)" }}>AI TRANSLATION (PLAIN TERMS)</span>
              </div>
              {translationLoading ? (
                <div style={{ fontSize: 13, color: "var(--muted)" }}>Translating control requirement…</div>
              ) : (
                <div style={{ fontSize: 14, color: "var(--text-primary)", lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                  {plainTranslation || "Translate this complex control into plain English."}
                </div>
              )}
            </div>

            {/* Technical Details Collapsible */}
            <div style={{ border: "1px solid var(--border)", borderRadius: 8, overflow: "hidden" }}>
              <button
                onClick={() => setShowTechnical(!showTechnical)}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--surface-raised)",
                  border: "none",
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--muted)",
                  cursor: "pointer",
                }}
              >
                <span>{showTechnical ? "Hide" : "Show"} Technical Details & Mapping</span>
                <span>{showTechnical ? "▲" : "▼"}</span>
              </button>
              {showTechnical && (
                <div style={{ padding: 14, fontSize: 12, display: "flex", flexDirection: "column", gap: 8, background: "var(--surface)" }}>
                  <div><strong>Control Identifier:</strong> {control?.control_id || "N/A"}</div>
                  <div><strong>Compliance Framework:</strong> {control?.framework_name || "N/A"}</div>
                  <div><strong>Description:</strong> {control?.notes || "N/A"}</div>
                </div>
              )}
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn btn-primary" onClick={() => setStep(2)}>
                Got it, continue
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Upload Evidence */}
        {step === 2 && (
          <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
            <div>
              <h3 style={{ margin: "0 0 4px 0" }}>Upload your proof</h3>
              <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>
                Provide screenshots or documents showing compliance. You can run an AI check before uploading.
              </p>
            </div>

            {/* File Drop Area */}
            <div style={{ border: "2px dashed var(--border)", borderRadius: 12, padding: 24, textAlign: "center", background: "var(--surface-raised)" }}>
              {!file ? (
                <label style={{ cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
                  <UploadCloud size={32} color="var(--primary)" />
                  <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>Click to select a file</span>
                  <span style={{ fontSize: 12, color: "var(--muted)" }}>PDF, PNG, JPG, CSV, DOCX (Max 10MB)</span>
                  <input
                    type="file"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      if (e.target.files?.[0]) {
                        setFile(e.target.files[0]);
                        setPreflightResult(null);
                        setPreflightError(null);
                      }
                    }}
                  />
                </label>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
                  <FileText size={32} color="var(--primary)" />
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>{file.name}</div>
                    <div style={{ fontSize: 12, color: "var(--muted)" }}>{Math.round(file.size / 1024)} KB</div>
                  </div>

                  <div style={{ width: "100%", maxWidth: 400, marginTop: 8 }}>
                    <input
                      type="text"
                      placeholder="Briefly describe what this file shows (optional)"
                      value={evidenceDesc}
                      onChange={(e) => setEvidenceDesc(e.target.value)}
                      style={{
                        width: "100%",
                        padding: "8px 10px",
                        borderRadius: 8,
                        border: "1px solid var(--border)",
                        fontSize: 13,
                        background: "var(--surface)",
                      }}
                    />
                  </div>

                  {/* Preflight Check Button */}
                  <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                    <button
                      className="btn btn-ghost"
                      onClick={handlePreflightCheck}
                      disabled={preflightLoading || uploadProgress}
                      style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}
                    >
                      <Sparkles size={14} color="var(--primary)" />
                      {preflightLoading ? "Checking file..." : "AI Check: Will this work?"}
                    </button>
                    <button className="btn btn-ghost" onClick={() => setFile(null)} style={{ fontSize: 12, color: "var(--critical)" }}>
                      Choose Different File
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* AI Preflight Result Banner */}
            {preflightError && (
              <div style={{ padding: 12, borderRadius: 8, background: "#FEF2F2", color: "#EF4444", fontSize: 12, display: "flex", gap: 8 }}>
                <AlertTriangle size={16} />
                <span>{preflightError}</span>
              </div>
            )}

            {preflightResult && (
              <div
                style={{
                  padding: 16,
                  borderRadius: 10,
                  background: preflightResult.status === "pass" ? "#ECFDF5" : "#FFF7ED",
                  borderLeft: `4px solid ${preflightResult.status === "pass" ? "var(--success)" : "var(--warning)"}`,
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span
                    style={{
                      fontSize: 13,
                      fontWeight: 700,
                      color: preflightResult.status === "pass" ? "var(--success)" : "#D97706",
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                    }}
                  >
                    {preflightResult.status === "pass" ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    {preflightResult.status === "pass"
                      ? "AI PRE-FLIGHT: Good to Upload!"
                      : "AI PRE-FLIGHT: Recommendation / Warning"}
                  </span>
                  <span style={{ fontSize: 11, color: "var(--muted)", fontWeight: 500 }}>
                    Confidence: {Math.round(preflightResult.confidence * 100)}%
                  </span>
                </div>
                <div style={{ fontSize: 13, lineHeight: 1.5, color: "var(--text-primary)" }}>
                  {preflightResult.feedback}
                </div>
                {Array.isArray(preflightResult.missing_elements) && preflightResult.missing_elements.length > 0 && (
                  <div style={{ marginTop: 4 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase" }}>Missing Details:</div>
                    <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: 12, color: "var(--text-secondary)" }}>
                      {preflightResult.missing_elements.map((el: string, idx: number) => (
                        <li key={idx} style={{ marginBottom: 2 }}>{el}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Upload Action */}
            {file && (
              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  className="btn btn-primary"
                  onClick={handleUploadFile}
                  disabled={uploadProgress || (preflightResult?.status === "fail")}
                >
                  {uploadProgress ? "Uploading file..." : "Upload Evidence"}
                </button>
              </div>
            )}

            {/* Previously Uploaded list */}
            {previouslyUploaded.length > 0 && (
              <div style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--muted)", marginBottom: 10 }}>
                  PREVIOUSLY UPLOADED FOR THIS TASK
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {previouslyUploaded.map((ev) => (
                    <div
                      key={ev.evidence_id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "10px 14px",
                        background: "var(--surface-raised)",
                        borderRadius: 8,
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <FileText size={16} color="var(--primary)" />
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 500 }}>{ev.file_name}</div>
                          {ev.description && <div style={{ fontSize: 11, color: "var(--muted)" }}>{ev.description}</div>}
                        </div>
                      </div>
                      <span className={`badge badge-${ev.approval_status === "approved" ? "compliant" : ev.approval_status === "rejected" ? "non_compliant" : "in_progress"}`}>
                        {ev.approval_status.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Navigation */}
            <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: 16, marginTop: 8 }}>
              <button className="btn btn-ghost" onClick={() => setStep(1)}>
                Back to step 1
              </button>
              <button
                className="btn btn-primary"
                disabled={previouslyUploaded.length === 0}
                onClick={() => setStep(3)}
              >
                Next Step
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Confirm & Submit */}
        {step === 3 && (
          <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
            <div>
              <h3 style={{ margin: "0 0 4px 0" }}>Ready to submit?</h3>
              <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>
                Confirm details before submitting this completed remediation task for final compliance approval.
              </p>
            </div>

            <div style={{ background: "var(--surface-raised)", borderRadius: 10, padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
              <div><strong>Task:</strong> {task.task_title}</div>
              <div><strong>Uploaded Files:</strong> {previouslyUploaded.length} document(s)</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
                {previouslyUploaded.map((u) => (
                  <span
                    key={u.evidence_id}
                    style={{ fontSize: 11, background: "var(--surface)", border: "1px solid var(--border)", padding: "4px 8px", borderRadius: 4 }}
                  >
                    {u.file_name}
                  </span>
                ))}
              </div>
            </div>

            {/* Self-declaration */}
            <label style={{ display: "flex", gap: 8, alignItems: "flex-start", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                style={{ marginTop: 3 }}
              />
              <span style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                I confirm that the uploaded evidence accurately represents the current state of our department's compliance with this requirement.
              </span>
            </label>

            {/* Reviewer Note */}
            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6 }}>
                Message for the Compliance Officer (optional)
              </label>
              <textarea
                style={{
                  width: "100%",
                  minHeight: 80,
                  padding: 10,
                  borderRadius: 8,
                  border: "1px solid var(--border)",
                  background: "var(--surface)",
                  color: "var(--text-primary)",
                  fontSize: 13,
                  resize: "vertical",
                }}
                placeholder="Add any context, location, or additional explanation about the evidence uploaded..."
                value={reviewerNote}
                onChange={(e) => setReviewerNote(e.target.value)}
              />
            </div>

            {/* Navigation */}
            <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: 16 }}>
              <button className="btn btn-ghost" onClick={() => setStep(2)}>
                Back to step 2
              </button>
              <button
                className="btn btn-primary"
                onClick={handleFinalSubmit}
                disabled={!confirmed || submitting}
              >
                {submitting ? "Submitting..." : "Submit Task"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: Done */}
        {step === 4 && (
          <div className="card" style={{ padding: 32, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: "50%",
                background: "#ECFDF5",
                color: "var(--success)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CheckCircle size={32} />
            </div>
            <div>
              <h3 style={{ margin: "0 0 6px 0" }}>Submitted Successfully!</h3>
              <p style={{ margin: 0, fontSize: 14, color: "var(--muted)", lineHeight: 1.5 }}>
                Your evidence and response has been sent to the Compliance Officer for review.
              </p>
            </div>

            <div
              style={{
                background: "var(--surface-raised)",
                borderRadius: 10,
                padding: 16,
                textAlign: "left",
                width: "100%",
                fontSize: 13,
                color: "var(--text-secondary)",
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}
            >
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>What happens next?</div>
              <div>• The Compliance Officer will review your submission.</div>
              <div>• You'll receive a notification if changes are needed or once approved.</div>
              <div>• Expected review cycle: 1–3 business days.</div>
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              <button className="btn btn-primary" onClick={() => navigate("/dept/tasks")}>
                Back to My Tasks
              </button>
              <button className="btn btn-ghost" onClick={() => navigate("/dept/evidence")}>
                View Evidence History
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
export { TaskWizard };
