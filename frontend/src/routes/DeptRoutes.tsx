// Use: Routing configuration for the Department Reviewer workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Dashboard from "../pages/dept/Dashboard";
import Tasks from "../pages/dept/Tasks";
import TaskWizard from "../pages/dept/TaskWizard";
import Evidence from "../pages/dept/Evidence";
import SelfAssessment from "../pages/dept/SelfAssessment";
import Chat from "../pages/dept/Chat";
import Notifications from "../pages/compliance/Notifications";

export const deptRoutes: RouteObject = {
  path: "/dept",
  element: (
    <RoleRoute allowedRoles={["Department Reviewer"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "tasks", element: <Tasks /> },
    { path: "tasks/:id", element: <TaskWizard /> },
    { path: "evidence", element: <Evidence /> },
    { path: "self-assessment", element: <SelfAssessment /> },
    { path: "chat", element: <Chat /> },
    { path: "notifications", element: <Notifications /> }
  ]
};
