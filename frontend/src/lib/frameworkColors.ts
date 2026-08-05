// Use: Consistent accent colors for regulatory framework categorization.
// These are intentionally distinct from severity colors (red/amber/green)
// so that "this is ISO 27001" is never confused with "this is dangerous."
// Apply everywhere framework_name appears: badges, chart legends, table cells.

export interface FrameworkColor {
  bg: string;
  text: string;
  border: string;
}

export const FRAMEWORK_COLORS: Record<string, FrameworkColor> = {
  "ISO 27001:2022":    { bg: "#E0E7FF", text: "#3730A3", border: "#C7D2FE" }, // indigo
  "ISO 27001":         { bg: "#E0E7FF", text: "#3730A3", border: "#C7D2FE" }, // indigo (alias)
  "NIST CSF 2.0":      { bg: "#CCFBF1", text: "#0F766E", border: "#99F6E4" }, // teal
  "NIST CSF":          { bg: "#CCFBF1", text: "#0F766E", border: "#99F6E4" }, // teal (alias)
  "NIST SP 800-53":    { bg: "#D1FAE5", text: "#065F46", border: "#A7F3D0" }, // emerald
  "DPDP Act 2023":     { bg: "#F3E8FF", text: "#7E22CE", border: "#E9D5FF" }, // violet
  "DPDP Act":          { bg: "#F3E8FF", text: "#7E22CE", border: "#E9D5FF" }, // violet (alias)
  "IT Act / CERT-In":  { bg: "#FFEDD5", text: "#9A3412", border: "#FED7AA" }, // deep orange
  "CERT-In":           { bg: "#FFEDD5", text: "#9A3412", border: "#FED7AA" }, // deep orange (alias)
  "UGC":               { bg: "#E0F2FE", text: "#0C4A6E", border: "#BAE6FD" }, // sky
  "NAAC":              { bg: "#FEF9C3", text: "#713F12", border: "#FEF08A" }, // warm yellow
};

const DEFAULT_COLOR: FrameworkColor = {
  bg: "#F1F5F9",
  text: "#475569",
  border: "#CBD5E1",
};

/**
 * Returns the bg/text/border color triple for a given framework name.
 * Falls back to a neutral grey for unrecognized names.
 */
export function getFrameworkColor(name: string): FrameworkColor {
  if (!name) return DEFAULT_COLOR;
  // Exact match first
  if (FRAMEWORK_COLORS[name]) return FRAMEWORK_COLORS[name];
  // Partial match — check if any key is a substring of the name
  const key = Object.keys(FRAMEWORK_COLORS).find((k) =>
    name.toLowerCase().includes(k.toLowerCase())
  );
  return key ? FRAMEWORK_COLORS[key] : DEFAULT_COLOR;
}
