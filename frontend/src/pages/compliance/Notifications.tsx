// Use: Retrieves and displays user-targeted system notifications.

import { useEffect, useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { useNavigate } from "react-router-dom";
import { Bell, CheckCircle2 } from "lucide-react";
import { api } from "../../lib/api";
import { PageShell } from "../../components/shared/PageShell";
import Loading from "../../components/shared/Loading";
import ErrorState from "../../components/shared/ErrorState";
import EmptyState from "../../components/shared/EmptyState";
import { useAuthStore, useNotificationStore } from "../../store/authStore";
import type { Notification } from "../../store/authStore";

function getNotifBasePath(role: string): string {
  const paths: Record<string, string> = {
    "Super Admin": "/super-admin",
    "Institution Admin": "/admin",
    "Compliance Officer": "/compliance",
    "IT Security Officer": "/security",
    "Auditor": "/auditor",
    "Department Reviewer": "/dept",
    "Vendor Reviewer": "/vendor",
    "Policy Approver": "/policy",
    "Read-Only Assessor": "/assessor",
  };
  return paths[role] ?? "/compliance";
}

function normalizeNotification(raw: Notification & { notification_type?: string }): Notification {
  return {
    ...raw,
    type: raw.type ?? raw.notification_type ?? "notification",
  };
}

function getNotificationPath(notification: Notification, role: string): string | null {
  const base = getNotifBasePath(role);
  const typePaths: Record<string, string> = {
    task_assigned: `${base}/tasks`,
    evidence_approved: `${base}/evidence`,
    evidence_rejected: `${base}/evidence`,
    incident_logged: "/security/incidents",
    policy_pending: "/policy/inbox",
    control_overdue: "/compliance/controls",
    vendor_risk_flagged: "/vendor/dashboard",
  };
  if (notification.related_entity_type && notification.related_entity_id) {
    if (notification.related_entity_type === "task") return `${base}/tasks/${notification.related_entity_id}`;
    if (notification.related_entity_type === "incident") return `/security/incidents/${notification.related_entity_id}`;
    if (notification.related_entity_type === "policy") return `/policy/${notification.related_entity_id}/review`;
    if (notification.related_entity_type === "vendor") return `/vendor/vendors/${notification.related_entity_id}`;
  }
  return typePaths[notification.type] ?? null;
}

export default function Notifications() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { setNotifications, setUnreadCount, markAllRead } = useNotificationStore();
  const [items, setItems] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [marking, setMarking] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get("/api/v1/notifications", { params: { limit: 50, unread: unreadOnly } });
      const next = (data.notifications ?? []).map(normalizeNotification);
      setItems(next);
      setNotifications(next);
      setUnreadCount(data.unread_count ?? 0);
    } catch (err: unknown) {
      setError(err instanceof Error ? err : new Error("Failed to load notifications"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [unreadOnly]);

  const unreadCount = useMemo(() => items.filter((item) => !item.is_read).length, [items]);

  async function handleMarkAllRead() {
    setMarking(true);
    try {
      await api.patch("/api/v1/notifications/read-all");
      markAllRead();
      setItems((current) => current.map((item) => ({ ...item, is_read: true })));
    } finally {
      setMarking(false);
    }
  }

  return (
    <PageShell
      title="Notification Center"
      subtitle="Review system alerts and route follow-up work to the right workspace."
      actions={
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" onClick={() => setUnreadOnly((value) => !value)}>
            {unreadOnly ? "Show all" : "Unread only"}
          </button>
          <button className="btn btn-primary" onClick={handleMarkAllRead} disabled={marking || unreadCount === 0}>
            <CheckCircle2 size={14} /> {marking ? "Marking..." : "Mark all read"}
          </button>
        </div>
      }
    >
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void load()} />
      ) : items.length === 0 ? (
        <EmptyState title="No notifications" description="There are no alerts matching this view." />
      ) : (
        <section className="card" style={{ padding: 0, overflow: "hidden" }}>
          {items.map((item) => {
            const path = getNotificationPath(item, user?.active_role_name ?? "");
            return (
              <button
                key={item.notification_id}
                className="dropdown-item"
                onClick={() => path && navigate(path)}
                style={{
                  width: "100%",
                  padding: "14px 16px",
                  display: "grid",
                  gridTemplateColumns: "24px 1fr auto",
                  gap: 12,
                  alignItems: "start",
                  borderBottom: "1px solid var(--border)",
                  background: item.is_read ? "transparent" : "var(--primary-bg)",
                  textAlign: "left",
                }}
              >
                <Bell size={16} style={{ color: item.is_read ? "var(--text-muted)" : "var(--primary)", marginTop: 2 }} />
                <span>
                  <span style={{ display: "block", fontWeight: 700, color: "var(--text-primary)" }}>{item.title}</span>
                  <span style={{ display: "block", color: "var(--text-secondary)", fontSize: 13, marginTop: 3 }}>
                    {item.message || "No additional details provided."}
                  </span>
                  <span className="badge badge-info" style={{ marginTop: 8 }}>{item.type.replaceAll("_", " ")}</span>
                </span>
                <span style={{ color: "var(--text-muted)", fontSize: 12, whiteSpace: "nowrap" }}>
                  {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </span>
              </button>
            );
          })}
        </section>
      )}
    </PageShell>
  );
}
