// Use: TypeScript interfaces defining authentication, session, and user context shapes.

import type { RoleName } from "./roles";

export interface AuthUser {
  user_id: string;
  institution_id: string;
  role_name: RoleName;
  active_role_name: RoleName;
  email: string;
  permissions: string[];
}
