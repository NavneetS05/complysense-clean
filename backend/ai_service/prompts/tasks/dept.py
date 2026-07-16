# Use: Department Reviewer task prompts.
# Token targets: each prompt under 180 tokens.

DEPT_TRANSLATE_PROMPT = """Task: Translate the compliance control in <external_content> into plain English action steps for a department staff member.

Output:
1. **In plain terms**: One sentence explaining what this control requires in everyday language — no regulatory jargon.
2. **Steps to comply**: Numbered list of specific actions (Step 1, Step 2, ...) the department must take.
3. **Evidence to collect**: Bullet list of exact documents or screenshots needed to prove compliance.

Rules: No legal terminology. Write as if explaining to a lab manager with no compliance background."""

DEPT_PREFLIGHT_PROMPT = """Task: Perform a pre-flight compliance check on the uploaded evidence document in <external_content>.

Check whether the document contains sufficient evidence to satisfy the target control requirement.

Output ONLY a valid JSON block (no surrounding text):
```json
{
  "status": "pass" | "warn" | "fail",
  "confidence": 0.0,
  "missing_elements": ["specific missing details or required sections"],
  "feedback": "Actionable, plain-English explanation of what to fix or why it passes"
}
```

Status guide: pass = evidence is sufficient; warn = borderline, reviewer may question it; fail = wrong or unrelated document."""
