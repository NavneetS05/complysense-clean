// Use: Root router - session hydration on mount, dark mode init, full route tree.

import { useEffect } from "react";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
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
import { useAuthStore, useThemeStore } from "../store/authStore";
import { clearSessionStorage, refreshSession, roleDashboard } from "../lib/auth";

function RootRedirect() {
  const user = useAuthStore((s) => s.user);
  if (user) {
    return <Navigate to={roleDashboard(user.role_name)} replace />;
  }
  return <Navigate to="/login" replace />;
}

const router = createBrowserRouter([
  authRoutes,
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      { index: true, element: <RootRedirect /> },
      adminRoutes,
      complianceRoutes,
      securityRoutes,
      superAdminRoutes,
      assessorRoutes,
      auditorRoutes,
      deptRoutes,
      vendorRoutes,
      policyRoutes,
    ],
  },
  { path: "*", element: <Navigate to="/login" replace /> },
]);

export function AppRouter() {
  const { setSession, clearSession, setHydrated } = useAuthStore();
  const { dark } = useThemeStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    async function hydrate() {
      const storedUser = localStorage.getItem("auth_user");

      if (storedUser) {
        try {
          const refreshed = await refreshSession();
          setSession(refreshed.access_token, refreshed.user);
        } catch {
          clearSession();
          clearSessionStorage();
        }
      }
      setHydrated();
    }
    hydrate();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return <RouterProvider router={router} />;
}
