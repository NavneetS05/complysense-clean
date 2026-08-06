// Use: Routing configuration for the IT Security Officer dashboard.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Controls from "../pages/security/Controls";
import Dashboard from "../pages/security/Dashboard";
import Evidence from "../pages/security/Evidence";
import IncidentDetail from "../pages/security/IncidentDetail";
import Incidents from "../pages/security/Incidents";
import NewIncident from "../pages/security/NewIncident";
import Chat from "../pages/security/Chat";
import Notifications from "../pages/compliance/Notifications";

export const securityRoutes: RouteObject = {
  path: "/security",
  element: (
    <RoleRoute allowedRoles={["IT Security Officer"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "incidents", element: <Incidents /> },
    { path: "incidents/new", element: <NewIncident /> },
    { path: "incidents/:id", element: <IncidentDetail /> },
    { path: "controls", element: <Controls /> },
    { path: "evidence", element: <Evidence /> },
    { path: "chat", element: <Chat /> },
    { path: "notifications", element: <Notifications /> }
  ]
};
