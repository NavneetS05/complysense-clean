// Use: Routing configuration for the Super Admin system console.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import AuditTrail from "../pages/super-admin/AuditTrail";
import Dashboard from "../pages/super-admin/Dashboard";
import Roles from "../pages/super-admin/Roles";
import TenantDetail from "../pages/super-admin/TenantDetail";
import Tenants from "../pages/super-admin/Tenants";
import Notifications from "../pages/compliance/Notifications";

export const superAdminRoutes: RouteObject = {
  path: "/super-admin",
  element: (
    <RoleRoute allowedRoles={["Super Admin"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "tenants",   element: <Tenants /> },
    { path: "tenants/:institution_id", element: <TenantDetail /> },
    { path: "audit-trail", element: <AuditTrail /> },
    { path: "roles",     element: <Roles /> },
    { path: "notifications", element: <Notifications /> },
  ],
};
