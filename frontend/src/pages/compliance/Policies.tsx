// Use: Policy drafting, generation, and approval management list.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

type PolicyItem = {
  policy_id: string;
  policy_name: string;
  version_number: number;
  policy_status: string;
  related_control_id?: string;
  created_at?: string;
  policy_content?: string;
};

export default function Policies() {
  const [policies, setPolicies] = useState<PolicyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [draftName, setDraftName] = useState("");
  const [draftContent, setDraftContent] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/policies");
        setPolicies(Array.isArray(data) ? data : []);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const createPolicy = async () => {
    if (!draftName.trim()) return;
    const { data } = await api.post("/api/v1/policies", { policy_name: draftName.trim(), policy_content: draftContent.trim(), policy_status: "draft" });
    setPolicies((prev) => [
      { ...data, policy_name: data.policy_name, policy_status: data.policy_status },
      ...prev,
    ]);
    setDraftName("");
    setDraftContent("");
  };

  return (
    <div className="page-panel">
      <h2>Policies</h2>
      <p>Institution policies and their workflow status.</p>
      <div className="card" style={{ padding: 16, marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Create draft policy</h3>
        <input value={draftName} onChange={(event) => setDraftName(event.target.value)} placeholder="Policy name" style={{ width: "100%", padding: 8, marginBottom: 8 }} />
        <textarea value={draftContent} onChange={(event) => setDraftContent(event.target.value)} placeholder="Start drafting policy content" rows={4} style={{ width: "100%", padding: 8 }} />
        <button onClick={() => void createPolicy()} style={{ marginTop: 8 }}>Save Draft</button>
      </div>
      {loading ? <p>Loading policies…</p> : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>Policy</th>
                <th style={{ padding: "8px 6px" }}>Version</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Related Control</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((policy) => (
                <tr key={policy.policy_id}>
                  <td style={{ padding: "8px 6px" }}>{policy.policy_name}</td>
                  <td style={{ padding: "8px 6px" }}>v{policy.version_number}</td>
                  <td style={{ padding: "8px 6px" }}>{policy.policy_status}</td>
                  <td style={{ padding: "8px 6px" }}>{policy.related_control_id ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
