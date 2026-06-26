// Use: List of active and historical compliance assessments.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";

type AssessmentItem = {
  assessment_id: string;
  assessment_name: string;
  framework_name: string;
  assessment_status: string;
  started_at?: string;
};

export default function Assessments() {
  const [assessments, setAssessments] = useState<AssessmentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get("/api/v1/assessments");
        setAssessments(Array.isArray(data) ? data : []);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  return (
    <div className="page-panel">
      <h2>Assessments</h2>
      <p>Operational assessment runs and their current status.</p>
      {loading ? <p>Loading assessments…</p> : (
        <div className="card" style={{ padding: 16, marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                <th style={{ padding: "8px 6px" }}>Assessment</th>
                <th style={{ padding: "8px 6px" }}>Framework</th>
                <th style={{ padding: "8px 6px" }}>Status</th>
                <th style={{ padding: "8px 6px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((item) => (
                <tr key={item.assessment_id}>
                  <td style={{ padding: "8px 6px" }}>{item.assessment_name}</td>
                  <td style={{ padding: "8px 6px" }}>{item.framework_name}</td>
                  <td style={{ padding: "8px 6px" }}>{item.assessment_status}</td>
                  <td style={{ padding: "8px 6px" }}><Link to={`/compliance/assessments/${item.assessment_id}`}>Open</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
