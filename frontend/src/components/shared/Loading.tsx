export default function Loading({ size = 32 }: { size?: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 12 }}>
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="var(--muted)" strokeWidth="3" opacity="0.2" />
        <path d="M22 12a10 10 0 00-10-10" stroke="var(--primary)" strokeWidth="3" strokeLinecap="round" />
      </svg>
    </div>
  );
}
