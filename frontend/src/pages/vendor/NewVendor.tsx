// Use: Onboarding form for registering vendor organizations.

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Save } from "lucide-react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";

const CATEGORIES = [
  { value: "cloud", label: "Cloud" },
  { value: "saas", label: "SaaS" },
  { value: "payment", label: "Payment" },
  { value: "data_processor", label: "Data Processor" },
  { value: "security", label: "Security" },
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
      title="Onboard Vendor"
      subtitle="Register a third-party provider and capture initial contract posture."
      actions={
        <button className="btn btn-ghost" onClick={() => navigate("/vendor/dashboard")}>
          <ArrowLeft size={14} /> Back
        </button>
      }
    >
      <form className="card" onSubmit={handleSubmit} style={{ maxWidth: 860, padding: 20, display: "grid", gap: 18 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="form-group">
            <label className="form-label" htmlFor="vendor-name">Vendor name *</label>
            <input
              id="vendor-name"
              className="form-input"
              value={form.vendor_name}
              onChange={(event) => setForm((current) => ({ ...current, vendor_name: event.target.value }))}
              placeholder="e.g. Acme Cloud Services"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="product-name">Product or service</label>
            <input
              id="product-name"
              className="form-input"
              value={form.product_name}
              onChange={(event) => setForm((current) => ({ ...current, product_name: event.target.value }))}
              placeholder="e.g. Learning platform"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="vendor-category">Category</label>
            <select
              id="vendor-category"
              className="form-input"
              value={form.vendor_category}
              onChange={(event) => setForm((current) => ({ ...current, vendor_category: event.target.value }))}
            >
              {CATEGORIES.map((category) => (
                <option key={category.value} value={category.value}>{category.label}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="processing-location">Processing location</label>
            <input
              id="processing-location"
              className="form-input"
              value={form.processing_location}
              onChange={(event) => setForm((current) => ({ ...current, processing_location: event.target.value }))}
              placeholder="e.g. India, Singapore"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="contract-expiry">Contract expiry date</label>
            <input
              id="contract-expiry"
              type="date"
              className="form-input"
              value={form.contract_expiry_date}
              onChange={(event) => setForm((current) => ({ ...current, contract_expiry_date: event.target.value }))}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="contact-email">Contact email</label>
            <input
              id="contact-email"
              type="email"
              className="form-input"
              value={form.contact_email}
              onChange={(event) => setForm((current) => ({ ...current, contact_email: event.target.value }))}
              placeholder="security@vendor.com"
            />
          </div>
        </div>

        <div style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
            <input
              type="checkbox"
              checked={form.dpa_available}
              onChange={(event) => setForm((current) => ({ ...current, dpa_available: event.target.checked }))}
            />
            DPA available
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
            <input
              type="checkbox"
              checked={form.model_training_allowed}
              onChange={(event) => setForm((current) => ({ ...current, model_training_allowed: event.target.checked }))}
            />
            Allows model training on institutional data
          </label>
        </div>

        <button type="submit" className="btn btn-primary" disabled={saving} style={{ justifySelf: "start" }}>
          <Save size={14} /> {saving ? "Saving..." : "Save Vendor"}
        </button>
      </form>
    </PageShell>
  );
}
