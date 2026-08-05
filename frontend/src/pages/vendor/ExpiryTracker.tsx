// Use: Expiry tracker showing vendor contract and certification expiries.

import { useMemo } from "react";
import { Link } from "react-router-dom";
import { CalendarX, ChevronRight } from "lucide-react";
import { api } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import { PageShell } from "../../components/shared/PageShell";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";

type Vendor = {
  vendor_id: string;
  vendor_name: string;
  product_name?: string | null;
  vendor_category?: string | null;
  contract_expiry_date?: string | null;
  dpa_available?: boolean;
};

function daysUntil(date: string) {
  const end = new Date(date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);
  return Math.ceil((end.getTime() - today.getTime()) / (24 * 3600 * 1000));
}

function getBucket(days: number) {
  if (days < 0) return { key: "expired", label: "Already expired", className: "badge-non_compliant" };
  if (days <= 30) return { key: "30", label: "Expiring in 30 days", className: "badge-critical" };
  if (days <= 90) return { key: "90", label: "Expiring in 90 days", className: "badge-high" };
  return { key: "later", label: "Later", className: "badge-info" };
}

export default function ExpiryTracker() {
  const { data, loading, error, refetch } = useApi(async () => {
    const res = await api.get("/api/v1/vendors");
    return Array.isArray(res.data) ? res.data : res.data?.vendors ?? [];
  }, []);

  const vendors = useMemo(() => {
    return ((data ?? []) as Vendor[])
      .filter((vendor) => vendor.contract_expiry_date)
      .map((vendor) => {
        const days = daysUntil(vendor.contract_expiry_date!);
        return { ...vendor, days, bucket: getBucket(days) };
      })
      .sort((a, b) => a.days - b.days);
  }, [data]);

  const counts = {
    expired: vendors.filter((vendor) => vendor.bucket.key === "expired").length,
    soon30: vendors.filter((vendor) => vendor.bucket.key === "30").length,
    soon90: vendors.filter((vendor) => vendor.bucket.key === "90").length,
    later: vendors.filter((vendor) => vendor.bucket.key === "later").length,
  };

  return (
    <PageShell title="Expiry Tracker" subtitle="Prioritize vendor contracts by renewal and compliance urgency.">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(160px, 1fr))", gap: 12, marginBottom: 16 }}>
        {[
          ["Expired", counts.expired],
          ["Next 30 days", counts.soon30],
          ["Next 90 days", counts.soon90],
          ["Later", counts.later],
        ].map(([label, value]) => (
          <div className="card" key={label} style={{ padding: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)", fontSize: 12 }}>
              <CalendarX size={14} /> {label}
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, marginTop: 4 }}>{value}</div>
          </div>
        ))}
      </div>

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : vendors.length === 0 ? (
        <EmptyState title="No contract expiries" description="No vendors currently have a contract expiry date recorded." />
      ) : (
        <section className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Category</th>
                <th>Expiry</th>
                <th>Urgency</th>
                <th>DPA</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {vendors.map((vendor) => (
                <tr key={vendor.vendor_id}>
                  <td>
                    <div style={{ fontWeight: 700 }}>{vendor.vendor_name}</div>
                    {vendor.product_name && <div style={{ color: "var(--text-muted)", fontSize: 12 }}>{vendor.product_name}</div>}
                  </td>
                  <td>{vendor.vendor_category ?? "General"}</td>
                  <td>
                    {new Date(vendor.contract_expiry_date!).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    })}
                  </td>
                  <td><span className={`badge ${vendor.bucket.className}`}>{vendor.bucket.label}</span></td>
                  <td>{vendor.dpa_available ? "Available" : "Missing"}</td>
                  <td>
                    <Link className="btn btn-ghost btn-sm" to={`/vendor/vendors/${vendor.vendor_id}`}>
                      Open <ChevronRight size={12} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </PageShell>
  );
}
