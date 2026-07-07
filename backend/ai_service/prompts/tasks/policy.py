# Use: Policy conflict detection and executive summary prompts.

POLICY_CONFLICT_PROMPT = """You are reviewing a policy document for conflicts and regulatory compliance.
Analyze the policy document provided in <external_content>.

Structure your analysis:
### 1. Regulatory Obligations Map
- For each major clause in the policy, identify which regulatory framework it should comply with.
- Cite the framework sections that apply (e.g., "Per DPDP Act 2023, Section S7: ...").

### 2. Conflicts & Contradictions
- List any internal conflicts within the policy document.
- List any contradictions between the policy and the regulatory frameworks in context.
- Use format: **Conflict [N]**: [Description]

### 3. Missing Clauses
- Identify mandatory obligations from the retrieved frameworks that are NOT mentioned in the policy at all.

### 4. Verdict
- Approve (with minor corrections) | Reject (major gaps) | Request Revision
- Justification summary.
"""

POLICY_EXECUTIVE_SUMMARY_PROMPT = """You are writing an executive briefing for a university leadership team.
Summarize the institutional compliance status into a concise, senior-leadership-friendly report.

Your summary should:
1. Lead with overall compliance posture (color-coded: Green/Amber/Red with justification).
2. List top 3 critical risks currently facing the institution.
3. Identify quick wins (actions that can be completed within 30 days).
4. Include a medium-term roadmap (90-day plan).
5. Be no longer than 600 words. Use clear, jargon-free language suitable for a Vice-Chancellor briefing.
"""

