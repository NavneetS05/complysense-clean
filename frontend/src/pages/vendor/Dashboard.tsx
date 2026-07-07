// Use: Vendor risk register listing all vendors with compliance status and DPA flags.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { Building2, AlertTriangle, CheckCircle, Shield, Plus, ChevronRight } from "lucide-react";

type Vendor = {
  vendor_id: string;
  vendor_name: string;
  product_name?: string | null;
  vendor_category?: string | null;
  processing_location?: string | null;
  dpa_available: boolean;
  risk_level?: string | null;
  dpdp_compliant?: boolean | null;
  contract_expiry_date?: string | null;
};

const RISK_COLORS: Record<string, { bg: string; text: string }> = {
  critical: { bg: "#FEF2F2", text: "#EF4444" },
  high:     { bg: "#FFF7ED", text: "#F97316" },
  medium:   { bg: "#FFFBEB", text: "#F59E0B" },
  low:      { bg: "#ECFDF5", text: "#10B981" },
};

export default function VendorDashboard() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/vendors");
        setVendors(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load vendors", err);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const filtered = vendors.filter((v) =>
    !search ||
    v.vendor_name.toLowerCase().includes(search.toLowerCase()) ||
    (v.vendor_category || "").toLowerCase().includes(search.toLowerCase())
  );

  const stats = {
    total: vendors.length,
    noDpa: vendors.filter((v) => !v.dpa_available).length,
    highRisk: vendors.filter((v) => v.risk_level === "critical" || v.risk_level === "high").length,
    expiringSoon: vendors.filter((v) => {
      if (!v.contract_expiry_date) return false;
      const diff = new Date(v.contract_expiry_date).getTime() - Date.now();
      return diff > 0 && diff < 90 * 24 * 3600 * 1000; // 90 days
    }).length,
  };

  return (
    <PageShell
      title="Vendor Risk Register"
      subtitle="Track third-party data processors and their compliance posture."
      actions={
        <Link to="/vendor/vendors/new" className="btn btn-primary" style={{ display: "inline-flex", alignItems: "center", gap: 6, textDecoration: "none" }}>
          <Plus size={14} /> Add Vendor
        </Link>
      }
    >
      <div className="page-panel" style={{ paddingBottom: 48 }}>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginTop: 20 }}>
        {[
          { label: "Total Vendors", value: stats.total, icon: Building2, color: "var(--primary)" },
          { label: "Missing DPA", value: stats.noDpa, icon: AlertTriangle, color: "var(--warning)" },
          { label: "High / Critical Risk", value: stats.highRisk, icon: Shield, color: "var(--critical)" },
          { label: "Expiring in 90d", value: stats.expiringSoon, icon: CheckCircle, color: "var(--success)" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div className="card" key={label} style={{ padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <Icon size={16} color={color} />
              <span style={{ fontSize: 12, color: "var(--muted)" }}>{label}</span>
            </div>
            <div style={{ fontSize: 26, fontWeight: 700 }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Search */}
      <div style={{ marginTop: 20, marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Search vendors by name or category..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: "100%", maxWidth: 400, padding: "8px 12px", borderRadius: 8, border: "1px solid var(--border)", fontSize: 13 }}
        />
      </div>

      {/* Vendor table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {loading ? (
          <div style={{ padding: 32, textAlign: "center", color: "var(--muted)" }}>Loading vendor register…</div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: 32, textAlign: "center", color: "var(--muted)" }}>
            No vendors found. <Link to="/vendor/vendors/new" style={{ color: "var(--primary)" }}>Add your first vendor.</Link>
          </div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--surface-raised)" }}>
                {["Vendor", "Category", "Data Location", "DPA", "DPDP", "Risk Level", ""].map((h) => (
                  <th key={h} style={{ padding: "10px 16px", textAlign: "left", fontSize: 11, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((v) => {
                const riskStyle = v.risk_level ? RISK_COLORS[v.risk_level] || RISK_COLORS.medium : null;
                return (
                  <tr key={v.vendor_id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{v.vendor_name}</div>
                      {v.product_name && <div style={{ fontSize: 12, color: "var(--muted)" }}>{v.product_name}</div>}
                    </td>
                    <td style={{ padding: "12px 16px", fontSize: 13, color: "var(--text-secondary)" }}>{v.vendor_category || "—"}</td>
                    <td style={{ padding: "12px 16px", fontSize: 13, color: "var(--text-secondary)" }}>{v.processing_location || "—"}</td>
                    <td style={{ padding: "12px 16px" }}>
                      {v.dpa_available
                        ? <CheckCircle size={16} color="var(--success)" />
                        : <AlertTriangle size={16} color="var(--warning)" />}
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      {v.dpdp_compliant === true
                        ? <CheckCircle size={16} color="var(--success)" />
                        : v.dpdp_compliant === false
                        ? <AlertTriangle size={16} color="var(--critical)" />
                        : <span style={{ fontSize: 12, color: "var(--muted)" }}>—</span>}
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      {riskStyle ? (
                        <span className="badge" style={{ backgroundColor: riskStyle.bg, color: riskStyle.text, fontWeight: 600, fontSize: 11 }}>
                          {v.risk_level!.toUpperCase()}
                        </span>
                      ) : (
                        <span style={{ fontSize: 12, color: "var(--muted)" }}>Not assessed</span>
                      )}
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <Link
                        to={`/vendor/vendors/${v.vendor_id}`}
                        className="btn btn-ghost btn-sm"
                        style={{ display: "inline-flex", alignItems: "center", gap: 4, textDecoration: "none" }}
                      >
                        Analyze <ChevronRight size={12} />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  </PageShell>
);
}
