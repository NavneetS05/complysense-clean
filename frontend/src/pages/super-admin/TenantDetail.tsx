// Use: Super Admin — Institution Detail view. Shows 3 stat cards and tabs for Users, Departments, and Audit Logs.

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";
import { Users, Building2, BarChart3, UserPlus, Plus, KeyRound } from "lucide-react";

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
  user_name: string | null;
  action_type: string;
  entity_type: string | null;
  entity_id: string | null;
  ip_address: string | null;
  mac_address?: string | null;
  created_at: string;
}

const ACTION_LABELS: Record<string, string> = {
  login: "Logged In",
  logout: "Logged Out",
  user_created: "Created User",
  user_invited: "Invited User",
  user_role_updated: "Updated User Role",
  user_unlocked: "Unlocked User Account",
  admin_password_reset: "Reset User Password",
  change_password: "Changed Password",
  institution_created: "Created Institution",
  institution_updated: "Updated Institution",
  institution_status_toggled: "Toggled Institution Status",
  department_created: "Created Department",
  department_updated: "Updated Department",
  department_deleted: "Deleted Department",
  event_created: "Created Calendar Event",
  evidence_approved: "Approved Evidence",
  evidence_rejected: "Rejected Evidence",
  reviewer_assigned: "Assigned Reviewer",
  login_failed: "Failed Login",
  user_blocked: "Account Blocked",
};

const ASSIGNABLE_ROLES = [
  "Institution Admin", "Compliance Officer", "IT Security Officer",
  "Auditor", "Department Reviewer", "Vendor Reviewer", "Policy Approver", "Read-Only Assessor",
];

