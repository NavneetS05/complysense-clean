// Use: Auditor observation tracking and finding register.

import { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";

type ObservationItem = {
  observation_id: string;
  observation_text: string;
  severity: string;
  status: string;
  created_at?: string;
  control_id?: string;
  assessment_name?: string;
  framework_name?: string;
  evidence_file?: string;
};

export default function Observations() {
  const [rows, setRows] = useState<ObservationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<ObservationItem | null>(null);
  const [filters, setFilters] = useState({ search: "", severity: "All", status: "All" });

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/audit/observations");
        setRows(Array.isArray(data) ? data : []);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const visibleRows = useMemo(() => rows.filter((row) => {
    const matchesSearch = !filters.search || `${row.observation_text} ${row.control_id || ""}`.toLowerCase().includes(filters.search.toLowerCase());
    const matchesSeverity = filters.severity === "All" || row.severity === filters.severity;
    const matchesStatus = filters.status === "All" || row.status === filters.status;
    return matchesSearch && matchesSeverity && matchesStatus;
  }), [rows, filters]);

  const summary = useMemo(() => ({
    findings: rows.filter((row) => row.severity === "finding").length,
    observations: rows.filter((row) => row.severity === "observation").length,
    recommendations: rows.filter((row) => row.severity === "recommendation").length,
    resolved: rows.filter((row) => row.status === "resolved").length,
  }), [rows]);

  async function handleDelete(id: string) {
    if (!window.confirm("Delete this observation?")) {
      return;
    }
    await api.delete(`/api/v1/audit/observations/${id}`);
    setRows((current) => current.filter((row) => row.observation_id !== id));
  }

  async function handleToggleStatus(id: string, nextStatus: string) {
    await api.patch(`/api/v1/audit/observations/${id}`, { status: nextStatus });
    setRows((current) => current.map((row) => row.observation_id === id ? { ...row, status: nextStatus } : row));
  }

  return (
    <div className="page-panel" style={{ display: "grid", gap: 16 }}>
      <div>
        <h2>Observations & Findings</h2>
        <p>Track every observation created during the audit cycle and keep status aligned with remediation progress.</p>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {[
          { label: "Findings", value: summary.findings, color: "#dc2626" },
          { label: "Observations", value: summary.observations, color: "#2563eb" },
          { label: "Recommendations", value: summary.recommendations, color: "#d97706" },
          { label: "Resolved", value: summary.resolved, color: "#16a34a" },
        ].map((chip) => (
          <div key={chip.label} style={{ borderRadius: 999, padding: "8px 12px", background: `${chip.color}1A`, color: chip.color, fontWeight: 700 }}>
            {chip.label}: {chip.value}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
        <input value={filters.search} onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))} placeholder="Search by observation or control" style={{ minWidth: 220, padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }} />
        <select value={filters.severity} onChange={(event) => setFilters((current) => ({ ...current, severity: event.target.value }))} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }}>
          <option value="All">Severity: All</option>
          <option value="finding">Finding</option>
          <option value="observation">Observation</option>
          <option value="recommendation">Recommendation</option>
        </select>
        <select value={filters.status} onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1" }}>
          <option value="All">Status: All</option>
          <option value="open">Open</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>
      {loading ? <p>Loading observations…</p> : (
        <div style={{ display: "grid", gap: 12 }}>
          {visibleRows.map((row) => (
            <div key={row.observation_id} style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{row.observation_text}</div>
                  <div style={{ color: "#64748b", fontSize: 13, marginTop: 4 }}>{row.control_id || "Control"} • {row.framework_name || "Framework"}</div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ padding: "4px 10px", borderRadius: 999, background: row.severity === "finding" ? "#fee2e2" : row.severity === "recommendation" ? "#fef3c7" : "#dbeafe", color: row.severity === "finding" ? "#b91c1c" : row.severity === "recommendation" ? "#92400e" : "#1d4ed8", fontSize: 12, fontWeight: 700 }}>{row.severity}</span>
                  <span style={{ padding: "4px 10px", borderRadius: 999, background: row.status === "resolved" ? "#dcfce7" : row.status === "acknowledged" ? "#fef3c7" : "#fee2e2", color: row.status === "resolved" ? "#166534" : row.status === "acknowledged" ? "#92400e" : "#b91c1c", fontSize: 12, fontWeight: 700 }}>{row.status}</span>
                </div>
              </div>
              <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center", color: "#64748b", fontSize: 13 }}>
                <span>Added: {row.created_at ? new Date(row.created_at).toLocaleString() : "—"}</span>
                {row.evidence_file ? <span>Evidence: {row.evidence_file}</span> : null}
              </div>
              <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
                {row.status !== "resolved" ? <button onClick={() => handleToggleStatus(row.observation_id, row.status === "acknowledged" ? "resolved" : "acknowledged")} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1", background: "white" }}>{row.status === "acknowledged" ? "Resolve" : "Acknowledge"}</button> : null}
                <button onClick={() => setSelected(row)} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1", background: "white" }}>View</button>
                <button onClick={() => handleDelete(row.observation_id)} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #dc2626", color: "#dc2626", background: "white" }}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
      {selected ? <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, background: "white", padding: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
          <div>
            <h3 style={{ margin: 0 }}>{selected.severity}</h3>
            <p style={{ margin: "4px 0 0", color: "#475569" }}>{selected.observation_text}</p>
          </div>
          <button onClick={() => setSelected(null)} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #cbd5e1", background: "white" }}>Close</button>
        </div>
        <div style={{ marginTop: 10, color: "#64748b", fontSize: 13 }}>
          <div>Control: {selected.control_id || "—"}</div>
          <div>Assessment: {selected.assessment_name || "—"}</div>
          <div>Status: {selected.status}</div>
          <div>Added: {selected.created_at ? new Date(selected.created_at).toLocaleString() : "—"}</div>
        </div>
      </div> : null}
    </div>
  );
}
