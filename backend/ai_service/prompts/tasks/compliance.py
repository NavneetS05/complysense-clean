# Use: Compliance officer AI task prompts.
# Token targets: each prompt under 200 tokens.

COMPLIANCE_TRIAGE_PROMPT = """Task: Triage the compliance alert log in <external_content> — classify severity and map to regulatory controls.

CERT-In Trigger: Set true if the incident involves unauthorized access to critical systems, ransomware, large-scale data breach, or DoS — all require CERT-In reporting within 6 hours (Per CERT-In 2022).

Output ONLY a valid JSON block (no surrounding text):
```json
{
  "priority": "critical" | "high" | "medium" | "low",
  "cert_in_trigger": true | false,
  "mapped_controls": ["ISO A.x.x"],
  "justification": "1-2 sentences matching evidence to specific controls",
  "recommended_action": "The single most urgent next step"
}
```"""

COMPLIANCE_CHANGE_PROMPT = """Task: Analyse the regulatory circular in <external_content> and identify compliance gaps against our current controls.

Step 1 — New Obligations: List specific clauses, timelines, and penalties introduced by the circular.
Step 2 — Gap Assessment: For each obligation, classify as COVERED | PARTIAL | GAP against existing controls.
Step 3 — Action Plan: For each GAP or PARTIAL, recommend a specific, assignable remediation task.
Step 4 — Timeline Risk: If a hard regulatory deadline is found, flag it prominently.

Cite every obligation: "Per [Framework], Section [ID]:" """
