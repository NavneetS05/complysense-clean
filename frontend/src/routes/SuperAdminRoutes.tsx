// Use: Routing configuration for the Super Admin system console.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import AuditTrail from "../pages/super-admin/AuditTrail";
import Dashboard from "../pages/super-admin/Dashboard";
import Roles from "../pages/super-admin/Roles";
import TenantDetail from "../pages/super-admin/TenantDetail";
import Tenants from "../pages/super-admin/Tenants";

const nav = [
  { to: "/super-admin/dashboard", label: "Dashboard" },
  { to: "/super-admin/tenants", label: "Tenants" },
  { to: "/super-admin/audit-trail", label: "Audit Trail" },
  { to: "/super-admin/roles", label: "Roles" }
];

export const superAdminRoutes: RouteObject = {
  path: "/super-admin",
  element: <DashboardLayout title="Super Admin" nav={nav} />,
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "tenants", element: <Tenants /> },
    { path: "tenants/:id", element: <TenantDetail /> },
    { path: "audit-trail", element: <AuditTrail /> },
    { path: "roles", element: <Roles /> }
  ]
};
