// Use: Routing configuration for the Read-Only Assessor workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Dashboard from "../pages/assessor/Dashboard";
import Chat from "../pages/assessor/Chat";
import ReportLibrary from "../pages/assessor/ReportLibrary";

export const assessorRoutes: RouteObject = {
  path: "/assessor",
  element: (
    <RoleRoute allowedRoles={["Read-Only Assessor"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "reports", element: <ReportLibrary /> },
    { path: "chat", element: <Chat /> }
  ]
};
