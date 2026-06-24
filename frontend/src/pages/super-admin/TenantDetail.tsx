// Use: Super Admin — Institution Detail view. Shows 3 stat cards and tabs for Users, Departments, and Audit Logs.

import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { useToast } from "../../components/shared/Toast";
import { Users, Building2, BarChart3, ScrollText } from "lucide-react";

interface Institution {
  institution_id: string;
  institution_name: string;
  institution_type: string;
  city: string;
  state: string;
  staff_count: number;
  is_active: boolean;
  user_count: number;
  department_count: number;
  compliance_percentage: number;
}

interface User {
  user_id: string;
  full_name: string;
  email: string;
  role_name: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

interface Department {
  department_id: string;
  department_name: string;
  department_code: string | null;
  hod_name: string | null;
  reviewer_name: string | null;
  is_active: boolean;
}

interface AuditLog {
  audit_log_id: string;
  user_name: string;
  action_type: string;
  entity_type: string | null;
  entity_id: string | null;
  ip_address: string | null;
  created_at: string;
}

const ACTION_LABELS: Record<string, string> = {
  login: "Logged in", logout: "Logged out", user_created: "Created user",
  role_changed: "Changed role", login_failed: "Failed login", evidence_approved: "Approved evidence",
  reviewer_assigned: "Assigned reviewer",
};

export default function TenantDetail() {
  const { institution_id } = useParams<{ institution_id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [institution, setInstitution] = useState<Institution | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [activeTab, setActiveTab] = useState<"users" | "departments" | "audit">("users");
  const [loading, setLoading] = useState(true);
  const [confirmDeactivate, setConfirmDeactivate] = useState(false);

  useEffect(() => {
    if (!institution_id) return;
    async function load() {
      setLoading(true);
      try {
        const [instRes, usersRes, deptsRes, auditRes] = await Promise.allSettled([
          api.get(`/api/v1/institutions/${institution_id}`),
          api.get(`/api/v1/users`, { params: { institution_id } }),
          api.get(`/api/v1/departments`),
          api.get(`/api/v1/audit/logs`, { params: { institution_id, limit: 50 } }),
        ]);
        if (instRes.status === "fulfilled") setInstitution(instRes.value.data);
        if (usersRes.status === "fulfilled") setUsers(usersRes.value.data);
        if (deptsRes.status === "fulfilled") setDepartments(deptsRes.value.data);
        if (auditRes.status === "fulfilled") setAuditLogs(auditRes.value.data?.logs ?? []);
      } catch { /* individual handled */ }
      setLoading(false);
    }
    load();
  }, [institution_id]);

  async function handleToggleStatus() {
    if (!institution) return;
    try {
      await api.put(`/api/v1/institutions/${institution_id}/status`, { is_active: !institution.is_active });
      showToast(`Institution ${institution.is_active ? "deactivated" : "activated"}`, "success");
      setInstitution({ ...institution, is_active: !institution.is_active });
      setConfirmDeactivate(false);
    } catch {
      showToast("Failed to update status", "error");
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 32 }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 40, marginBottom: 16, borderRadius: 8 }} />
        ))}
      </div>
    );
  }

  if (!institution) {
    return (
      <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)" }}>
        <p>Institution not found.</p>
        <Link to="/super-admin/tenants" className="btn btn-primary" style={{ marginTop: 12 }}>← Back to Institutions</Link>
      </div>
    );
  }

  return (
    <PageShell
      title={institution.institution_name}
      subtitle={`${institution.institution_type} — ${institution.city}, ${institution.state}`}
      breadcrumbs={[
        { label: "Institutions", href: "/super-admin/tenants" },
        { label: institution.institution_name },
      ]}
      actions={
        <div style={{ display: "flex", gap: 8 }}>
          <button
            className={`btn ${institution.is_active ? "btn-ghost" : "btn-primary"}`}
            onClick={() => setConfirmDeactivate(true)}
          >
            {institution.is_active ? "Deactivate" : "Activate"}
          </button>
        </div>
      }
    >
      {/* Stat Cards */}
      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 24 }}>
        {[
          { icon: Users, label: "Total Users", value: institution.user_count },
          { icon: Building2, label: "Departments", value: institution.department_count },
          { icon: BarChart3, label: "Compliance Score", value: `${institution.compliance_percentage}%` },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="stat-card">
            <div className="stat-card-icon"><Icon size={20} /></div>
            <div className="stat-card-value">{value}</div>
            <div className="stat-card-label">{label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="card">
        <div style={{ display: "flex", borderBottom: "1px solid var(--border)", marginBottom: 20 }}>
          {(["users", "departments", "audit"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`tab-btn ${activeTab === tab ? "active" : ""}`}
              style={{ padding: "10px 20px", background: "none", border: "none", cursor: "pointer", fontSize: 14, fontWeight: activeTab === tab ? 600 : 400, color: activeTab === tab ? "var(--primary)" : "var(--text-secondary)", borderBottom: activeTab === tab ? "2px solid var(--primary)" : "2px solid transparent", marginBottom: -1 }}
            >
              {tab === "users" ? "Users" : tab === "departments" ? "Departments" : "Audit Logs"}
            </button>
          ))}
        </div>

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Last Login</th><th>Created</th></tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)", padding: 32 }}>No users found.</td></tr>
                ) : users.map((u) => (
                  <tr key={u.user_id}>
                    <td style={{ fontWeight: 500 }}>{u.full_name}</td>
                    <td style={{ fontSize: 13, color: "var(--text-secondary)" }}>{u.email}</td>
                    <td><span className="badge badge-draft">{u.role_name}</span></td>
                    <td><span className={`badge ${u.is_active ? "badge-compliant" : "badge-inactive"}`}>{u.is_active ? "Active" : "Inactive"}</span></td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{u.last_login ? new Date(u.last_login).toLocaleDateString("en-IN") : "Never"}</td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>{new Date(u.created_at).toLocaleDateString("en-IN")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Departments Tab */}
        {activeTab === "departments" && (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr><th>Department Name</th><th>Code</th><th>HOD Name</th><th>Reviewer Assigned</th><th>Status</th></tr>
              </thead>
              <tbody>
                {departments.length === 0 ? (
                  <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: 32 }}>No departments found.</td></tr>
                ) : departments.map((d) => (
                  <tr key={d.department_id}>
                    <td style={{ fontWeight: 500 }}>{d.department_name}</td>
                    <td><code style={{ fontSize: 12, color: "var(--text-muted)" }}>{d.department_code ?? "—"}</code></td>
                    <td>{d.hod_name ?? "—"}</td>
                    <td style={{ color: d.reviewer_name ? "var(--text-primary)" : "var(--warning)" }}>{d.reviewer_name ?? "Unassigned"}</td>
                    <td><span className={`badge ${d.is_active ? "badge-compliant" : "badge-inactive"}`}>{d.is_active ? "Active" : "Inactive"}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Audit Logs Tab */}
        {activeTab === "audit" && (
          <>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr><th>Timestamp</th><th>User</th><th>Action</th><th>Entity</th><th>IP</th></tr>
                </thead>
                <tbody>
                  {auditLogs.length === 0 ? (
                    <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: 32 }}>No logs for this institution.</td></tr>
                  ) : auditLogs.slice(0, 50).map((log) => (
                    <tr key={log.audit_log_id}>
                      <td style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{new Date(log.created_at).toLocaleString("en-IN")}</td>
                      <td style={{ fontSize: 13 }}>{log.user_name ?? "System"}</td>
                      <td><span className="badge badge-draft">{ACTION_LABELS[log.action_type] ?? log.action_type}</span></td>
                      <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{log.entity_type ?? "—"}</td>
                      <td style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{log.ip_address ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: 12 }}>
              <Link to={`/super-admin/audit-trail?institution_id=${institution_id}`} style={{ fontSize: 12, color: "var(--primary)", fontWeight: 600 }}>
                View full audit trail for this institution →
              </Link>
            </div>
          </>
        )}
      </div>

      {confirmDeactivate && (
        <ConfirmModal
          title={institution.is_active ? "Deactivate Institution" : "Activate Institution"}
          description={institution.is_active
            ? `Deactivating will prevent all users at "${institution.institution_name}" from logging in. Continue?`
            : `This will re-enable access for all users at "${institution.institution_name}". Continue?`}
          confirmLabel={institution.is_active ? "Deactivate" : "Activate"}
          variant={institution.is_active ? "destructive" : "default"}
          onConfirm={handleToggleStatus}
          onCancel={() => setConfirmDeactivate(false)}
        />
      )}
    </PageShell>
  );
}
