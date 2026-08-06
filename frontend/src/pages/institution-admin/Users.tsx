// Use: Institution Admin — User Management. List, invite, deactivate, unlock, and change role for institution users.

import { useState, useEffect, useCallback } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";
import { UserPlus, Lock, Unlock, AlertCircle, KeyRound } from "lucide-react";

interface User {
  user_id: string;
  full_name: string;
  email: string;
  role_name: string;
  is_active: boolean;
  is_locked: boolean;
  last_login: string | null;
  created_at: string;
  department_name: string | null;
}

interface InviteForm {
  full_name: string;
  email: string;
  role_name: string;
  department_id?: string;
}

interface Department {
  department_id: string;
  department_name: string;
}

const ASSIGNABLE_ROLES = [
  "Institution Admin", "Compliance Officer", "IT Security Officer",
  "Auditor", "Department Reviewer", "Vendor Reviewer", "Policy Approver", "Read-Only Assessor",
];

const EMPTY_INVITE: InviteForm = { full_name: "", email: "", role_name: "Department Reviewer" };

export default function Users() {
  const toast = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  // Modals
  const [inviteModal, setInviteModal] = useState(false);
  const [roleModal, setRoleModal] = useState<{ open: boolean; user: User | null }>({ open: false, user: null });
  const [newRole, setNewRole] = useState("");
  const [confirmAction, setConfirmAction] = useState<{ user: User; action: "deactivate" | "activate" | "unlock" } | null>(null);
  const [resetPwUser, setResetPwUser] = useState<User | null>(null);
  const [customNewPw, setCustomNewPw] = useState("");
  const [resetPwLoading, setResetPwLoading] = useState(false);
  const [form, setForm] = useState<InviteForm>(EMPTY_INVITE);
  const [formErrors, setFormErrors] = useState<Partial<InviteForm>>({});
  const [modalLoading, setModalLoading] = useState(false);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (roleFilter !== "All") params.role = roleFilter;
    if (statusFilter !== "All") params.status = statusFilter;
    try {
      const res = await api.get("/api/v1/users", { params });
      setUsers(res.data);
    } catch { toast.error("Failed to load users"); }
    setLoading(false);
  }, [search, roleFilter, statusFilter, toast]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);
  useEffect(() => {
    api.get("/api/v1/departments").then((r) => setDepartments(r.data)).catch(() => {});
  }, []);

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
      fetchUsers();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to reset password"));
    }
    setResetPwLoading(false);
  }

  function validateInvite(): boolean {
    const errors: Partial<InviteForm> = {};
    if (!form.full_name.trim()) errors.full_name = "Name is required";
    if (!form.email.trim()) errors.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = "Invalid email format";
    if (!form.role_name) errors.role_name = "Role is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleInvite() {
    if (!validateInvite()) return;
    setModalLoading(true);
    try {
      await api.post("/api/v1/users/invite", form);
      toast.success("User invited — they will receive an email with login instructions");
      setInviteModal(false);
      setForm(EMPTY_INVITE);
      fetchUsers();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Invite failed"));
    }
    setModalLoading(false);
  }

  async function handleChangeRole() {
    if (!roleModal.user || !newRole) return;
    setModalLoading(true);
    try {
      await api.patch(`/api/v1/users/${roleModal.user.user_id}/role`, { role_name: newRole });
      toast.success("Role updated successfully");
      setRoleModal({ open: false, user: null });
      setNewRole("");
      fetchUsers();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to change role"));
    }
    setModalLoading(false);
  }

  async function handleConfirmAction() {
    if (!confirmAction) return;
    const { user, action } = confirmAction;
    try {
      if (action === "unlock") {
        await api.post(`/api/v1/users/${user.user_id}/unlock`);
        toast.success("Account unlocked");
      } else {
        await api.put(`/api/v1/users/${user.user_id}/status`, { is_active: action === "activate" });
        toast.success(`User ${action}d`);
      }
      setConfirmAction(null);
      fetchUsers();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Action failed"));
    }
  }

  return (
    <PageShell
      title="User Management"
      subtitle="Manage institution users, roles, and access"
      actions={
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY_INVITE); setFormErrors({}); setInviteModal(true); }} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <UserPlus size={15} /> Invite User
        </button>
      }
    >
      {/* Filters */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap" }}>
        <input className="form-input" placeholder="Search by name or email..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ flex: 1, minWidth: 200, fontSize: 13 }} />
        <select className="form-input" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} style={{ minWidth: 160, fontSize: 13 }}>
          <option value="All">All Roles</option>
          {ASSIGNABLE_ROLES.map((r) => <option key={r}>{r}</option>)}
        </select>
        <select className="form-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ minWidth: 130, fontSize: 13 }}>
          <option value="All">All Status</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
          <option value="Locked">Locked</option>
        </select>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>Name</th><th>Email</th><th>Role</th><th>Department</th><th>Status</th><th>Last Login</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i}>{Array.from({ length: 7 }).map((_, j) => <td key={j}><div className="skeleton" style={{ height: 18, borderRadius: 4 }} /></td>)}</tr>
                ))
              ) : users.length === 0 ? (
                <tr><td colSpan={7} style={{ textAlign: "center", color: "var(--text-muted)", padding: 40 }}>No users found.</td></tr>
              ) : users.map((u) => (
                <tr key={u.user_id}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--primary-bg)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, flexShrink: 0 }}>
                        {u.full_name.charAt(0).toUpperCase()}
                      </div>
                      <span style={{ fontWeight: 500 }}>{u.full_name}</span>
                    </div>
                  </td>
                  <td style={{ fontSize: 13, color: "var(--text-secondary)" }}>{u.email}</td>
                  <td><span className="badge badge-draft">{u.role_name}</span></td>
                  <td style={{ fontSize: 13, color: "var(--text-muted)" }}>{u.department_name ?? "—"}</td>
                  <td>
                    {u.is_locked ? (
                      <span className="badge badge-non_compliant" style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        <Lock size={10} /> Locked
                      </span>
                    ) : (
                      <span className={`badge ${u.is_active ? "badge-compliant" : "badge-inactive"}`}>
                        {u.is_active ? "Active" : "Inactive"}
                      </span>
                    )}
                  </td>
                  <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{u.last_login ? new Date(u.last_login).toLocaleDateString("en-IN") : "Never"}</td>
                  <td>
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                      <button className="btn btn-ghost" onClick={() => { setRoleModal({ open: true, user: u }); setNewRole(u.role_name); }} style={{ padding: "4px 8px", fontSize: 11 }}>
                        Change Role
                      </button>
                      <button className="btn btn-ghost" onClick={() => setResetPwUser(u)} style={{ padding: "4px 8px", fontSize: 11, display: "flex", alignItems: "center", gap: 4, color: "var(--primary)" }}>
                        <KeyRound size={11} /> Reset PW
                      </button>
                      {u.is_locked && (
                        <button className="btn btn-ghost" onClick={() => setConfirmAction({ user: u, action: "unlock" })} style={{ padding: "4px 8px", fontSize: 11, display: "flex", alignItems: "center", gap: 4 }}>
                          <Unlock size={11} /> Unlock
                        </button>
                      )}
                      <button
                        className="btn btn-ghost"
                        onClick={() => setConfirmAction({ user: u, action: u.is_active ? "deactivate" : "activate" })}
                        style={{ padding: "4px 8px", fontSize: 11, color: u.is_active ? "var(--danger)" : "var(--success)" }}
                      >
                        {u.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invite Modal */}
      {inviteModal && (
        <div className="modal-overlay" onClick={() => setInviteModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Invite New User</h2>
              <button className="modal-close" onClick={() => setInviteModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="card" style={{ background: "var(--info-bg)", border: "1px solid var(--info)", padding: "12px 16px", borderRadius: 8, marginBottom: 16, display: "flex", alignItems: "flex-start", gap: 10 }}>
                <AlertCircle size={16} style={{ color: "var(--info)", flexShrink: 0, marginTop: 2 }} />
                <p style={{ margin: 0, fontSize: 13, color: "var(--text-secondary)" }}>
                  An email will be sent with a secure invitation link. The user will set their own password on first login.
                </p>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Full Name *</label>
                  <input className={`form-input ${formErrors.full_name ? "input-error" : ""}`} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="e.g. Priya Sharma" />
                  {formErrors.full_name && <span className="form-error">{formErrors.full_name}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">Email Address *</label>
                  <input type="email" className={`form-input ${formErrors.email ? "input-error" : ""}`} value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="user@institution.ac.in" />
                  {formErrors.email && <span className="form-error">{formErrors.email}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">Role *</label>
                  <select className={`form-input ${formErrors.role_name ? "input-error" : ""}`} value={form.role_name} onChange={(e) => setForm({ ...form, role_name: e.target.value })}>
                    {ASSIGNABLE_ROLES.map((r) => <option key={r}>{r}</option>)}
                  </select>
                  {formErrors.role_name && <span className="form-error">{formErrors.role_name}</span>}
                </div>
                {form.role_name === "Department Reviewer" && (
                  <div className="form-group">
                    <label className="form-label">Assign to Department</label>
                    <select className="form-input" value={form.department_id ?? ""} onChange={(e) => setForm({ ...form, department_id: e.target.value })}>
                      <option value="">— Select department (optional) —</option>
                      {departments.map((d) => <option key={d.department_id} value={d.department_id}>{d.department_name}</option>)}
                    </select>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setInviteModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleInvite} disabled={modalLoading}>
                {modalLoading ? "Sending..." : "Send Invitation"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Change Role Modal */}
      {roleModal.open && roleModal.user && (
        <div className="modal-overlay" onClick={() => setRoleModal({ open: false, user: null })}>
          <div className="modal" style={{ maxWidth: 420 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Change Role</h2>
              <button className="modal-close" onClick={() => setRoleModal({ open: false, user: null })}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
                Changing the role of <strong>{roleModal.user.full_name}</strong> will affect their access immediately.
              </p>
              <div className="form-group">
                <label className="form-label">New Role</label>
                <select className="form-input" value={newRole} onChange={(e) => setNewRole(e.target.value)}>
                  {ASSIGNABLE_ROLES.map((r) => <option key={r}>{r}</option>)}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setRoleModal({ open: false, user: null })}>Cancel</button>
              <button className="btn btn-primary" onClick={handleChangeRole} disabled={!newRole || newRole === roleModal.user.role_name || modalLoading}>
                {modalLoading ? "Updating..." : "Update Role"}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        open={!!confirmAction}
        title={
          confirmAction?.action === "unlock" ? "Unlock Account" :
          confirmAction?.action === "deactivate" ? "Deactivate User" : "Activate User"
        }
        description={
          confirmAction?.action === "unlock"
            ? `Unlock "${confirmAction.user.full_name}"'s account? They will be able to log in again.`
            : confirmAction?.action === "deactivate"
            ? `Deactivating "${confirmAction.user.full_name}" will prevent them from logging in immediately.`
            : confirmAction
            ? `Activating "${confirmAction.user.full_name}" will restore their login access.`
            : ""
        }
        confirmLabel={confirmAction?.action === "unlock" ? "Unlock" : confirmAction?.action === "deactivate" ? "Deactivate" : "Activate"}
        confirmVariant={confirmAction?.action === "deactivate" ? "destructive" : "default"}
        onConfirm={handleConfirmAction}
        onCancel={() => setConfirmAction(null)}
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
