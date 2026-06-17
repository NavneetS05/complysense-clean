// Use: Main system dashboard shell containing topbar, sidebar, and notification indicators.

import { NavLink, Outlet } from "react-router-dom";

interface DashboardLayoutProps {
  title: string;
  nav: Array<{ to: string; label: string }>;
}

export function DashboardLayout({ title, nav }: DashboardLayoutProps) {
  return (
    <div className="dashboard-shell">
      <aside className="sidebar">
        <div className="brand">ComplySense</div>
        <nav>
          {nav.map((item) => (
            <NavLink key={item.to} to={item.to}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <section className="workspace">
        <header className="topbar">
          <h1>{title}</h1>
        </header>
        <Outlet />
      </section>
    </div>
  );
}
