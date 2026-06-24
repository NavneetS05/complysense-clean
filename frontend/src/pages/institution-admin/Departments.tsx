// Use: Institution Admin — Department Manager. List, create, edit, assign reviewer, and toggle status.

import { useState, useEffect, useCallback } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { useToast } from "../../components/shared/Toast";
import { Plus, Edit, UserCheck, Building2 } from "lucide-react";

interface Department {
  department_id: string;
  department_name: string;
  department_code: string | null;
  hod_name: string | null;
  reviewer_user_id: string | null;
  reviewer_name: string | null;
  reviewer_email: string | null;
  is_active: boolean;
}

interface ReviewerUser {
  user_id: string;
  full_name: string;
  email: string;
}

interface DeptForm {
  department_name: string;
  department_code: string;
  hod_name: string;
}

const EMPTY_DEPT_FORM: DeptForm = { department_name: "", department_code: "", hod_name: "" };

export default function Departments() {
  const { showToast } = useToast();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [reviewerUsers, setReviewerUsers] = useState<ReviewerUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  // Modals
  const [deptModal, setDeptModal] = useState<{ open: boolean; editTarget: Department | null }>({ open: false, editTarget: null });
  const [reviewerModal, setReviewerModal] = useState<{ open: boolean; dept: Department | null }>({ open: false, dept: null });
  const [confirmToggle, setConfirmToggle] = useState<Department | null>(null);
  const [form, setForm] = useState<DeptForm>(EMPTY_DEPT_FORM);
  const [selectedReviewer, setSelectedReviewer] = useState("");
  const [formErrors, setFormErrors] = useState<Partial<DeptForm>>({});
  const [modalLoading, setModalLoading] = useState(false);

  const fetchDepartments = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (statusFilter !== "All") params.status = statusFilter;
      if (search) params.search = search;
      const res = await api.get("/api/v1/departments", { params });
      setDepartments(res.data);
    } catch { showToast("Failed to load departments", "error"); }
    setLoading(false);
  }, [search, statusFilter]);

  useEffect(() => { fetchDepartments(); }, [fetchDepartments]);

  useEffect(() => {
    api.get("/api/v1/users", { params: { role: "Department Reviewer" } })
      .then((r) => setReviewerUsers(r.data))
      .catch(() => {});
  }, []);

  function openAddModal() {
    setForm(EMPTY_DEPT_FORM);
    setFormErrors({});
    setDeptModal({ open: true, editTarget: null });
  }

  function openEditModal(dept: Department) {
    setForm({ department_name: dept.department_name, department_code: dept.department_code ?? "", hod_name: dept.hod_name ?? "" });
    setFormErrors({});
    setDeptModal({ open: true, editTarget: dept });
  }

  function validateForm(): boolean {
    const errors: Partial<DeptForm> = {};
    if (!form.department_name.trim()) errors.department_name = "Department name is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    if (!validateForm()) return;
    setModalLoading(true);
    try {
      if (deptModal.editTarget) {
        await api.patch(`/api/v1/departments/${deptModal.editTarget.department_id}`, form);
        showToast("Department updated", "success");
      } else {
        await api.post("/api/v1/departments", form);
        showToast("Department created", "success");
      }
      setDeptModal({ open: false, editTarget: null });
      fetchDepartments();
    } catch (err: any) {
      showToast(err?.response?.data?.detail ?? "Operation failed", "error");
    }
    setModalLoading(false);
  }

  async function handleAssignReviewer() {
    if (!reviewerModal.dept || !selectedReviewer) return;
    setModalLoading(true);
    try {
      await api.patch(`/api/v1/departments/${reviewerModal.dept.department_id}`, { reviewer_user_id: selectedReviewer });
      showToast("Reviewer assigned successfully", "success");
      setReviewerModal({ open: false, dept: null });
      setSelectedReviewer("");
      fetchDepartments();
    } catch (err: any) {
      showToast(err?.response?.data?.detail ?? "Failed to assign reviewer", "error");
    }
    setModalLoading(false);
  }

  async function handleToggleStatus() {
    if (!confirmToggle) return;
    try {
      await api.put(`/api/v1/departments/${confirmToggle.department_id}/status`, { is_active: !confirmToggle.is_active });
      showToast(`Department ${confirmToggle.is_active ? "deactivated" : "activated"}`, "success");
      setConfirmToggle(null);
      fetchDepartments();
    } catch { showToast("Failed to update status", "error"); }
  }

  return (
    <PageShell
      title="Departments"
      subtitle="Manage academic and administrative departments"
      actions={
        <button className="btn btn-primary" onClick={openAddModal} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Plus size={15} /> Add Department
        </button>
      }
    >
      {/* Filter Row */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <input className="form-input" placeholder="Search by name or code..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ flex: 1, fontSize: 13 }} />
        <select className="form-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ minWidth: 130, fontSize: 13 }}>
          <option value="All">All Status</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </select>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>Department Name</th><th>Code</th><th>HOD Name</th><th>Assigned Reviewer</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>{Array.from({ length: 6 }).map((_, j) => <td key={j}><div className="skeleton" style={{ height: 18, borderRadius: 4 }} /></td>)}</tr>
                ))
              ) : departments.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "48px 16px" }}>
                    <Building2 size={36} style={{ color: "var(--text-muted)", display: "block", margin: "0 auto 10px" }} />
                    <p style={{ color: "var(--text-muted)", margin: 0, fontSize: 14 }}>No departments created yet.</p>
                    <button className="btn btn-primary" onClick={openAddModal} style={{ marginTop: 12, display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <Plus size={14} /> Add Department
                    </button>
                  </td>
                </tr>
              ) : departments.map((dept) => (
                <tr key={dept.department_id}>
                  <td style={{ fontWeight: 500 }}>{dept.department_name}</td>
                  <td><code style={{ fontSize: 12, color: "var(--text-muted)" }}>{dept.department_code ?? "—"}</code></td>
                  <td>{dept.hod_name ?? "—"}</td>
                  <td>
                    {dept.reviewer_name ? (
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 500 }}>{dept.reviewer_name}</div>
                        <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{dept.reviewer_email}</div>
                      </div>
                    ) : (
                      <span style={{ color: "var(--warning)", fontSize: 13, fontStyle: "italic" }}>Unassigned</span>
                    )}
                  </td>
                  <td><span className={`badge ${dept.is_active ? "badge-compliant" : "badge-inactive"}`}>{dept.is_active ? "Active" : "Inactive"}</span></td>
                  <td>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-ghost" onClick={() => openEditModal(dept)} style={{ padding: "4px 10px", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <Edit size={12} /> Edit
                      </button>
                      <button className="btn btn-ghost" onClick={() => { setReviewerModal({ open: true, dept }); setSelectedReviewer(dept.reviewer_user_id ?? ""); }} style={{ padding: "4px 10px", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <UserCheck size={12} /> {dept.reviewer_user_id ? "Change" : "Assign"} Reviewer
                      </button>
                      <button className="btn btn-ghost" onClick={() => setConfirmToggle(dept)} style={{ padding: "4px 10px", fontSize: 12, color: dept.is_active ? "var(--danger)" : "var(--success)" }}>
                        {dept.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Department Modal */}
      {deptModal.open && (
        <div className="modal-overlay" onClick={() => setDeptModal({ open: false, editTarget: null })}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{deptModal.editTarget ? "Edit Department" : "Add Department"}</h2>
              <button className="modal-close" onClick={() => setDeptModal({ open: false, editTarget: null })}>×</button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Department Name *</label>
                  <input className={`form-input ${formErrors.department_name ? "input-error" : ""}`} value={form.department_name} onChange={(e) => setForm({ ...form, department_name: e.target.value })} placeholder="e.g. Computer Science" />
                  {formErrors.department_name && <span className="form-error">{formErrors.department_name}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">Department Code</label>
                  <input className="form-input" value={form.department_code} onChange={(e) => setForm({ ...form, department_code: e.target.value })} placeholder="e.g. CS, ADMIN, FIN" />
                </div>
                <div className="form-group">
                  <label className="form-label">Head of Department (HOD)</label>
                  <input className="form-input" value={form.hod_name} onChange={(e) => setForm({ ...form, hod_name: e.target.value })} placeholder="e.g. Prof. Ramesh Kumar" />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setDeptModal({ open: false, editTarget: null })}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSave} disabled={modalLoading}>
                {modalLoading ? "Saving..." : deptModal.editTarget ? "Save Changes" : "Create Department"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Reviewer Modal */}
      {reviewerModal.open && reviewerModal.dept && (
        <div className="modal-overlay" onClick={() => setReviewerModal({ open: false, dept: null })}>
          <div className="modal" style={{ maxWidth: 440 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Assign Department Reviewer</h2>
              <button className="modal-close" onClick={() => setReviewerModal({ open: false, dept: null })}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
                Select a user with <strong>Department Reviewer</strong> role to assign to <strong>{reviewerModal.dept.department_name}</strong>
              </p>
              <div className="form-group">
                <label className="form-label">Reviewer</label>
                <select className="form-input" value={selectedReviewer} onChange={(e) => setSelectedReviewer(e.target.value)}>
                  <option value="">Select reviewer...</option>
                  {reviewerUsers.map((u) => (
                    <option key={u.user_id} value={u.user_id}>{u.full_name} — {u.email}</option>
                  ))}
                </select>
                {reviewerUsers.length === 0 && (
                  <p style={{ fontSize: 12, color: "var(--warning)", marginTop: 6 }}>No Department Reviewer users found. Create one first in User Management.</p>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setReviewerModal({ open: false, dept: null })}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAssignReviewer} disabled={!selectedReviewer || modalLoading}>
                {modalLoading ? "Assigning..." : "Assign"}
              </button>
            </div>
          </div>
        </div>
      )}

      {confirmToggle && (
        <ConfirmModal
          title={confirmToggle.is_active ? "Deactivate Department" : "Activate Department"}
          description={`Are you sure you want to ${confirmToggle.is_active ? "deactivate" : "activate"} "${confirmToggle.department_name}"?`}
          confirmLabel={confirmToggle.is_active ? "Deactivate" : "Activate"}
          variant={confirmToggle.is_active ? "destructive" : "default"}
          onConfirm={handleToggleStatus}
          onCancel={() => setConfirmToggle(null)}
        />
      )}
    </PageShell>
  );
}
