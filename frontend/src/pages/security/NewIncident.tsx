// Use: Incident form that registers title, category, and detection time.

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";

const incidentTypes = ["Data Breach", "Unauthorized Access", "Ransomware", "Phishing Attack", "System Failure", "DDoS Attack", "Other"];
const dataCategories = ["Student Personal Data", "Staff Personal Data", "Financial Records", "Research Data", "Authentication Credentials", "System Configuration", "Other"];

export default function NewIncident() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [incidentType, setIncidentType] = useState("Other");
  const [severity, setSeverity] = useState("high");
  const [description, setDescription] = useState("");
  const [occurredAt, setOccurredAt] = useState("");
  const [detectedAt, setDetectedAt] = useState("");
  const [affectedSystems, setAffectedSystems] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [dpdpRequired, setDpdpRequired] = useState(false);
  const [assignedTo, setAssignedTo] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const deadline = useMemo(() => {
    if (!detectedAt) return "—";
    const base = new Date(detectedAt);
    base.setHours(base.getHours() + 6);
    return base.toLocaleString();
  }, [detectedAt]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      const { data } = await api.post("/api/v1/incidents", {
        title: title.trim(),
        description: description.trim(),
        incident_type: incidentType,
        severity,
        occurred_at: occurredAt || undefined,
        detected_at: detectedAt || undefined,
        affected_systems: affectedSystems.trim() || undefined,
        affected_data_categories: selectedCategories.join(", "),
        dpdp_notification_required: dpdpRequired,
        assigned_to: assignedTo || undefined
      });
      navigate(`/security/incidents/${data.incident_id}`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-panel">
      <PageShell title="Log New Incident" subtitle="Fast incident intake with CERT-In clock start." />
      <div style={{ background: "#fffbeb", border: "1px solid #fcd34d", borderRadius: 10, padding: 12, marginTop: 16 }}>
        ℹ Logging an incident starts the CERT-In 6-hour reporting clock from the detected time you enter below.
      </div>
      <form onSubmit={handleSubmit} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <label style={{ display: "block", marginBottom: 8 }}>
            Incident Title*
            <input required value={title} onChange={(event) => setTitle(event.target.value)} maxLength={255} placeholder="Brief, clear description" style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
          <label style={{ display: "block", marginBottom: 8 }}>
            Incident Type*
            <select value={incidentType} onChange={(event) => setIncidentType(event.target.value)} style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }}>
              {incidentTypes.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label style={{ display: "block", marginBottom: 8 }}>
            Severity*
            <select value={severity} onChange={(event) => setSeverity(event.target.value)} style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }}>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </label>
          <label style={{ display: "block", marginBottom: 8 }}>
            Description*
            <textarea required rows={5} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Describe what happened and initial findings" style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16 }}>
          <label style={{ display: "block", marginBottom: 8 }}>
            Date & Time Occurred
            <input type="datetime-local" value={occurredAt} onChange={(event) => setOccurredAt(event.target.value)} style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
          <label style={{ display: "block", marginBottom: 8 }}>
            Date & Time Detected*
            <input required type="datetime-local" value={detectedAt} onChange={(event) => setDetectedAt(event.target.value)} style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
            <div style={{ color: "#6b7280", fontSize: 12, marginTop: 4 }}>⏰ CERT-In deadline: {deadline}</div>
          </label>
          <label style={{ display: "block", marginBottom: 8 }}>
            Affected Systems
            <textarea rows={3} value={affectedSystems} onChange={(event) => setAffectedSystems(event.target.value)} placeholder="Hostnames or IPs" style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
          <div style={{ marginBottom: 8 }}>
            Affected Data Categories
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginTop: 6 }}>
              {dataCategories.map((category) => (
                <label key={category} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
                  <input type="checkbox" checked={selectedCategories.includes(category)} onChange={() => setSelectedCategories((current) => current.includes(category) ? current.filter((item) => item !== category) : [...current, category])} />
                  {category}
                </label>
              ))}
            </div>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <input type="checkbox" checked={dpdpRequired} onChange={(event) => setDpdpRequired(event.target.checked)} />
            DPDP Notification Required
          </label>
          {dpdpRequired ? <div style={{ background: "#fef3c7", border: "1px solid #fde68a", borderRadius: 8, padding: 8, marginBottom: 8, fontSize: 13 }}>DPDP Act 2023 Section 8(6) may require notification to the Data Protection Board and affected individuals.</div> : null}
          <label style={{ display: "block" }}>
            Assign To
            <input value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)} placeholder="User ID or email" style={{ width: "100%", padding: 10, marginTop: 4, borderRadius: 8, border: "1px solid #d1d5db" }} />
          </label>
        </div>
        <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <button type="button" onClick={() => navigate(-1)} style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #d1d5db", background: "#fff" }}>Cancel</button>
          <button type="submit" disabled={submitting} style={{ padding: "10px 14px", borderRadius: 8, border: 0, background: "#2563eb", color: "#fff" }}>{submitting ? "Saving…" : "Log Incident"}</button>
        </div>
      </form>
    </div>
  );
}
