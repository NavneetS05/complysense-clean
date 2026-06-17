// Use: Reusable wrapper component providing page headers and margin layouts.

interface PageShellProps {
  title: string;
  context: string;
}

export function PageShell({ title, context }: PageShellProps) {
  return (
    <section className="page-panel">
      <h2>{title}</h2>
      <p>{context}</p>
    </section>
  );
}
