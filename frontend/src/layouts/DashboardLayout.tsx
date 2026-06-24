// Use: DashboardLayout — full app shell with sidebar, topbar, role assumption banner, and scrollable content area.

import { Outlet } from "react-router-dom";
import { Sidebar } from "../components/shared/Sidebar";
import { Topbar } from "../components/shared/Topbar";

export function DashboardLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content-wrapper">
        <Topbar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
