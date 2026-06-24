// Use: Routing configuration for the Policy Approver workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Inbox from "../pages/policy/Inbox";
import PolicyReview from "../pages/policy/PolicyReview";
import History from "../pages/policy/History";

export const policyRoutes: RouteObject = {
  path: "/policy",
  element: (
    <RoleRoute allowedRoles={["Policy Approver"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "inbox", element: <Inbox /> },
    { path: ":id/review", element: <PolicyReview /> },
    { path: "history", element: <History /> }
  ]
};
