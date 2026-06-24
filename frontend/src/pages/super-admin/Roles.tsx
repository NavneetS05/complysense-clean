// Use: Super Admin — Roles & Permissions. Read-only RBAC matrix showing all 9 roles and their permissions.

import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import { ShieldCheck, Check, Minus } from "lucide-react";

interface RbacMatrix {
  permissions: string[];
  matrix: Record<string, Record<string, boolean>>;
}

const ROLE_NAMES = [
  "Super Admin", "Institution Admin", "Compliance Officer", "IT Security Officer",
  "Auditor", "Department Reviewer", "Vendor Reviewer", "Policy Approver", "Read-Only Assessor"
];

const ROLE_DESCRIPTIONS: Record<string, string> = {
  "Super Admin": "Platform-level administrator with full system access.",
  "Institution Admin": "Manages institution users, departments, and calendar events.",
  "Compliance Officer": "Primary daily operator for controls, gaps, and evidence.",
  "IT Security Officer": "Technical controls, incident management, and CERT-In reporting.",
  "Auditor": "Read-only access to review evidence and add audit observations.",
  "Department Reviewer": "Department-level tasks and evidence submission.",
  "Vendor Reviewer": "Vendor register and risk assessment management.",
  "Policy Approver": "Reviews and approves or rejects drafted policies.",
  "Read-Only Assessor": "Pure observer — view dashboards, controls, and reports only.",
};

const PERMISSION_GROUPS: Record<string, string> = {
  "view_": "👁 View Permissions",
  "manage_": "⚙️ Manage Permissions",
  "upload_": "📤 Upload Permissions",
  "approve_": "✅ Approve Permissions",
  "generate_": "🤖 Generate Permissions",
  "draft_": "✏️ Draft Permissions",
  "add_": "➕ Add Permissions",
  "use_": "🔑 Use Permissions",
};

function getGroupLabel(permKey: string): string {
  for (const [prefix, label] of Object.entries(PERMISSION_GROUPS)) {
    if (permKey.startsWith(prefix)) return label;
  }
  return "Other";
}

function groupPermissions(keys: string[]): Record<string, string[]> {
  const groups: Record<string, string[]> = {};
  for (const key of keys) {
    const group = getGroupLabel(key);
    if (!groups[group]) groups[group] = [];
    groups[group].push(key);
  }
  return groups;
}

function humanize(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function Roles() {
  const [data, setData] = useState<RbacMatrix | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/v1/rbac/matrix")
      .then((r) => setData(r.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ padding: 32 }}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 40, marginBottom: 12, borderRadius: 8 }} />
        ))}
      </div>
    );
  }

  const grouped = data ? groupPermissions(data.permissions) : {};

  const permCountPerRole = (roleName: string) => {
    if (!data) return 0;
    return data.permissions.filter((p) => data.matrix[p]?.[roleName]).length;
  };

  return (
    <PageShell
      title="Roles & Permissions"
      subtitle="Fixed RBAC matrix — contact engineering to modify"
    >
      {/* Role Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16, marginBottom: 32 }}>
        {ROLE_NAMES.map((role) => (
          <div key={role} className="card" style={{ padding: 18 }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
              <div style={{ background: "var(--primary-bg)", borderRadius: 8, padding: 8, flexShrink: 0 }}>
                <ShieldCheck size={18} style={{ color: "var(--primary)" }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14, color: "var(--text-primary)", marginBottom: 4 }}>{role}</div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5, marginBottom: 8 }}>
                  {ROLE_DESCRIPTIONS[role] ?? "Standard role."}
                </div>
                <span className="badge badge-draft">{permCountPerRole(role)} permissions</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Permission Matrix */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Permission Matrix</h2>
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Read-only — scroll horizontally</span>
        </div>
        {!data ? (
          <p style={{ color: "var(--text-muted)", padding: "24px 0", fontSize: 14 }}>Failed to load permissions matrix.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ minWidth: 900, width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "10px 16px", color: "var(--text-muted)", fontWeight: 600, background: "var(--surface-raised)", position: "sticky", left: 0, zIndex: 10, minWidth: 220 }}>Permission</th>
                  {ROLE_NAMES.map((role) => (
                    <th key={role} style={{ padding: "10px 12px", textAlign: "center", color: "var(--text-secondary)", fontWeight: 600, background: "var(--surface-raised)", minWidth: 110, whiteSpace: "nowrap" }}>
                      {role.split(" ").map((w, i, arr) => (
                        <span key={i}>{w}{i < arr.length - 1 ? <br /> : ""}</span>
                      ))}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(grouped).map(([groupLabel, perms]) => (
                  <>
                    <tr key={`group-${groupLabel}`}>
                      <td colSpan={ROLE_NAMES.length + 1} style={{ padding: "10px 16px 6px", fontSize: 11, fontWeight: 700, color: "var(--text-muted)", background: "var(--surface-raised)", letterSpacing: "0.04em" }}>
                        {groupLabel}
                      </td>
                    </tr>
                    {perms.map((perm) => (
                      <tr key={perm} style={{ borderBottom: "1px solid var(--border)" }}>
                        <td style={{ padding: "8px 16px", fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-secondary)", position: "sticky", left: 0, background: "var(--surface)", zIndex: 5 }}>
                          {humanize(perm)}
                        </td>
                        {ROLE_NAMES.map((role) => (
                          <td key={role} style={{ textAlign: "center", padding: "8px 12px" }}>
                            {data.matrix[perm]?.[role] ? (
                              <Check size={15} style={{ color: "var(--success)", margin: "0 auto" }} />
                            ) : (
                              <Minus size={15} style={{ color: "var(--border)", margin: "0 auto" }} />
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </PageShell>
  );
}
