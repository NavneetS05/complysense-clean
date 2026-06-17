// Use: Routing configuration for the IT Security Officer dashboard.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import Controls from "../pages/security/Controls";
import Dashboard from "../pages/security/Dashboard";
import Evidence from "../pages/security/Evidence";
import IncidentDetail from "../pages/security/IncidentDetail";
import Incidents from "../pages/security/Incidents";
import NewIncident from "../pages/security/NewIncident";

const nav = [
  { to: "/security/dashboard", label: "Dashboard" },
  { to: "/security/incidents", label: "Incidents" },
  { to: "/security/controls", label: "Controls" },
  { to: "/security/evidence", label: "Evidence" }
];

export const securityRoutes: RouteObject = {
  path: "/security",
  element: <DashboardLayout title="IT Security Officer" nav={nav} />,
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "incidents", element: <Incidents /> },
    { path: "incidents/new", element: <NewIncident /> },
    { path: "incidents/:id", element: <IncidentDetail /> },
    { path: "controls", element: <Controls /> },
    { path: "evidence", element: <Evidence /> }
  ]
};
