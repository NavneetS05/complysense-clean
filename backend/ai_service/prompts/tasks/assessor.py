# Use: Read-Only Assessor task prompts.
# Token target: under 180 tokens.

ASSESSOR_TASK_PROMPT = """Task: Answer the assessor's compliance question using only the retrieved REGULATORY CONTEXT.

Instructions:
1. Identify the most relevant framework clause(s) that directly answer the query.
2. Cite each clause inline: "Per [Framework], Section [ID]: ..."
3. Provide a clear, direct answer in plain English — suitable for a board member or regulator.
4. If the topic spans multiple frameworks, address each with its own cited clause.
5. If no relevant clause is found, respond exactly: "This is not covered in the provided regulatory frameworks."

Keep the answer factual and concise (under 250 words). Do not extrapolate beyond what the retrieved context states."""
