// Use: Routing configuration for the Vendor Reviewer workspace.

import type { RouteObject } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RoleRoute } from "./RoleRoute";
import Dashboard from "../pages/vendor/Dashboard";
import ExpiryTracker from "../pages/vendor/ExpiryTracker";
import NewVendor from "../pages/vendor/NewVendor";
import VendorDetail from "../pages/vendor/VendorDetail";
import Chat from "../pages/vendor/Chat";
import Notifications from "../pages/compliance/Notifications";

export const vendorRoutes: RouteObject = {
  path: "/vendor",
  element: (
    <RoleRoute allowedRoles={["Vendor Reviewer"]}>
      <DashboardLayout />
    </RoleRoute>
  ),
  children: [
    { path: "dashboard", element: <Dashboard /> },
    { path: "vendors/new", element: <NewVendor /> },
    { path: "vendors/:id", element: <VendorDetail /> },
    { path: "expiry", element: <ExpiryTracker /> },
    { path: "chat", element: <Chat /> },
    { path: "notifications", element: <Notifications /> }
  ]
};
