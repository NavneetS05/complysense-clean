// Use: Onboarding form for registering vendor organizations.

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Save, Info, Building2, ShieldCheck } from "lucide-react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";

const CATEGORIES = [
  { value: "cloud", label: "Cloud Infrastructure" },
  { value: "saas", label: "SaaS Application" },
  { value: "payment", label: "Payment Gateway" },
  { value: "data_processor", label: "Data Processor" },
  { value: "security", label: "Security & Operations" },
  { value: "other", label: "Other" },
];

export default function NewVendor() {
  const navigate = useNavigate();
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    vendor_name: "",
    product_name: "",
    vendor_category: "saas",
    processing_location: "",
    dpa_available: false,
    model_training_allowed: false,
    contract_expiry_date: "",
    contact_email: "",
  });

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!form.vendor_name.trim()) {
      toast.error("Vendor name is required.");
      return;
    }
    setSaving(true);
    try {
      const { data } = await api.post("/api/v1/vendors", {
        vendor_name: form.vendor_name.trim(),
        product_name: form.product_name.trim() || null,
        vendor_category: form.vendor_category || null,
        processing_location: form.processing_location.trim() || null,
        dpa_available: form.dpa_available,
        model_training_allowed: form.model_training_allowed,
        contract_expiry_date: form.contract_expiry_date || null,
        contact_email: form.contact_email.trim() || null,
      });
      toast.success("Vendor added successfully.");
      navigate(`/vendor/vendors/${data.vendor_id}`);
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to add vendor."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <PageShell
      title="Onboard New Vendor"
      subtitle="Register a third-party service provider and establish DPDP compliance posture."
      actions={
        <button className="btn btn-secondary" onClick={() => navigate("/vendor/dashboard")}>
          <ArrowLeft size={14} /> Back to Register
        </button>
      }
    >
      {/* Guidance Banner */}
      <div className="guidance-banner" style={{ maxWidth: 860 }}>
        <div className="guidance-header">
          <Info size={18} /> Vendor Onboarding Checklist
        </div>
        <div className="guidance-steps">
          <div className="guidance-step">
            <div className="guidance-step-num">1</div>
            <div>
              <strong style={{ display: "block", color: "var(--text-primary)" }}>Basic Details</strong>
              Vendor legal entity name & main software product.
            </div>
          </div>
          <div className="guidance-step">
            <div className="guidance-step-num">2</div>
            <div>
              <strong style={{ display: "block", color: "var(--text-primary)" }}>Data Residency</strong>
              Processing location & DPA agreement status.
            </div>
          </div>
          <div className="guidance-step">
            <div className="guidance-step-num">3</div>
            <div>
              <strong style={{ display: "block", color: "var(--text-primary)" }}>Risk Assessment</strong>
              Perform initial DPDP section 8 review after creation.
            </div>
          </div>
        </div>
      </div>

      <form className="card" onSubmit={handleSubmit} style={{ maxWidth: 860, padding: 24, display: "grid", gap: 24 }}>
        {/* Section 1 */}
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, paddingBottom: 8, borderBottom: "1px solid var(--border)" }}>
            <Building2 size={16} style={{ color: "var(--primary)" }} />
            <h3 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>1. Vendor Identity & Contact</h3>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="vendor-name">Vendor Entity Name</label>
              <input
                id="vendor-name"
                className="form-input"
                value={form.vendor_name}
                onChange={(event) => setForm((current) => ({ ...current, vendor_name: event.target.value }))}
                placeholder="e.g. Amazon Web Services India Pvt Ltd"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="product-name">Product / Service Name</label>
              <input
                id="product-name"
                className="form-input"
                value={form.product_name}
                onChange={(event) => setForm((current) => ({ ...current, product_name: event.target.value }))}
                placeholder="e.g. AWS Cloud Hosting Services"
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="vendor-category">Vendor Category</label>
              <select
                id="vendor-category"
                className="filter-select"
                style={{ width: "100%" }}
                value={form.vendor_category}
                onChange={(event) => setForm((current) => ({ ...current, vendor_category: event.target.value }))}
              >
                {CATEGORIES.map((category) => (
                  <option key={category.value} value={category.value}>{category.label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="contact-email">Vendor Contact Email</label>
              <input
                id="contact-email"
                type="email"
                className="form-input"
                value={form.contact_email}
                onChange={(event) => setForm((current) => ({ ...current, contact_email: event.target.value }))}
                placeholder="compliance@vendor.com"
              />
            </div>
          </div>
        </div>

        {/* Section 2 */}
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, paddingBottom: 8, borderBottom: "1px solid var(--border)" }}>
            <ShieldCheck size={16} style={{ color: "var(--primary)" }} />
            <h3 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>2. DPDP Data Governance & Contract Posture</h3>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="processing-location">Data Processing Location</label>
              <input
                id="processing-location"
                className="form-input"
                value={form.processing_location}
                onChange={(event) => setForm((current) => ({ ...current, processing_location: event.target.value }))}
                placeholder="e.g. Mumbai (ap-south-1), India"
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="contract-expiry">Contract Expiry Date</label>
              <input
                id="contract-expiry"
                type="date"
                className="form-input"
                value={form.contract_expiry_date}
                onChange={(event) => setForm((current) => ({ ...current, contract_expiry_date: event.target.value }))}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: 24, flexWrap: "wrap", marginTop: 16, background: "var(--surface-secondary)", padding: 14, borderRadius: "var(--radius-md)" }}>
            <label style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 13, cursor: "pointer", fontWeight: 500 }}>
              <input
                type="checkbox"
                style={{ width: 16, height: 16, accentColor: "var(--primary)" }}
                checked={form.dpa_available}
                onChange={(event) => setForm((current) => ({ ...current, dpa_available: event.target.checked }))}
              />
              Data Processing Addendum (DPA) signed & available
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 13, cursor: "pointer", fontWeight: 500 }}>
              <input
                type="checkbox"
                style={{ width: 16, height: 16, accentColor: "var(--primary)" }}
                checked={form.model_training_allowed}
                onChange={(event) => setForm((current) => ({ ...current, model_training_allowed: event.target.checked }))}
              />
              Vendor is permitted to train AI models on institutional data
            </label>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, paddingTop: 12, borderTop: "1px solid var(--border)" }}>
          <button type="button" className="btn btn-secondary" onClick={() => navigate("/vendor/dashboard")}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            <Save size={14} /> {saving ? "Saving Vendor..." : "Save & Onboard Vendor"}
          </button>
        </div>
      </form>
    </PageShell>
  );
}
