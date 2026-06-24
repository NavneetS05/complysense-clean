// Use: Routing configuration for the Institution Admin portal.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Calendar from "../pages/institution-admin/Calendar";
import Dashboard from "../pages/institution-admin/Dashboard";
import Departments from "../pages/institution-admin/Departments";
import Reports from "../pages/institution-admin/Reports";
import Users from "../pages/institution-admin/Users";

export const adminRoutes: RouteObject = {
  path: "/admin",
  element: (
    <RoleRoute allowedRoles={["Institution Admin"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "departments", element: <Departments /> },
    { path: "users", element: <Users /> },
    { path: "calendar", element: <Calendar /> },
    { path: "reports", element: <Reports /> }
  ]
};
