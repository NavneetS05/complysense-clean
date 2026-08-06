// Use: Super Admin — Audit Trail Explorer. Filterable, paginated, and CSV-downloadable log of all platform actions.

import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { Download, Search } from "lucide-react";

interface AuditLog {
  audit_log_id: string;
  institution_name: string | null;
  user_name: string | null;
  user_email: string | null;
  role_at_time: string | null;
  action_type: string;
  entity_type: string | null;
  entity_id: string | null;
  ip_address: string | null;
  mac_address?: string | null;
  created_at: string;
}

interface Institution {
  institution_id: string;
  institution_name: string;
}

const ACTION_TYPES = [
  "login", "logout", "user_created", "user_invited", "user_role_updated",
  "user_unlocked", "admin_password_reset", "change_password", "institution_created",
  "institution_updated", "institution_status_toggled", "department_created",
  "event_created", "evidence_approved", "evidence_rejected", "reviewer_assigned", "user_blocked",
];

const ACTION_LABELS: Record<string, string> = {
  login: "Logged In",
  logout: "Logged Out",
  register: "Account Registered",
  user_created: "Created User",
  user_invited: "Invited User",
  user_role_updated: "Updated User Role",
  user_unlocked: "Unlocked User Account",
  admin_password_reset: "Reset User Password",
  change_password: "Changed Password",
  institution_created: "Created Institution",
  institution_updated: "Updated Institution",
  institution_deleted: "Deleted Institution",
  institution_status_toggled: "Toggled Institution Status",
  department_created: "Created Department",
  department_updated: "Updated Department",
  department_deleted: "Deleted Department",
  event_created: "Created Calendar Event",
  event_updated: "Updated Calendar Event",
  event_deleted: "Deleted Calendar Event",
  policy_created: "Created Policy",
  policy_approved: "Approved Policy",
  policy_rejected: "Rejected Policy",
  evidence_submitted: "Submitted Evidence",
  evidence_approved: "Approved Evidence",
  evidence_rejected: "Rejected Evidence",
  incident_created: "Reported Incident",
  incident_updated: "Updated Incident",
  vendor_created: "Added Vendor",
  vendor_assessed: "Assessed Vendor",
  observation_added: "Added Audit Observation",
  reviewer_assigned: "Assigned Reviewer",
  login_failed: "Failed Login",
  user_blocked: "Account Blocked",
};

