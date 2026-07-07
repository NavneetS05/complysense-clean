// Use: Inbox page listing all policy drafts submitted to the current approver for review.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";
import { PageShell } from "../PageShell";
import { FileText, Clock, AlertCircle, CheckCircle, ChevronRight, Eye } from "lucide-react";

type Policy = {
  policy_id: string;
  policy_name: string;
  version_number: number;
  policy_status: string;
  related_control_id?: string | null;
  created_at: string;
};

export default function Inbox() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/policies");
        // List all policies that are submitted/pending approval
        setPolicies(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load policy inbox", err);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const pendingPolicies = policies.filter(
    (p) => p.policy_status === "pending_approval" || p.policy_status === "draft"
  );

  const getStatusStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
        return { bg: "#ECFDF5", text: "#10B981" };
      case "rejected":
        return { bg: "#FEF2F2", text: "#EF4444" };
      case "pending_approval":
      case "submitted":
        return { bg: "#FFFBEB", text: "#F59E0B" };
      default:
        return { bg: "#F3F4F6", text: "#6B7280" };
    }
  };

  return (
    <div className="page-panel">
      <PageShell title="Policy Inbox" context="Verify and approve generated organizational policies." />
      
      {loading ? (
        <p style={{ marginTop: 20 }}>Loading policy queue…</p>
      ) : (
        <div style={{ marginTop: 24, display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: 20 }}>
            <h3 style={{ marginTop: 0, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
              <Clock size={18} color="var(--primary)" /> Pending Sign-off Queue ({pendingPolicies.length})
            </h3>
            
            {pendingPolicies.length === 0 ? (
              <p style={{ color: "var(--muted)", margin: 0, fontSize: 13 }}>
                No policies currently awaiting review.
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {pendingPolicies.map((policy) => {
                  const style = getStatusStyle(policy.policy_status);
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
                        transition: "all 0.2s",
                        background: "var(--surface)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: 8,
                            backgroundColor: "var(--primary-bg)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "var(--primary)",
                          }}
                        >
                          <FileText size={18} />
                        </div>
                        <div>
                          <strong style={{ display: "block", fontSize: 14 }}>{policy.policy_name}</strong>
                          <span style={{ fontSize: 12, color: "var(--muted)" }}>
                            v{policy.version_number} · Control: {policy.related_control_id || "None"} · Submitted {new Date(policy.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <span
                          className="badge"
                          style={{ backgroundColor: style.bg, color: style.text, fontWeight: 600, fontSize: 11 }}
                        >
                          {policy.policy_status.replace("_", " ").toUpperCase()}
                        </span>
                        <Link
                          to={`/policy/${policy.policy_id}/review`}
                          className="btn btn-secondary btn-sm"
                          style={{ display: "inline-flex", alignItems: "center", gap: 4, textDecoration: "none" }}
                        >
                          <Eye size={12} /> Review Policy <ChevronRight size={12} />
                        </Link>
                      </div>
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
