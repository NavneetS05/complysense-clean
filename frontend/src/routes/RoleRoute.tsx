// Use: Role-based access control route wrapper — checks primary or assumed role.

import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { roleDashboard } from "../lib/auth";

interface RoleRouteProps {
  allowedRoles: string[];
  children: React.ReactElement;
}

export function RoleRoute({ allowedRoles, children }: RoleRouteProps) {
  const user = useAuthStore((s) => s.user);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check the active role (may be an assumed role) against the allowed list
  const effectiveRole = user.active_role_name ?? user.role_name;

  if (!allowedRoles.includes(effectiveRole)) {
    // Redirect to the user's correct dashboard silently — never 403
    return <Navigate to={roleDashboard(user.role_name)} replace />;
  }

  return children;
}
