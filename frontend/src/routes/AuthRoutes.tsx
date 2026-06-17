// Use: Routing configuration for public authentication screens.

import type { RouteObject } from "react-router-dom";
import { AuthLayout } from "../layouts/AuthLayout";
import ForgotPassword from "../pages/auth/ForgotPassword";
import Login from "../pages/auth/Login";
import ResetPassword from "../pages/auth/ResetPassword";

export const authRoutes: RouteObject = {
  element: <AuthLayout />,
  children: [
    { path: "/login", element: <Login /> },
    { path: "/forgot-password", element: <ForgotPassword /> },
    { path: "/reset-password/:token", element: <ResetPassword /> }
  ]
};
