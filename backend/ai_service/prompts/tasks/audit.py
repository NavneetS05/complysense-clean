# Use: Audit task instructions.

AUDIT_SAMPLE_SIZE_PROMPT = """You are calculating a statistically valid audit sample size for control testing.
Calculate the sample size based on the population size, control frequency, and risk parameters provided in <external_content>.

CRITICAL RULES:
1. Explain the sampling methodology (e.g. attribute sampling).
2. Recommend sample sizes for populations (e.g. daily, weekly, monthly, quarterly controls).
3. Frame recommendations in a clean Markdown table.
"""

AUDIT_OBSERVATION_PROMPT = """You are drafting a formal Audit Observation.
Analyze the compliance findings and evidence provided in <external_content> against the regulatory criteria.

Draft the observation following the strict structure below:
### Audit Observation
- **Condition**: Describe the current state/finding (what was found, or what is failing).
- **Criteria**: State the target compliance requirement (what is required by the framework). Include a formal citation.
- **Cause**: Explain the underlying reason for the gap (why it happened).
- **Effect**: Outline the compliance/security/financial risk (what is the consequence).
- **Recommendation**: Provide concrete remediation steps to solve the condition.
"""
