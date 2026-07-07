// Use: CitationChip — non-interactive badge displaying regulatory framework references in AI responses.

import { BookOpen } from "lucide-react";

interface CitationChipProps {
  framework: string;
  section?: string;
}

export function CitationChip({ framework, section }: CitationChipProps) {
  if (!framework) return null;

  return (
    <span
      className="badge badge-draft"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        margin: "2px 4px",
        padding: "4px 8px",
        fontSize: "11px",
        fontWeight: 500,
        backgroundColor: "var(--surface-raised)",
        border: "1px solid var(--border)",
        color: "var(--text-secondary)",
        borderRadius: "var(--radius-sm)",
        fontFamily: "var(--font-mono)",
      }}
    >
      <BookOpen size={10} color="var(--primary)" />
      <span>
        {framework}
        {section ? ` — ${section}` : ""}
      </span>
    </span>
  );
}
