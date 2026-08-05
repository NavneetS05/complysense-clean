export default function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <div className="error-state">
      <div className="error-state-title">Error</div>
      <div className="error-state-message">{message || "An error occurred while fetching data."}</div>
      {onRetry && (
        <div className="error-state-actions">
          <button className="btn btn-secondary" onClick={onRetry}>Retry</button>
        </div>
      )}
    </div>
  );
}
