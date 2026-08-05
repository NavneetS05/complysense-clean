// Use: Authenticated profile settings page backed by PATCH /auth/me.

import { useState } from "react";
import { PageShell } from "../components/shared/PageShell";
import { useAuthStore } from "../store/authStore";
import { fetchCurrentUser, persistSession, updateProfile } from "../lib/auth";
import { useToast } from "../components/shared/ToastContext";
import { getApiErrorMessage } from "../lib/errors";

export default function Profile() {
  const { user, updateUser } = useAuthStore();
  const toast = useToast();
  const [form, setForm] = useState({
    full_name: user?.full_name ?? "",
    phone: user?.phone ?? "",
    designation: user?.designation ?? "",
  });
  const [saving, setSaving] = useState(false);

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

  return (
    <PageShell title="Profile Settings" subtitle="Update your account details and institutional context.">
      <section className="card" style={{ maxWidth: 720, padding: 20, display: "grid", gap: 20 }}>
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
    </PageShell>
  );
}
