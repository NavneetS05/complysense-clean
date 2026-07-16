# Use: Read-Only Assessor task prompts.
# Token target: under 180 tokens.

ASSESSOR_TASK_PROMPT = """Task: Answer the assessor's compliance question using only the retrieved REGULATORY CONTEXT.

Instructions:
1. Route the answer to the narrowest relevant framework(s) for the question.
2. Use only clauses that are present in the retrieved context and cite each one inline: "Per [Framework], Section [ID]: ..."
3. Provide a clear, direct answer in plain English — suitable for a board member or regulator.
4. If the topic spans multiple frameworks, address each with its own cited clause.
5. If no relevant clause is found, respond exactly: "This is not covered in the provided regulatory frameworks."
6. Do not speculate beyond the retrieved context or add policy advice not grounded in the cited framework(s).

Keep the answer factual and concise (under 250 words)."""
