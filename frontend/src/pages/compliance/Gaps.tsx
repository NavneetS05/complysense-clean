// Use: Matrix view of identified compliance gaps sorted by framework.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";

type GapRow = {
  gap_id: string;
  control_id?: string;
  framework_name: string;
  severity: string;
  title: string;
  remediation_status: string;
  created_at?: string;
};

export default function Gaps() {
  const [gaps, setGaps] = useState<GapRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/gaps");
        setGaps(Array.isArray(data) ? data : []);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  return (
    <div className="page-panel">
      <h2>Compliance Gaps</h2>
      <p>Open and in-progress remediation items across the institution.</p>
      {loading ? <p>Loading gaps…</p> : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>Severity</th>
                <th style={{ padding: "8px 6px" }}>Framework</th>
                <th style={{ padding: "8px 6px" }}>Control</th>
                <th style={{ padding: "8px 6px" }}>Gap</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {gaps.map((gap) => (
                <tr key={gap.gap_id}>
                  <td style={{ padding: "8px 6px" }}>{gap.severity}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.framework_name}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.control_id ?? "—"}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.title}</td>
                  <td style={{ padding: "8px 6px" }}>{gap.remediation_status}</td>
                  <td style={{ padding: "8px 6px" }}><Link to="/compliance/tasks">Create task</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
