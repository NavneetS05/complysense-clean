// Use: Topbar — notification bell with popover, dark mode toggle, role assumption banner, avatar menu.

import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bell, Sun, Moon, X,
  CheckSquare, CheckCircle, XCircle, Siren, FileText, Clock, AlertTriangle,
} from "lucide-react";
import { useAuthStore, useNotificationStore, type Notification } from "../../store/authStore";
import { useThemeStore } from "../../store/authStore";
import { api } from "../../lib/api";
import { exitRoleAssumption } from "../../lib/auth";
import { roleDashboard } from "../../lib/auth";
import { formatDistanceToNow } from "date-fns";

// ─── Notification type → icon ─────────────────────────────────────────────────

function NotifIcon({ type }: { type: string }) {
  const map: Record<string, { icon: React.ReactNode; bg: string }> = {
    task_assigned:       { icon: <CheckSquare size={14} />,    bg: "#DBEAFE" },
    evidence_approved:   { icon: <CheckCircle size={14} />,    bg: "#DCFCE7" },
    evidence_rejected:   { icon: <XCircle size={14} />,        bg: "#FEE2E2" },
    incident_logged:     { icon: <Siren size={14} />,          bg: "#FEE2E2" },
    policy_pending:      { icon: <FileText size={14} />,       bg: "#FEF3C7" },
    control_overdue:     { icon: <Clock size={14} />,          bg: "#FEE2E2" },
    vendor_risk_flagged: { icon: <AlertTriangle size={14} />,  bg: "#FFEDD5" },
  };
  const def = map[type] ?? { icon: <Bell size={14} />, bg: "#F1F5F9" };
  return (
    <div
      className="notif-icon"
      style={{ background: def.bg, color: "var(--text-primary)" }}
    >
      {def.icon}
    </div>
  );
}

// ─── Topbar Component ─────────────────────────────────────────────────────────