export default function TenantDetail() {
  const { institution_id } = useParams<{ institution_id: string }>();
  const toast = useToast();
  const [institution, setInstitution] = useState<Institution | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [activeTab, setActiveTab] = useState<"users" | "departments" | "audit">("users");
  const [loading, setLoading] = useState(true);
  const [confirmDeactivate, setConfirmDeactivate] = useState(false);

  // Add User Modal State
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [addUserForm, setAddUserForm] = useState({
    full_name: "",
    email: "",
    role_name: "Institution Admin",
  });
  const [addUserLoading, setAddUserLoading] = useState(false);

  // Admin Reset Password State
  const [resetPwUser, setResetPwUser] = useState<User | null>(null);
  const [customNewPw, setCustomNewPw] = useState("");
  const [resetPwLoading, setResetPwLoading] = useState(false);

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
      toast.success(`Institution ${institution.is_active ? "deactivated" : "activated"}`);
      setInstitution({ ...institution, is_active: !institution.is_active });
      setConfirmDeactivate(false);
    } catch {
      toast.error("Failed to update status");
    }
  }

  async function handleAddUser() {
    if (!addUserForm.full_name.trim() || !addUserForm.email.trim()) {
      toast.error("Full name and Email are required");
      return;
    }
    setAddUserLoading(true);
    try {
      await api.post("/api/v1/users/invite", {
        ...addUserForm,
        institution_id,
      });
      toast.success(`User invited successfully for ${institution?.institution_name}`);
      setShowAddUserModal(false);
      setAddUserForm({ full_name: "", email: "", role_name: "Institution Admin" });

      const [uRes, iRes] = await Promise.all([
        api.get("/api/v1/users", { params: { institution_id } }),
        api.get(`/api/v1/institutions/${institution_id}`),
      ]);
      setUsers(uRes.data);
      if (institution && iRes.status === 200) {
        setInstitution({ ...institution, user_count: iRes.data.user_count });
      }
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to add user"));
    } finally {
      setAddUserLoading(false);
    }
  }

  async function handleAdminResetPassword() {
    if (!resetPwUser) return;
    setResetPwLoading(true);
    try {
      const res = await api.post(`/api/v1/users/${resetPwUser.user_id}/reset-password`, {
        new_password: customNewPw.trim() || undefined,
      });
      toast.success(`Password for ${resetPwUser.full_name} reset to: "${res.data.new_password}"`);
      setResetPwUser(null);
      setCustomNewPw("");

      const uRes = await api.get("/api/v1/users", { params: { institution_id } });
      setUsers(uRes.data);
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to reset password"));
    }
    setResetPwLoading(false);
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
            className="btn btn-primary"
            onClick={() => setShowAddUserModal(true)}
            style={{ display: "flex", alignItems: "center", gap: 6 }}
          >
            <UserPlus size={15} /> Add User
          </button>
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
        <div style={{ display: "flex", borderBottom: "1px solid var(--border)", marginBottom: 20, justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex" }}>
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

          {activeTab === "users" && (
            <button
              className="btn btn-ghost"
              onClick={() => setShowAddUserModal(true)}
              style={{ fontSize: 13, display: "flex", alignItems: "center", gap: 5, padding: "6px 12px" }}
            >
              <Plus size={14} /> Add User to Institution
            </button>
          )}
        </div>

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Last Login</th><th>Created</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: "center", color: "var(--text-muted)", padding: 48 }}>
                      <Users size={36} style={{ marginBottom: 8, display: "block", margin: "0 auto 8px" }} />
                      <p style={{ margin: "0 0 12px" }}>No users registered for this institution yet.</p>
                      <button className="btn btn-primary" onClick={() => setShowAddUserModal(true)}>
                        + Add First User
                      </button>
                    </td>
                  </tr>
                ) : users.map((u) => (
                  <tr key={u.user_id}>
                    <td style={{ fontWeight: 500 }}>{u.full_name}</td>
                    <td style={{ fontSize: 13, color: "var(--text-secondary)" }}>{u.email}</td>
                    <td><span className="badge badge-draft">{u.role_name}</span></td>
                    <td><span className={`badge ${u.is_active ? "badge-compliant" : "badge-inactive"}`}>{u.is_active ? "Active" : "Inactive"}</span></td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{u.last_login ? new Date(u.last_login).toLocaleDateString("en-IN") : "Never"}</td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>{new Date(u.created_at).toLocaleDateString("en-IN")}</td>
                    <td>
                      <button
                        className="btn btn-ghost"
                        onClick={() => setResetPwUser(u)}
                        style={{ padding: "4px 8px", fontSize: 11, display: "flex", alignItems: "center", gap: 4, color: "var(--primary)" }}
                      >
                        <KeyRound size={11} /> Reset PW
                      </button>
                    </td>
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
                  <tr><th>Timestamp</th><th>User</th><th>Action</th><th>Entity</th><th>IP</th><th>MAC</th></tr>
                </thead>
                <tbody>
                  {auditLogs.length === 0 ? (
                    <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)", padding: 32 }}>No logs for this institution.</td></tr>
                  ) : auditLogs.slice(0, 50).map((log) => (
                    <tr key={log.audit_log_id}>
                      <td style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{new Date(log.created_at).toLocaleString("en-IN")}</td>
                      <td style={{ fontSize: 13 }}>{log.user_name ?? "System"}</td>
                      <td><span className="badge badge-draft">{ACTION_LABELS[log.action_type] ?? log.action_type}</span></td>
                      <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{log.entity_type ?? "—"}</td>
                      <td style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{log.ip_address ?? "—"}</td>
                      <td style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{log.mac_address ?? "—"}</td>
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

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="modal-overlay" onClick={() => setShowAddUserModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add User to {institution.institution_name}</h2>
              <button className="modal-close" onClick={() => setShowAddUserModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label className="form-label">Full Name *</label>
                <input
                  className="form-input"
                  placeholder="e.g. Dr. Rajesh Sharma"
                  value={addUserForm.full_name}
                  onChange={(e) => setAddUserForm({ ...addUserForm, full_name: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label className="form-label">Email Address *</label>
                <input
                  type="email"
                  className="form-input"
                  placeholder="e.g. rajesh.sharma@institution.ac.in"
                  value={addUserForm.email}
                  onChange={(e) => setAddUserForm({ ...addUserForm, email: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Role *</label>
                <select
                  className="form-input"
                  value={addUserForm.role_name}
                  onChange={(e) => setAddUserForm({ ...addUserForm, role_name: e.target.value })}
                >
                  {ASSIGNABLE_ROLES.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
              <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 12, marginBottom: 0 }}>
                🔑 Default password will be set to <code style={{ color: "var(--primary)" }}>Comply@2025</code>.
              </p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowAddUserModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAddUser} disabled={addUserLoading}>
                {addUserLoading ? "Adding User..." : "Add User"}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        open={confirmDeactivate}
        title={institution.is_active ? "Deactivate Institution" : "Activate Institution"}
        description={institution.is_active
          ? `Deactivating will prevent all users at "${institution.institution_name}" from logging in. Continue?`
          : `This will re-enable access for all users at "${institution.institution_name}". Continue?`}
        confirmLabel={institution.is_active ? "Deactivate" : "Activate"}
        confirmVariant={institution.is_active ? "destructive" : "default"}
        onConfirm={handleToggleStatus}
        onCancel={() => setConfirmDeactivate(false)}
      />

      {/* Admin Reset Password Modal */}
      {resetPwUser && (
        <div className="modal-overlay" onClick={() => setResetPwUser(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Reset Password — {resetPwUser.full_name}</h2>
              <button className="modal-close" onClick={() => setResetPwUser(null)}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: "0 0 16px" }}>
                Resetting password for <strong style={{ color: "var(--text-primary)" }}>{resetPwUser.email}</strong>.
              </p>

              <div className="form-group">
                <label className="form-label">New Password (optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Default: Comply@2025"
                  value={customNewPw}
                  onChange={(e) => setCustomNewPw(e.target.value)}
                />
                <span className="form-help" style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6, display: "block" }}>
                  Leave blank to reset password to default <code style={{ color: "var(--primary)" }}>Comply@2025</code>.
                </span>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setResetPwUser(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAdminResetPassword} disabled={resetPwLoading}>
                {resetPwLoading ? "Resetting..." : "Reset Password"}
              </button>
            </div>
          </div>
        </div>
      )}
    </PageShell>
  );
}
