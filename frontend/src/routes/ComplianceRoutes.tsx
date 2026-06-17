// Use: Routing configuration for the Compliance Officer workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
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

const nav = [
  { to: "/compliance/dashboard", label: "Dashboard" },
  { to: "/compliance/controls", label: "Controls" },
  { to: "/compliance/gaps", label: "Gaps" },
  { to: "/compliance/evidence-queue", label: "Evidence Queue" },
  { to: "/compliance/assessments", label: "Assessments" },
  { to: "/compliance/policies", label: "Policies" },
  { to: "/compliance/tasks", label: "Tasks" },
  { to: "/compliance/notifications", label: "Notifications" }
];

export const complianceRoutes: RouteObject = {
  path: "/compliance",
  element: <DashboardLayout title="Compliance Officer" nav={nav} />,
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
