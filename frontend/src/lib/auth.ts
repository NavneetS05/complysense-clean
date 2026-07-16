// Use: Auth helper functions — login, logout, token persistence, password reset flows.

import { api } from "./api";
import type { AuthUser } from "../types/auth";

// ─── Shapes ─────────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface ValidateTokenResponse {
  valid: boolean;
  email: string | null;
}

export interface ExitRoleResponse {
  message: string;
  user: AuthUser;
}

// ─── API calls ──────────────────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<LoginResponse> {
  const res = await api.post<LoginResponse>("/api/v1/auth/login", { email, password });
  return res.data;
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const res = await api.get<AuthUser>("/api/v1/auth/me");
  return res.data;
}

export async function refreshSession(): Promise<LoginResponse> {
  const res = await api.post<LoginResponse>("/api/v1/auth/refresh");
  return res.data;
}

export async function forgotPassword(email: string): Promise<void> {
  await api.post("/api/v1/auth/forgot-password", { email });
}

export async function validateResetToken(token: string): Promise<ValidateTokenResponse> {
  const res = await api.get<ValidateTokenResponse>("/api/v1/auth/validate-reset-token", {
    params: { token },
  });
  return res.data;
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  await api.post("/api/v1/auth/reset-password", {
    token,
    new_password: newPassword,
  });
}

export async function logoutApi(): Promise<void> {
  await api.post("/api/v1/auth/logout");
}

export async function exitRoleAssumption(): Promise<ExitRoleResponse> {
  const res = await api.post<ExitRoleResponse>("/api/v1/auth/exit-role-assumption");
  return res.data;
}

// ─── Storage helpers ─────────────────────────────────────────────────────────

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

// ─── Role → dashboard mapping ────────────────────────────────────────────────

export function roleDashboard(roleName: string): string {
  const map: Record<string, string> = {
    "Super Admin":         "/super-admin/dashboard",
    "Institution Admin":   "/admin/dashboard",
    "Compliance Officer":  "/compliance/dashboard",
    "IT Security Officer": "/security/dashboard",
    "Auditor":             "/auditor/workspace",
    "Department Reviewer": "/dept/dashboard",
    "Vendor Reviewer":     "/vendor/dashboard",
    "Policy Approver":     "/policy/inbox",
    "Read-Only Assessor":  "/assessor/dashboard",
  };
  return map[roleName] ?? "/login";
}
