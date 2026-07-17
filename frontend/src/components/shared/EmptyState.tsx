export default function EmptyState({ title, description, actionLabel, onAction }: { title?: string; description?: string; actionLabel?: string; onAction?: () => void }) {
  return (
    <div style={{ padding: 20, textAlign: "center" }}>
      <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>{title || "No items"}</div>
      {description && <div style={{ color: "var(--text-secondary)", marginBottom: 12 }}>{description}</div>}
      {onAction && actionLabel && (
        <button className="btn btn-primary" onClick={onAction}>{actionLabel}</button>
      )}
    </div>
  );
}
