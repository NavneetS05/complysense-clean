interface EmptyStateProps {
  title?: string;
  description?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({ title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-title">{title || "No items"}</div>
      {description && <div className="empty-state-description">{description}</div>}
      {onAction && actionLabel && (
        <button className="btn btn-primary" onClick={onAction}>{actionLabel}</button>
      )}
    </div>
  );
}
