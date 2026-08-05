// Use: Super Admin — Tenant Manager. List, create, activate/deactivate institutions.

import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { ConfirmModal } from "../../components/shared/ConfirmModal";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";
import { Plus, Eye, Building2 } from "lucide-react";

interface Institution {
  institution_id: string;
  institution_name: string;
  institution_type: string;
  city: string;
  state: string;
  staff_count: number;
  is_active: boolean;
  created_at: string;
}

const INDIAN_STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
  "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
  "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
  "Uttarakhand","West Bengal","Delhi","Jammu and Kashmir","Ladakh","Chandigarh",
  "Puducherry","Lakshadweep","Dadra and Nagar Haveli","Daman and Diu","Andaman and Nicobar Islands"
];

const INST_TYPES = ["University", "College", "Institute"];

interface InstitutionFormData {
  institution_name: string;
  institution_type: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  staff_count: string;
}

const EMPTY_FORM: InstitutionFormData = {
  institution_name: "", institution_type: "University", email: "",
  phone: "", address: "", city: "", state: "", staff_count: "",
};

export default function Tenants() {
  const toast = useToast();
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");
  const [stateFilter, setStateFilter] = useState("All");

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [form, setForm] = useState<InstitutionFormData>(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState<Partial<InstitutionFormData>>({});

  // Confirm modal
  const [confirmTarget, setConfirmTarget] = useState<Institution | null>(null);

  const fetchInstitutions = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (statusFilter !== "All") params.status = statusFilter;
      if (typeFilter !== "All") params.type = typeFilter;
      if (stateFilter !== "All") params.state = stateFilter;
      const res = await api.get("/api/v1/institutions", { params });
      setInstitutions(res.data);
    } catch {
      toast.error("Failed to load institutions");
    }
    setLoading(false);
  }, [search, statusFilter, typeFilter, stateFilter, toast]);

  useEffect(() => { fetchInstitutions(); }, [fetchInstitutions]);

  function validateForm(): boolean {
    const errors: Partial<InstitutionFormData> = {};
    if (!form.institution_name.trim()) errors.institution_name = "Name is required";
    if (!form.city.trim()) errors.city = "City is required";
    if (!form.state) errors.state = "State is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleCreate() {
    if (!validateForm()) return;
    setModalLoading(true);
    try {
      await api.post("/api/v1/institutions", {
        ...form,
        staff_count: form.staff_count ? parseInt(form.staff_count) : 0,
      });
      toast.success("Institution created successfully");
      setShowModal(false);
      setForm(EMPTY_FORM);
      fetchInstitutions();
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to create institution"));
    }
    setModalLoading(false);
  }

  async function handleToggleStatus() {
    if (!confirmTarget) return;
    try {
      await api.put(`/api/v1/institutions/${confirmTarget.institution_id}/status`, {
        is_active: !confirmTarget.is_active,
      });
      toast.success(`Institution ${confirmTarget.is_active ? "deactivated" : "activated"} successfully`);
      setConfirmTarget(null);
      fetchInstitutions();
    } catch {
      toast.error("Failed to update status");
    }
  }

  return (
    <PageShell
      title="Institutions"
      subtitle="Manage all registered tenants on the platform"
      actions={
        <button className="btn btn-primary" onClick={() => setShowModal(true)} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Plus size={15} /> Add Institution
        </button>
      }
    >
      {/* Filter Row */}
      <div className="filter-bar" style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 20 }}>
        <input
          className="form-input"
          placeholder="Search by name or city..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 200, fontSize: 13 }}
        />
        <select className="form-input" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} style={{ fontSize: 13, minWidth: 130 }}>
          <option value="All">All Types</option>
          {INST_TYPES.map((t) => <option key={t}>{t}</option>)}
        </select>
        <select className="form-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ fontSize: 13, minWidth: 120 }}>
          <option value="All">All Status</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </select>
        <select className="form-input" value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} style={{ fontSize: 13, minWidth: 150 }}>
          <option value="All">All States</option>
          {INDIAN_STATES.map((s) => <option key={s}>{s}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th><th>Type</th><th>City, State</th><th>Staff</th><th>Status</th><th>Created</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j}><div className="skeleton" style={{ height: 18, borderRadius: 4 }} /></td>
                    ))}
                  </tr>
                ))
              ) : institutions.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: "48px 16px" }}>
                    <Building2 size={36} style={{ color: "var(--text-muted)", marginBottom: 10, display: "block", margin: "0 auto 10px" }} />
                    <p style={{ color: "var(--text-muted)", margin: 0, fontSize: 14 }}>No institutions found.</p>
                  </td>
                </tr>
              ) : institutions.map((inst) => (
                <tr key={inst.institution_id}>
                  <td>
                    <Link to={`/super-admin/tenants/${inst.institution_id}`} style={{ fontWeight: 600, color: "var(--primary)" }}>
                      {inst.institution_name}
                    </Link>
                  </td>
                  <td><span className="badge badge-draft">{inst.institution_type}</span></td>
                  <td style={{ color: "var(--text-secondary)", fontSize: 13 }}>{inst.city}, {inst.state}</td>
                  <td>{inst.staff_count ?? "—"}</td>
                  <td>
                    <span className={`badge ${inst.is_active ? "badge-compliant" : "badge-inactive"}`}>
                      {inst.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                    {new Date(inst.created_at).toLocaleDateString("en-IN")}
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: 6 }}>
                      <Link to={`/super-admin/tenants/${inst.institution_id}`} className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <Eye size={12} /> View
                      </Link>
                      <button
                        className={`btn ${inst.is_active ? "btn-ghost" : "btn-primary"}`}
                        onClick={() => setConfirmTarget(inst)}
                        style={{ padding: "4px 10px", fontSize: 12 }}
                      >
                        {inst.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Institution Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add New Institution</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="grid-2" style={{ gap: 16 }}>
                <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                  <label className="form-label">Institution Name *</label>
                  <input className={`form-input ${formErrors.institution_name ? "input-error" : ""}`} value={form.institution_name} onChange={(e) => setForm({ ...form, institution_name: e.target.value })} placeholder="e.g. Jaipur National University" />
                  {formErrors.institution_name && <span className="form-error">{formErrors.institution_name}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">Type *</label>
                  <select className="form-input" value={form.institution_type} onChange={(e) => setForm({ ...form, institution_type: e.target.value })}>
                    {INST_TYPES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Staff Count</label>
                  <input type="number" className="form-input" value={form.staff_count} onChange={(e) => setForm({ ...form, staff_count: e.target.value })} placeholder="e.g. 500" />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input type="email" className="form-input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="admin@institution.ac.in" />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone</label>
                  <input className="form-input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+91 98765 43210" />
                </div>
                <div className="form-group">
                  <label className="form-label">City *</label>
                  <input className={`form-input ${formErrors.city ? "input-error" : ""}`} value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="e.g. Jaipur" />
                  {formErrors.city && <span className="form-error">{formErrors.city}</span>}
                </div>
                <div className="form-group">
                  <label className="form-label">State *</label>
                  <select className={`form-input ${formErrors.state ? "input-error" : ""}`} value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })}>
                    <option value="">Select State</option>
                    {INDIAN_STATES.map((s) => <option key={s}>{s}</option>)}
                  </select>
                  {formErrors.state && <span className="form-error">{formErrors.state}</span>}
                </div>
                <div className="form-group" style={{ gridColumn: "1 / -1" }}>
                  <label className="form-label">Address</label>
                  <textarea className="form-input" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} rows={2} placeholder="Full postal address" />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={modalLoading}>
                {modalLoading ? "Creating..." : "Create Institution"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Deactivate Confirm */}
      <ConfirmModal
        open={!!confirmTarget}
        title={confirmTarget?.is_active ? "Deactivate Institution" : "Activate Institution"}
        description={confirmTarget ? (confirmTarget.is_active
          ? `Deactivating will prevent all users at "${confirmTarget.institution_name}" from logging in. Continue?`
          : `This will re-enable access for all users at "${confirmTarget.institution_name}". Continue?`) : ""}
        confirmLabel={confirmTarget?.is_active ? "Deactivate" : "Activate"}
        confirmVariant={confirmTarget?.is_active ? "destructive" : "default"}
        onConfirm={handleToggleStatus}
        onCancel={() => setConfirmTarget(null)}
      />
    </PageShell>
  );
}
