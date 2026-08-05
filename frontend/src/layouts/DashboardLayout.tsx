// Use: DashboardLayout — full app shell with responsive sidebar drawer, topbar, mobile header, and content area.

import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Menu, Shield } from "lucide-react";
import { Sidebar } from "../components/shared/Sidebar";
import { Topbar } from "../components/shared/Topbar";

export function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-shell">
      {/* Mobile Top Header */}
      <header className="mobile-header">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div className="sidebar-brand-logo" style={{ width: 28, height: 28 }}>
            <Shield size={16} />
          </div>
          <span style={{ fontWeight: 700, fontSize: 15 }}>ComplySense</span>
        </div>
        <button
          className="mobile-nav-toggle"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-label="Toggle navigation menu"
        >
          <Menu size={20} />
        </button>
      </header>

      {/* Backdrop for mobile drawer */}
      <div
        className={`sidebar-backdrop ${mobileOpen ? "show" : ""}`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Responsive Sidebar */}
      <Sidebar mobileOpen={mobileOpen} onCloseMobile={() => setMobileOpen(false)} />

      <div className="main-content-wrapper">
        <Topbar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