export default function AuditTrail() {
  const [searchParams] = useSearchParams();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const LIMIT = 50;

  // Filters
  const [institutionId, setInstitutionId] = useState(searchParams.get("institution_id") ?? "");
  const [actionType, setActionType] = useState(searchParams.get("action_type") ?? "");
  const [userSearch, setUserSearch] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    const params: Record<string, string | number> = { page, limit: LIMIT };
    if (institutionId) params.institution_id = institutionId;
    if (actionType) params.action_type = actionType;
    if (userSearch) params.user_search = userSearch;
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;

    try {
      const res = await api.get("/api/v1/audit/logs", { params });
      setLogs(res.data.logs ?? []);
      setTotal(res.data.total ?? 0);
    } catch { setLogs([]); }
    setLoading(false);
  }, [page, institutionId, actionType, userSearch, fromDate, toDate]);

  useEffect(() => {
    api.get("/api/v1/institutions").then((r) => setInstitutions(r.data)).catch(() => {});
  }, []);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  async function handleCSVExport() {
    const params: Record<string, string> = { format: "csv" };
    if (institutionId) params.institution_id = institutionId;
    if (actionType) params.action_type = actionType;
    if (userSearch) params.user_search = userSearch;
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;

    try {
      const res = await api.get("/api/v1/audit/logs", { params, responseType: "blob" });
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = "audit_trail_export.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch { alert("CSV export failed."); }
  }

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <PageShell
      title="Audit Trail"
      subtitle="Immutable, searchable log of every action across the platform"
      actions={
        <button className="btn btn-ghost" onClick={handleCSVExport} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Download size={14} /> Export CSV
        </button>
      }
    >
      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "flex-end" }}>
          <div style={{ flex: "1 1 150px" }}>
            <label className="form-label" style={{ fontSize: 11 }}>From Date</label>
            <input type="date" className="form-input" value={fromDate} onChange={(e) => setFromDate(e.target.value)} style={{ fontSize: 13 }} />
          </div>
          <div style={{ flex: "1 1 150px" }}>
            <label className="form-label" style={{ fontSize: 11 }}>To Date</label>
            <input type="date" className="form-input" value={toDate} onChange={(e) => setToDate(e.target.value)} style={{ fontSize: 13 }} />
          </div>
          <div style={{ flex: "1 1 180px" }}>
            <label className="form-label" style={{ fontSize: 11 }}>Institution</label>
            <select className="form-input" value={institutionId} onChange={(e) => setInstitutionId(e.target.value)} style={{ fontSize: 13 }}>
              <option value="">All Institutions</option>
              {institutions.map((i) => <option key={i.institution_id} value={i.institution_id}>{i.institution_name}</option>)}
            </select>
          </div>
          <div style={{ flex: "1 1 180px" }}>
            <label className="form-label" style={{ fontSize: 11 }}>Action Type</label>
            <select className="form-input" value={actionType} onChange={(e) => setActionType(e.target.value)} style={{ fontSize: 13 }}>
              <option value="">All Actions</option>
              {ACTION_TYPES.map((a) => <option key={a} value={a}>{ACTION_LABELS[a] ?? a}</option>)}
            </select>
          </div>
          <div style={{ flex: "1 1 200px" }}>
            <label className="form-label" style={{ fontSize: 11 }}>Search User</label>
            <div style={{ position: "relative" }}>
              <Search size={13} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
              <input
                className="form-input"
                placeholder="Name or email..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                style={{ fontSize: 13, paddingLeft: 30 }}
              />
            </div>
          </div>
          {(institutionId || actionType || userSearch || fromDate || toDate) && (
            <button className="btn btn-ghost" style={{ fontSize: 12, alignSelf: "flex-end" }}
              onClick={() => { setInstitutionId(""); setActionType(""); setUserSearch(""); setFromDate(""); setToDate(""); setPage(1); }}>
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Logs Table */}
      <div className="card">
        <div style={{ marginBottom: 12, fontSize: 13, color: "var(--text-muted)" }}>
          Showing {logs.length} of {total} entries
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Institution</th>
                <th>User</th>
                <th>Role</th>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>IP Address</th>
                <th>MAC Address</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={i}>{Array.from({ length: 9 }).map((_, j) => <td key={j}><div className="skeleton" style={{ height: 16, borderRadius: 4 }} /></td>)}</tr>
                ))
              ) : logs.length === 0 ? (
                <tr><td colSpan={9} style={{ textAlign: "center", color: "var(--text-muted)", padding: 40 }}>No audit logs match your filters.</td></tr>
              ) : logs.map((log) => (
                <tr key={log.audit_log_id}>
                  <td style={{ fontFamily: "var(--font-mono)", fontSize: 11, whiteSpace: "nowrap", color: "var(--text-muted)" }}>
                    {new Date(log.created_at).toLocaleString("en-IN")}
                  </td>
                  <td style={{ fontSize: 13 }}>{log.institution_name ?? "System"}</td>
                  <td>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{log.user_name ?? "System"}</div>
                    {log.user_email && <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{log.user_email}</div>}
                  </td>
                  <td style={{ fontSize: 12 }}>{log.role_at_time ? <span className="badge badge-draft">{log.role_at_time}</span> : "—"}</td>
                  <td><span className="badge badge-in_progress">{ACTION_LABELS[log.action_type] ?? log.action_type}</span></td>
                  <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{log.entity_type ?? "—"}</td>
                  <td>
                    {log.entity_id ? (
                      <span
                        style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-muted)", cursor: "help" }}
                        title={log.entity_id}
                      >
                        {log.entity_id.slice(0, 8)}…
                      </span>
                    ) : "—"}
                  </td>
                  <td style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-muted)" }}>{log.ip_address ?? "—"}</td>
                  <td style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-muted)" }}>{log.mac_address ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 20 }}>
            <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} style={{ fontSize: 12 }}>← Prev</button>
            <span style={{ fontSize: 13, alignSelf: "center", color: "var(--text-secondary)" }}>Page {page} of {totalPages}</span>
            <button className="btn btn-ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} style={{ fontSize: 12 }}>Next →</button>
          </div>
        )}
      </div>
    </PageShell>
  );
}
