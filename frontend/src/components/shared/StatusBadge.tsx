// Use: StatusBadge — converts status enum strings to coloured pill badges.

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const label = status
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

  const slug = status.toLowerCase().replace(/\s+/g, "_");

  return (
    <span className={`badge badge-${slug} ${className}`}>
      {label}
    </span>
  );
}
