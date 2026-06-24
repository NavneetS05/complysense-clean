// Use: Sidebar — role-aware navigation with count badges and user menu.

import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Building2, ScrollText, ShieldCheck,
  FolderTree, Users, CalendarDays, FileBarChart,
  Kanban, AlertTriangle, Inbox, ClipboardList, FileText,
  CheckSquare, Bell, ShieldAlert, Siren, Settings2, Upload,
  Microscope, MessageSquare, Archive, ClipboardCheck,
  Store, CalendarX, History, BarChart3, Library, Bot,
  LogOut, User, ChevronDown, Shield,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useAuthStore, useNotificationStore } from "../../store/authStore";
import { logoutApi, clearSessionStorage, roleDashboard } from "../../lib/auth";
import { useState } from "react";
import type { RoleName } from "../../types/roles";

// ─── Nav Item Definition ──────────────────────────────────────────────────────

interface NavItemDef {
  to: string;
  label: string;
  icon: LucideIcon;
  badge?: "unread" | "pending";
}

// ─── Role nav maps ────────────────────────────────────────────────────────────

const NAV_MAP: Record<RoleName, NavItemDef[]> = {
  "Super Admin": [
    { to: "/super-admin/dashboard",  label: "Dashboard",          icon: LayoutDashboard },
    { to: "/super-admin/tenants",    label: "Tenants",             icon: Building2 },
    { to: "/super-admin/audit-trail",label: "Audit Trail",         icon: ScrollText },
    { to: "/super-admin/roles",      label: "Roles & Permissions", icon: ShieldCheck },
  ],
  "Institution Admin": [
    { to: "/admin/dashboard",    label: "Dashboard",   icon: LayoutDashboard },
    { to: "/admin/departments",  label: "Departments", icon: FolderTree },
    { to: "/admin/users",        label: "Users",       icon: Users },
    { to: "/admin/calendar",     label: "Calendar",    icon: CalendarDays },
    { to: "/admin/reports",      label: "Reports",     icon: FileBarChart },
  ],
  "Compliance Officer": [
    { to: "/compliance/dashboard",      label: "Dashboard",     icon: LayoutDashboard },
    { to: "/compliance/controls",       label: "Controls",      icon: Kanban },
    { to: "/compliance/gaps",           label: "Gaps",          icon: AlertTriangle },
    { to: "/compliance/evidence-queue", label: "Evidence Queue",icon: Inbox,         badge: "pending" },
    { to: "/compliance/assessments",    label: "Assessments",   icon: ClipboardList },
    { to: "/compliance/policies",       label: "Policies",      icon: FileText },
    { to: "/compliance/tasks",          label: "Tasks",         icon: CheckSquare },
    { to: "/compliance/notifications",  label: "Notifications", icon: Bell,          badge: "unread" },
  ],
  "IT Security Officer": [
    { to: "/security/dashboard",  label: "Dashboard", icon: ShieldAlert },
    { to: "/security/incidents",  label: "Incidents", icon: Siren,   badge: "pending" },
    { to: "/security/controls",   label: "Controls",  icon: Settings2 },
    { to: "/security/evidence",   label: "Evidence",  icon: Upload },
  ],
  "Auditor": [
    { to: "/auditor/workspace",    label: "Workspace",    icon: Microscope },
    { to: "/auditor/observations", label: "Observations", icon: MessageSquare },
    { to: "/auditor/reports",      label: "Reports",      icon: FileText },
  ],
  "Department Reviewer": [
    { to: "/dept/dashboard",       label: "Dashboard",      icon: LayoutDashboard },
    { to: "/dept/tasks",           label: "My Tasks",       icon: CheckSquare, badge: "pending" },
    { to: "/dept/evidence",        label: "Evidence Vault", icon: Archive },
    { to: "/dept/self-assessment", label: "Self Assessment",icon: ClipboardCheck },
  ],
  "Vendor Reviewer": [
    { to: "/vendor/dashboard", label: "Vendor Register", icon: Store },
    { to: "/vendor/expiry",    label: "Expiry Tracker",  icon: CalendarX },
  ],
  "Policy Approver": [
    { to: "/policy/inbox",   label: "Inbox",          icon: Inbox, badge: "pending" },
    { to: "/policy/history", label: "Policy History", icon: History },
  ],
  "Read-Only Assessor": [
    { to: "/assessor/dashboard", label: "Dashboard", icon: BarChart3 },
    { to: "/assessor/reports",   label: "Reports",   icon: Library },
    { to: "/assessor/chat",      label: "Ask AI",    icon: Bot },
  ],
};

