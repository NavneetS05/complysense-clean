// Use: TypeScript interfaces defining authentication, session, and user context shapes.

import type { RoleName } from "./roles";

export interface AuthUser {
  user_id: string;
  institution_id: string;
  institution_name?: string | null;
  role_id: string;
  role_name: RoleName;
  active_role_id: string;
  active_role_name: RoleName;
  email: string;
  full_name?: string | null;
  phone?: string | null;
  designation?: string | null;
  permissions: string[];
  session_id: string;
}
