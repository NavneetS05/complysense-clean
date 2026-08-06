# Use: Read-Only Assessor task prompts.
# Token target: under 180 tokens.

ASSESSOR_TASK_PROMPT = """Task: Answer the assessor's compliance question using the provided LIVE INSTITUTION DATABASE CONTEXT and retrieved REGULATORY CONTEXT.

Instructions:
1. If the question asks about open gaps, policies, controls, or assessments in the registered institution, summarize the information directly from the LIVE INSTITUTION DATABASE CONTEXT.
2. Route regulatory framework questions to the narrowest relevant framework(s) and cite clauses inline: "Per [Framework], Section [ID]: ..."
3. Provide a clear, professional, direct answer suitable for an auditor, board member, or regulator.
4. Keep the answer factual, structured, and helpful (under 300 words)."""
