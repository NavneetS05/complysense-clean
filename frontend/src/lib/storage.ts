// Use: Session storage helpers — extracted to avoid circular dependency between api.ts and auth.ts.

import type { AuthUser } from "../types/auth";

export function persistSession(user: AuthUser) {
  try {
    localStorage.setItem("auth_user", JSON.stringify(user));
  } catch { /* quota errors */ }
}

export function clearSessionStorage() {
  try {
    localStorage.removeItem("auth_user");
  } catch { /* */ }
}
