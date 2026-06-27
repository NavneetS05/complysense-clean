// Use: Lists technical security controls assigned to the IT security officer.

import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../PageShell";

interface ControlItem {
  assignment_id: string;
  control_id: string;
  framework_name: string;
  status: string;
  due_date?: string | null;
  assigned_name?: string | null;
}

export default function Controls() {
  const [controls, setControls] = useState<ControlItem[]>([]);
  useEffect(() => {
    void api.get<ControlItem[]>("/api/v1/controls").then(({ data }) => setControls(data));
  }, []);

  return (
    <div className="page-panel">
      <PageShell title="IT Control Assignments" context="Technical control assignments and due dates." />
      <div style={{ overflowX: "auto", marginTop: 16 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb" }}>
              <th style={{ padding: 10 }}>Control</th>
              <th style={{ padding: 10 }}>Framework</th>
              <th style={{ padding: 10 }}>Status</th>
              <th style={{ padding: 10 }}>Due</th>
              <th style={{ padding: 10 }}>Owner</th>
            </tr>
          </thead>
          <tbody>
            {controls.map((item) => (
              <tr key={item.assignment_id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                <td style={{ padding: 10 }}>{item.control_id}</td>
                <td style={{ padding: 10 }}>{item.framework_name}</td>
                <td style={{ padding: 10 }}>{item.status}</td>
                <td style={{ padding: 10 }}>{item.due_date ? new Date(item.due_date).toLocaleDateString() : "—"}</td>
                <td style={{ padding: 10 }}>{item.assigned_name ?? "Unassigned"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
