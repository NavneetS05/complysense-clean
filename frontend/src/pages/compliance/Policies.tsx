// Use: Policy drafting, generation, and approval management list.

import { useEffect, useState, useMemo } from "react";
import { api } from "../../lib/api";
import { DataTable, Column } from "../../components/shared/DataTable";
import { PageShell } from "../../components/shared/PageShell";
import { useToast } from "../../components/shared/ToastContext";
import { getApiErrorMessage } from "../../lib/errors";

type PolicyItem = {
  policy_id: string;
  policy_name: string;
  version_number: number;
  policy_status: string;
  related_control_id?: string;
  created_at?: string;
  policy_content?: string;
  [key: string]: unknown;
};

export default function Policies() {
  const [policies, setPolicies] = useState<PolicyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [draftName, setDraftName] = useState("");
  const [draftContent, setDraftContent] = useState("");
  const [creating, setCreating] = useState(false);

  // Filter states
  const [filters, setFilters] = useState({ search: "", status: "" });

  const toast = useToast();

  async function load() {
    try {
      const { data } = await api.get("/api/v1/policies");
      setPolicies(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const createPolicy = async () => {
    if (!draftName.trim()) {
      toast.error("Please enter a policy name.");
      return;
    }
    setCreating(true);
    try {
      const { data } = await api.post("/api/v1/policies", {
        policy_name: draftName.trim(),
        policy_content: draftContent.trim(),
        policy_status: "draft"
      });
      setPolicies((prev) => [
        { ...data, policy_name: data.policy_name, policy_status: data.policy_status },
        ...prev,
      ]);
      setDraftName("");
      setDraftContent("");
      toast.success("Policy draft saved successfully.");
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Failed to create policy draft."));
    } finally {
      setCreating(false);
    }
  };

  // Unique statuses for filter
  const statuses = useMemo(() => {
    return Array.from(new Set(policies.map((p) => p.policy_status).filter(Boolean)));
  }, [policies]);

  // Client-side filtering
  const filteredPolicies = useMemo(() => {
    return policies.filter((p) => {
      const name = (p.policy_name || "").toLowerCase();
      const matchesSearch = !filters.search || name.includes(filters.search.toLowerCase());
      const matchesStatus = !filters.status || p.policy_status === filters.status;
      return matchesSearch && matchesStatus;
    });
  }, [policies, filters]);

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
      case "active":
        return "badge-approved";
      case "draft":
        return "badge-draft";
      case "pending_approval":
      case "pending":
        return "badge-pending";
      case "rejected":
        return "badge-rejected";
      default:
        return "badge-info";
    }
  };

  const columns: Column<PolicyItem>[] = [
    {
      key: "policy_name",
      label: "Policy",
      sortable: true,
      render: (val) => <span style={{ fontWeight: 600 }}>{String(val || "Unnamed Policy")}</span>
    },
    {
      key: "version_number",
      label: "Version",
      sortable: true,
      render: (val) => `v${val || 1}`
    },
    {
      key: "policy_status",
      label: "Status",
      sortable: true,
      render: (val) => {
        const status = String(val || "draft");
        return (
          <span className={`badge ${getStatusBadgeClass(status)}`}>
            {status.replace("_", " ")}
          </span>
        );
      }
    },
    {
      key: "related_control_id",
      label: "Related Control",
      sortable: true,
      render: (val) => <span className="font-mono">{String(val || "—")}</span>
    }
  ];

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell 
        title="Policies" 
        subtitle="Institution policies and their workflow status." 
      />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16, alignItems: "start" }}>
        <div className="card" style={{ display: "grid", gap: 12 }}>
          <h3 style={{ margin: 0, marginBottom: 4 }}>Create Draft Policy</h3>
          
          <div className="form-group">
            <label className="form-label">Policy Name</label>
            <input 
              value={draftName} 
              onChange={(event) => setDraftName(event.target.value)} 
              placeholder="e.g. Information Security Policy" 
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Content</label>
            <textarea 
              value={draftContent} 
              onChange={(event) => setDraftContent(event.target.value)} 
              placeholder="Start drafting policy content..." 
              rows={5} 
              className="form-textarea"
            />
          </div>

          <button 
            onClick={() => void createPolicy()} 
            disabled={creating || !draftName}
            className="btn btn-primary"
            style={{ width: 140, marginTop: 8 }}
          >
            {creating ? "Saving..." : "Save Draft"}
          </button>
        </div>

        <div style={{ display: "grid", gap: 12 }}>
          <section className="card" style={{ display: "flex", gap: 12, padding: 12 }}>
            <input 
              className="form-input" 
              placeholder="Search by policy name..." 
              value={filters.search} 
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} 
            />
            <select 
              className="form-input" 
              value={filters.status} 
              onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
              style={{ minWidth: 140 }}
            >
              <option value="">All Statuses</option>
              {statuses.map((status) => (
                <option key={status} value={status}>{status.replace("_", " ")}</option>
              ))}
            </select>
          </section>

          <DataTable 
            columns={columns} 
            data={filteredPolicies} 
            loading={loading}
            emptyTitle="No policies found"
            emptyDesc="No policies match the active filter criteria."
            keyField="policy_id"
            pageSize={10}
          />
        </div>
      </div>
    </div>
  );
}