export function Topbar() {
  const { user, updateUser } = useAuthStore();
  const { dark, toggleDark } = useThemeStore();
  const { notifications, unreadCount, setNotifications, setUnreadCount, markAllRead } =
    useNotificationStore();
  const navigate = useNavigate();
  const [notifOpen, setNotifOpen] = useState(false);
  const [exitingRole, setExitingRole] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);

  // ── Notification polling every 30 s ────────────────────────────────────────
  useEffect(() => {
    async function poll() {
      try {
        const res = await api.get("/api/v1/notifications", {
          params: { limit: 10, unread: true },
        });
        setNotifications((res.data.notifications ?? []).map((n: { notification_type?: string; type?: string }) => ({
          ...n,
          type: n.type ?? n.notification_type ?? "notification",
        })));
        setUnreadCount(res.data.unread_count ?? 0);
      } catch { /* silently ignore — no token yet, etc. */ }
    }
    poll();
    const id = setInterval(poll, 30_000);
    return () => clearInterval(id);
  }, [setNotifications, setUnreadCount]);

  // ── Close popover on outside click ─────────────────────────────────────────
  useEffect(() => {
    function onOutside(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    }
    if (notifOpen) document.addEventListener("mousedown", onOutside);
    return () => document.removeEventListener("mousedown", onOutside);
  }, [notifOpen]);

  // ── Mark all read ────────────────────────────────────────────────────────────
  async function handleMarkAllRead() {
    try {
      await api.patch("/api/v1/notifications/read-all");
      markAllRead();
    } catch { /* ignore */ }
  }

  // ── Exit role assumption ─────────────────────────────────────────────────────
  async function handleExitRole() {
    setExitingRole(true);
    try {
      const res = await exitRoleAssumption();
      updateUser(res.user);
      navigate(roleDashboard(res.user.role_name), { replace: true });
    } catch { /* ignore */ } finally {
      setExitingRole(false);
    }
  }

  const isAssuming = user?.role_id !== user?.active_role_id;

  return (
    <>
      <header className="topbar">
        <div className="topbar-left" />

        <div className="topbar-right">
          {/* Dark mode toggle */}
          <button
            className="topbar-icon-btn"
            onClick={toggleDark}
            aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
            title={dark ? "Light mode" : "Dark mode"}
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Notification bell */}
          <div style={{ position: "relative" }} ref={popoverRef}>
            <button
              className="topbar-icon-btn"
              onClick={() => setNotifOpen((v) => !v)}
              aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ""}`}
              id="notif-bell-btn"
              aria-haspopup="true"
              aria-expanded={notifOpen}
            >
              <Bell size={20} />
              {unreadCount > 0 && (
                <span className="notif-badge">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </button>

            {/* Notification popover */}
            {notifOpen && (
              <div
                className="notif-popover"
                style={{
                  position: "absolute",
                  right: 0,
                  top: "calc(100% + 8px)",
                  zIndex: 60,
                }}
              >
                <div className="notif-popover-header">
                  <span className="notif-popover-title">Notifications</span>
                  {unreadCount > 0 && (
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={handleMarkAllRead}
                      style={{ padding: "2px 8px" }}
                    >
                      Mark all read
                    </button>
                  )}
                </div>

                {notifications.length === 0 ? (
                  <div
                    style={{
                      padding: "32px 16px",
                      textAlign: "center",
                      color: "var(--text-secondary)",
                      fontSize: 13,
                    }}
                  >
                    <Bell size={32} style={{ margin: "0 auto 8px", opacity: 0.3 }} />
                    You're all caught up
                  </div>
                ) : (
                  <div>
                    {notifications.map((n) => (
                      <NotifItem
                        key={n.notification_id}
                        notification={n}
                        onClose={() => setNotifOpen(false)}
                      />
                    ))}
                  </div>
                )}

                <div className="notif-popover-footer">
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => {
                      setNotifOpen(false);
                      navigate(`${getNotifBasePath(user?.active_role_name ?? "")}/notifications`);
                    }}
                    style={{ width: "100%", justifyContent: "center" }}
                  >
                    View all notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Close popover X (mobile) */}
          {notifOpen && (
            <button
              className="topbar-icon-btn"
              onClick={() => setNotifOpen(false)}
              style={{ display: "none" }}
              aria-label="Close notifications"
            >
              <X size={18} />
            </button>
          )}
        </div>
      </header>

      {/* Role assumption banner */}
      {isAssuming && (
        <div className="role-assumption-bar" role="alert" aria-live="polite">
          <span className="role-assumption-text">
            ⚠ Operating as: <strong>{user?.active_role_name}</strong>
          </span>
          <span style={{ color: "#D97706" }}>|</span>
          <button
            className="role-assumption-exit-btn"
            onClick={handleExitRole}
            disabled={exitingRole}
            id="exit-role-assumption-btn"
          >
            {exitingRole ? "Exiting…" : "Exit Assumed Role"}
          </button>
        </div>
      )}
    </>
  );
}

// ─── Notification Item ────────────────────────────────────────────────────────

function NotifItem({
  notification,
  onClose,
}: {
  notification: Notification;
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  function handleClick() {
    onClose();
    const base = getNotifBasePath(user?.active_role_name ?? "");
    const paths: Record<string, string> = {
      task_assigned:       `${base}/tasks`,
      evidence_approved:   `${base}/evidence`,
      evidence_rejected:   `${base}/evidence`,
      incident_logged:     "/security/incidents",
      policy_pending:      "/policy/inbox",
      control_overdue:     "/compliance/controls",
      vendor_risk_flagged: "/vendor/dashboard",
    };
    const path = paths[notification.type];
    if (path) navigate(path);
  }

  return (
    <div
      className={`notif-item ${!notification.is_read ? "unread" : ""}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && handleClick()}
    >
      <NotifIcon type={notification.type} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="notif-title">{notification.title}</div>
        <div className="notif-time">
          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
        </div>
      </div>
      {!notification.is_read && <div className="notif-unread-dot" />}
    </div>
  );
}

function getNotifBasePath(role: string): string {
  const m: Record<string, string> = {
    "Super Admin":         "/super-admin",
    "Institution Admin":   "/admin",
    "Compliance Officer":  "/compliance",
    "IT Security Officer": "/security",
    "Auditor":             "/auditor",
    "Department Reviewer": "/dept",
    "Vendor Reviewer":     "/vendor",
    "Policy Approver":     "/policy",
    "Read-Only Assessor":  "/assessor",
  };
  return m[role] ?? "/compliance";
}
