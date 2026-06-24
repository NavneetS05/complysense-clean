// Use: AuthLayout — split-screen layout for Login, Forgot Password, and Reset Password pages.

import { Outlet } from "react-router-dom";
import { Shield, Check } from "lucide-react";

export function AuthLayout() {
  return (
    <main className="auth-shell">
      {/* ── Left brand panel ── */}
      <div className="auth-brand-panel">
        <div className="auth-brand-top">
          <div className="auth-brand-shield">
            <Shield size={24} />
          </div>
          <span className="auth-brand-text">ComplySense</span>
        </div>

        <div className="auth-brand-center">
          <h2 className="auth-tagline">
            Intelligent GRC for<br />
            <span>Indian Universities</span>
          </h2>

          <div className="auth-features">
            {[
              "DPDP Act 2023 Ready",
              "CERT-In Incident Management",
              "AI-Powered Compliance",
            ].map((f) => (
              <div key={f} className="auth-feature-item">
                <div className="auth-feature-check">
                  <Check size={12} strokeWidth={3} />
                </div>
                {f}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="auth-form-panel">
        <Outlet />
      </div>
    </main>
  );
}
