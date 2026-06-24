// Use: PageShell — page-level header wrapper with title, subtitle, breadcrumbs, and actions slot.

import { ChevronRight } from "lucide-react";

interface Breadcrumb {
  label: string;
  href?: string;
}

interface PageShellProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: Breadcrumb[];
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export function PageShell({
  title,
  subtitle,
  breadcrumbs,
  actions,
  children,
}: PageShellProps) {
  return (
    <div className="page-shell">
      <div className="page-shell-header">
        <div className="page-shell-title-block">
          {breadcrumbs && breadcrumbs.length > 0 && (
            <nav className="breadcrumb" aria-label="Breadcrumb">
              {breadcrumbs.map((crumb, i) => (
                <span key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  {i > 0 && <ChevronRight size={12} className="breadcrumb-sep" />}
                  {crumb.href ? (
                    <a href={crumb.href} style={{ color: "var(--text-secondary)" }}>
                      {crumb.label}
                    </a>
                  ) : (
                    <span>{crumb.label}</span>
                  )}
                </span>
              ))}
            </nav>
          )}
          <h1 className="page-title">{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
        {actions && <div className="page-shell-actions">{actions}</div>}
      </div>
      {children}
    </div>
  );
}
