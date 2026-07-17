// Use: Routing configuration for the Auditor workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Workspace from "../pages/auditor/Workspace";
import Observations from "../pages/auditor/Observations";
import ReportBuilder from "../pages/auditor/ReportBuilder";
import ReportView from "../pages/auditor/ReportView";
import Chat from "../pages/auditor/Chat";

export const auditorRoutes: RouteObject = {
  path: "/auditor",
  element: (
    <RoleRoute allowedRoles={["Auditor"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "workspace", element: <Workspace /> },
    { path: "observations", element: <Observations /> },
    { path: "reports", element: <ReportBuilder /> },
    { path: "reports/:id", element: <ReportView /> },
    { path: "chat", element: <Chat /> }
  ]
};
