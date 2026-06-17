// Use: Routing configuration for the Institution Admin portal.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import Calendar from "../pages/institution-admin/Calendar";
import Dashboard from "../pages/institution-admin/Dashboard";
import Departments from "../pages/institution-admin/Departments";
import Reports from "../pages/institution-admin/Reports";
import Users from "../pages/institution-admin/Users";

const nav = [
  { to: "/admin/dashboard", label: "Dashboard" },
  { to: "/admin/departments", label: "Departments" },
  { to: "/admin/users", label: "Users" },
  { to: "/admin/calendar", label: "Calendar" },
  { to: "/admin/reports", label: "Reports" }
];

export const adminRoutes: RouteObject = {
  path: "/admin",
  element: <DashboardLayout title="Institution Admin" nav={nav} />,
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "departments", element: <Departments /> },
    { path: "users", element: <Users /> },
    { path: "calendar", element: <Calendar /> },
    { path: "reports", element: <Reports /> }
  ]
};