// ─── Sidebar Component ────────────────────────────────────────────────────────

export function Sidebar() {
  const { user, clearSession } = useAuthStore();
  const { unreadCount } = useNotificationStore();
  const navigate = useNavigate();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  if (!user) return null;

  // Use active role for nav (assumed role shows that role's nav)
  const activeRole = user.active_role_name as RoleName;
  const navItems = NAV_MAP[activeRole] ?? NAV_MAP[user.role_name as RoleName] ?? [];

  const initials = user.email
    .split("@")[0]
    .slice(0, 2)
    .toUpperCase();

  async function handleLogout() {
    try { await logoutApi(); } catch { /* ignore */ }
    clearSession();
    clearSessionStorage();
    navigate("/login", { replace: true });
  }

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-row">
          <div className="sidebar-brand-logo">
            <Shield size={18} />
          </div>
          <span className="sidebar-brand-name">ComplySense</span>
        </div>
        {user.role_name !== "Super Admin" && (
          <div className="sidebar-institution-name">
            {user.institution_id}
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="sidebar-nav" aria-label="Main navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const badgeCount =
            item.badge === "unread" ? unreadCount : 0; // "pending" counts TBD via API

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
              end={item.to.endsWith("dashboard")}
            >
              <Icon size={18} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
              {badgeCount > 0 && (
                <span className="nav-badge">{badgeCount > 99 ? "99+" : badgeCount}</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User footer */}
      <div className="sidebar-footer" style={{ position: "relative" }}>
        <button
          className="sidebar-user-btn"
          onClick={() => setUserMenuOpen((v) => !v)}
          aria-expanded={userMenuOpen}
          aria-haspopup="menu"
          id="sidebar-user-btn"
        >
          <div className="user-avatar-circle">{initials}</div>
          <div className="user-info">
            <div className="user-info-name">{user.email.split("@")[0]}</div>
            <div className="user-info-role">{activeRole}</div>
          </div>
          <ChevronDown
            size={14}
            style={{
              color: "var(--text-secondary)",
              transform: userMenuOpen ? "rotate(180deg)" : "none",
              transition: "transform 200ms",
            }}
          />
        </button>

        {userMenuOpen && (
          <>
            <div
              style={{ position: "fixed", inset: 0, zIndex: 39 }}
              onClick={() => setUserMenuOpen(false)}
            />
            <div
              className="dropdown-menu"
              style={{
                position: "absolute",
                bottom: "calc(100% + 4px)",
                left: 8,
                right: 8,
                zIndex: 50,
              }}
              role="menu"
            >
              <div
                style={{ padding: "8px 10px 6px", borderBottom: "1px solid var(--border)", marginBottom: 4 }}
              >
                <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                  {user.email.split("@")[0]}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>{user.email}</div>
                <div
                  className="badge badge-in_progress"
                  style={{ marginTop: 4, display: "inline-flex" }}
                >
                  {activeRole}
                </div>
              </div>
              <button
                className="dropdown-item"
                onClick={() => { navigate("/profile"); setUserMenuOpen(false); }}
                role="menuitem"
              >
                <User size={14} /> Profile Settings
              </button>
              <div className="dropdown-separator" />
              <button
                className="dropdown-item danger"
                onClick={handleLogout}
                role="menuitem"
              >
                <LogOut size={14} /> Logout
              </button>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
