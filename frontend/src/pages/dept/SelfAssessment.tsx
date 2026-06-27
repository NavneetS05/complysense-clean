// Use: Form for submitting periodic local self-assessments.

import { useState } from "react";

export default function SelfAssessment() {
  const [form, setForm] = useState({ readiness: "Medium", notes: "", owner: "" });
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitted(true);
  }

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>Self Assessment</h2>
        <p>Capture the department’s readiness posture and the status of local remediation actions.</p>
      </div>
      <form onSubmit={handleSubmit} style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16, display: "grid", gap: 12 }}>
        <label style={{ display: "grid", gap: 4 }}>
          <span>Readiness level</span>
          <select value={form.readiness} onChange={(event) => setForm((current) => ({ ...current, readiness: event.target.value }))} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }}>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </label>
        <label style={{ display: "grid", gap: 4 }}>
          <span>Owner</span>
          <input value={form.owner} onChange={(event) => setForm((current) => ({ ...current, owner: event.target.value }))} placeholder="Department owner" style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
        </label>
        <label style={{ display: "grid", gap: 4 }}>
          <span>Notes</span>
          <textarea value={form.notes} onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))} rows={5} placeholder="Describe outstanding actions, blockers, and any evidence gaps." style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
        </label>
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "none", background: "#2563eb", color: "white", width: 200 }}>Submit Assessment</button>
      </form>
      {submitted ? <div style={{ border: "1px solid #dcfce7", borderRadius: 12, background: "#f0fdf4", padding: 12, color: "#166534" }}>Self-assessment submitted successfully.</div> : null}
    </div>
  );
}
