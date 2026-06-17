// Use: Custom hook for checking user permissions and roles on the client side.

import { useAuthStore } from "../store/authStore";

export function usePermission(permission: string): boolean {
  return useAuthStore((state) => state.user?.permissions.includes(permission) ?? false);
}
