// Use: Authenticated profile settings page backed by PATCH /auth/me.

import { useState } from "react";
import { PageShell } from "../components/shared/PageShell";
import { useAuthStore } from "../store/authStore";
import { fetchCurrentUser, persistSession, updateProfile, changePassword } from "../lib/auth";
import { useToast } from "../components/shared/ToastContext";
import { getApiErrorMessage } from "../lib/errors";
import { KeyRound, UserCheck, Lock } from "lucide-react";

export default function Profile() {
  const { user, updateUser } = useAuthStore();
  const toast = useToast();
  const [form, setForm] = useState({
    full_name: user?.full_name ?? "",
    phone: user?.phone ?? "",
    designation: user?.designation ?? "",
  });
  const [saving, setSaving] = useState(false);

  // Password state
  const [pwForm, setPwForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [pwSaving, setPwSaving] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await updateProfile({
        full_name: form.full_name.trim() || undefined,
        phone: form.phone.trim() || undefined,
        designation: form.designation.trim() || undefined,
      });
      const fresh = await fetchCurrentUser();
      updateUser(fresh);
      persistSession(fresh);
      toast.success("Profile updated successfully.");
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to update profile."));
    } finally {
      setSaving(false);
    }
  }

  async function handlePasswordChange(event: React.FormEvent) {
    event.preventDefault();
    if (!pwForm.current_password) {
      toast.error("Current password is required");
      return;
    }
    if (pwForm.new_password.length < 6) {
      toast.error("New password must be at least 6 characters");
      return;
    }
    if (pwForm.new_password !== pwForm.confirm_password) {
      toast.error("New password and confirmation do not match");
      return;
    }

    setPwSaving(true);
    try {
      await changePassword(pwForm.current_password, pwForm.new_password);
      toast.success("Password changed successfully! Use your new password on next login.");
      setPwForm({ current_password: "", new_password: "", confirm_password: "" });
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to change password."));
    } finally {
      setPwSaving(false);
    }
  }

  return (
    <PageShell title="Profile Settings" subtitle="Update your account details and security credentials.">
      <div style={{ maxWidth: 720, display: "grid", gap: 24 }}>
        {/* Profile Info Card */}
        <section className="card" style={{ padding: 24, display: "grid", gap: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, borderBottom: "1px solid var(--border)", paddingBottom: 12 }}>
            <UserCheck size={20} style={{ color: "var(--primary)" }} />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Personal Details</h3>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <div className="form-label">Email</div>
              <div style={{ fontWeight: 600 }}>{user?.email}</div>
            </div>
            <div>
              <div className="form-label">Institution</div>
              <div style={{ fontWeight: 600 }}>{user?.institution_name ?? "Not assigned"}</div>
            </div>
            <div>
              <div className="form-label">Role</div>
              <div style={{ fontWeight: 600 }}>{user?.active_role_name}</div>
            </div>
            <div>
              <div className="form-label">User ID</div>
              <code style={{ fontSize: 12, color: "var(--text-muted)" }}>{user?.user_id}</code>
            </div>
          </div>

          <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="profile-name">Full name</label>
              <input
                id="profile-name"
                className="form-input"
                value={form.full_name}
                onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="profile-phone">Phone</label>
              <input
                id="profile-phone"
                className="form-input"
                value={form.phone}
                onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="profile-designation">Designation</label>
              <input
                id="profile-designation"
                className="form-input"
                value={form.designation}
                onChange={(event) => setForm((current) => ({ ...current, designation: event.target.value }))}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving} style={{ justifySelf: "start" }}>
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </form>
        </section>

        {/* Security / Password Change Card */}
        <section className="card" style={{ padding: 24, display: "grid", gap: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, borderBottom: "1px solid var(--border)", paddingBottom: 12 }}>
            <KeyRound size={20} style={{ color: "var(--primary)" }} />
            <div>
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Security & Password</h3>
              <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--text-secondary)" }}>
                Update your login password
              </p>
            </div>
          </div>

          <form onSubmit={handlePasswordChange} style={{ display: "grid", gap: 16 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="current-password">Current Password *</label>
              <input
                id="current-password"
                type="password"
                className="form-input"
                placeholder="••••••••"
                value={pwForm.current_password}
                onChange={(e) => setPwForm({ ...pwForm, current_password: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="new-password">New Password *</label>
              <input
                id="new-password"
                type="password"
                className="form-input"
                placeholder="Minimum 6 characters"
                value={pwForm.new_password}
                onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirm-password">Confirm New Password *</label>
              <input
                id="confirm-password"
                type="password"
                className="form-input"
                placeholder="Re-enter new password"
                value={pwForm.confirm_password}
                onChange={(e) => setPwForm({ ...pwForm, confirm_password: e.target.value })}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={pwSaving} style={{ justifySelf: "start", display: "flex", alignItems: "center", gap: 6 }}>
              <Lock size={14} /> {pwSaving ? "Updating Password..." : "Update Password"}
            </button>
          </form>
        </section>
      </div>
    </PageShell>
  );
}
