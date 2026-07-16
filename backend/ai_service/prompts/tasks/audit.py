# Use: Auditor task prompts.
# Token targets: each prompt under 180 tokens.

AUDIT_SAMPLE_SIZE_PROMPT = """Task: Calculate a statistically valid audit sample size from the population and risk parameters in <external_content>.

Output:
1. Sampling Methodology — name the method (e.g., attribute sampling) and justify its selection for this control type.
2. Sample Size Table — markdown table with columns: Control | Frequency | Population | Recommended Sample | Confidence Level.
3. Risk Notes — flag any control where sample exceeds 25% of population, or where the control frequency is high-risk.

Base recommendations on recognized auditing standards (IAASB ISA 530, ISACA) where cited in retrieved context."""

AUDIT_OBSERVATION_PROMPT = """Task: Draft a formal audit observation from the evidence and findings in <external_content>.

Use the exact five-point structure below — do not omit or reorder sections:
- **Condition**: What was found or is currently failing (specific, factual).
- **Criteria**: The applicable framework requirement — cite: "Per [Framework], Section [ID]:"
- **Cause**: The root reason this gap exists (process failure, resource, awareness).
- **Effect**: The compliance, operational, or financial risk if unresolved.
- **Recommendation**: 2-3 specific, assignable remediation steps.

Tone: neutral, objective, evidence-driven. Do not recommend actions outside the audit scope."""
