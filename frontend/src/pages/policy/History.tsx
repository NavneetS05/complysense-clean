// Use: History page listing all organizational policies previously approved or rejected.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../PageShell";
import { FileText, CheckCircle, XCircle, Eye } from "lucide-react";

type Policy = {
  policy_id: string;
  policy_name: string;
  version_number: number;
  policy_status: string;
  related_control_id?: string | null;
  created_at: string;
};

export default function History() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/policies");
        setPolicies(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load policy history", err);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const historyPolicies = policies.filter(
    (p) => p.policy_status === "approved" || p.policy_status === "rejected"
  );

  return (
    <div className="page-panel">
      <PageShell title="Policy Review History" context="Archived decisions and past review audits." />
      
      {loading ? (
        <p style={{ marginTop: 20 }}>Loading policy archive…</p>
      ) : (
        <div style={{ marginTop: 24, display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 20 }}>
            <h3 style={{ marginTop: 0, marginBottom: 16 }}>Decision Archive</h3>
            
            {historyPolicies.length === 0 ? (
              <p style={{ color: "var(--muted)", margin: 0, fontSize: 13 }}>
                No completed reviews in history.
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {historyPolicies.map((policy) => {
                  const isApproved = policy.policy_status === "approved";
                  return (
                    <div
                      key={policy.policy_id}
                      style={{
                        border: "1px solid var(--border)",
                        borderRadius: 10,
                        padding: 16,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        background: "var(--surface)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: 8,
                            backgroundColor: isApproved ? "#E8F8F0" : "#FEECEB",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: isApproved ? "#10B981" : "#EF4444",
                          }}
                        >
                          {isApproved ? <CheckCircle size={18} /> : <XCircle size={18} />}
                        </div>
                        <div>
                          <strong style={{ display: "block", fontSize: 14 }}>{policy.policy_name}</strong>
                          <span style={{ fontSize: 12, color: "var(--muted)" }}>
                            v{policy.version_number} · Control: {policy.related_control_id || "None"} · Audited on {new Date(policy.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <Link
                        to={`/policy/${policy.policy_id}/review`}
                        className="btn btn-secondary btn-sm"
                        style={{ display: "inline-flex", alignItems: "center", gap: 4, textDecoration: "none" }}
                      >
                        <Eye size={12} /> View Details
                      </Link>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
