// Use: Root router — session hydration on mount, dark mode init, full route tree.

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
import { fetchCurrentUser, clearSessionStorage, roleDashboard } from "../lib/auth";

// Root redirect — sends logged-in users straight to their dashboard
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
  // Catch-all
  { path: "*", element: <Navigate to="/login" replace /> },
]);

export function AppRouter() {
  const { setSession, clearSession, setHydrated } = useAuthStore();
  const { dark } = useThemeStore();

  // Apply dark mode class on initial render
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  // Session hydration from localStorage
  useEffect(() => {
    async function hydrate() {
      const storedToken = localStorage.getItem("access_token");
      const storedRefresh = localStorage.getItem("refresh_token");
      const storedUser = localStorage.getItem("auth_user");

      if (storedToken && storedRefresh && storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          // Optimistic restore so the UI renders immediately
          setSession(storedToken, storedRefresh, parsedUser);
          // Validate against /auth/me in the background
          const freshUser = await fetchCurrentUser();
          setSession(storedToken, storedRefresh, freshUser);
        } catch {
          // Token is invalid/expired — clear everything
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
