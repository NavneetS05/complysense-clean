// Use: Routing configuration for the Compliance Officer workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import AssessmentRunner from "../pages/compliance/AssessmentRunner";
import Assessments from "../pages/compliance/Assessments";
import ControlDetail from "../pages/compliance/ControlDetail";
import Controls from "../pages/compliance/Controls";
import Dashboard from "../pages/compliance/Dashboard";
import EvidenceQueue from "../pages/compliance/EvidenceQueue";
import Gaps from "../pages/compliance/Gaps";
import Notifications from "../pages/compliance/Notifications";
import Policies from "../pages/compliance/Policies";
import Tasks from "../pages/compliance/Tasks";

export const complianceRoutes: RouteObject = {
  path: "/compliance",
  element: (
    <RoleRoute allowedRoles={["Compliance Officer"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "controls", element: <Controls /> },
    { path: "controls/:id", element: <ControlDetail /> },
    { path: "gaps", element: <Gaps /> },
    { path: "evidence-queue", element: <EvidenceQueue /> },
    { path: "assessments", element: <Assessments /> },
    { path: "assessments/:id", element: <AssessmentRunner /> },
    { path: "policies", element: <Policies /> },
    { path: "tasks", element: <Tasks /> },
    { path: "notifications", element: <Notifications /> }
  ]
};
