import { createBrowserRouter, Navigate } from "react-router-dom";
import { authRoutes } from "./AuthRoutes";
import { adminRoutes } from "./AdminRoutes";
import { complianceRoutes } from "./ComplianceRoutes";
import { securityRoutes } from "./SecurityRoutes";
import { superAdminRoutes } from "./SuperAdminRoutes";
import { assessorRoutes } from "./AssessorRoutes";
import { auditorRoutes } from "./AuditorRoutes";
import { deptRoutes } from "./DeptRoutes";
import { vendorRoutes } from "./VendorRoutes";
import { policyRoutes } from "./PolicyRoutes";
import { ProtectedRoute } from "./ProtectedRoute";

export const router = createBrowserRouter([
  authRoutes,
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      adminRoutes,
      complianceRoutes,
      securityRoutes,
      superAdminRoutes,
      assessorRoutes,
      auditorRoutes,
      deptRoutes,
      vendorRoutes,
      policyRoutes,
      { path: "/", element: <Navigate to="/login" replace /> }
    ]
  }
]);
