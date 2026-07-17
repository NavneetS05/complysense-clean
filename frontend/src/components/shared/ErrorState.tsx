export default function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <div style={{ padding: 16, textAlign: "center" }}>
      <div style={{ color: "var(--danger)", fontWeight: 600, marginBottom: 8 }}>Error</div>
      <div style={{ color: "var(--text-secondary)", marginBottom: 12 }}>{message || "An error occurred while fetching data."}</div>
      {onRetry && (
        <button className="btn" onClick={onRetry}>Retry</button>
      )}
    </div>
  );
}
