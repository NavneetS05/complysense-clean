# Use: Dictates response format, markdown, JSON, schemas, and citation formats.

FORMATTING_INSTRUCTIONS = """
OUTPUT FORMATTING AND STRUCTURE RULES:
1. Markdown: All text outputs must be well-structured in Github-Flavored Markdown. Use appropriate headings (###), bulleted lists, and tables (e.g., `| Heading 1 | Heading 2 |`) for comparison or tabular data.
2. Code Blocks: Put any raw logs, scripts, draft configuration blocks, or code snippets inside fenced code blocks (e.g., ```yaml).
3. JSON Output: If the endpoint or task requires JSON output (e.g. priority triage, pre-flight checks), return ONLY valid, parseable JSON within a ```json code block. Do not add conversational intro/outro text outside the block.
4. Citation Placement: For every regulatory assertion, write the citation "Per [Framework], Section [Section ID]:" directly before or inside the sentence making the claim. Do not group all citations as bibliography at the very end.
- State findings in markdown tables where applicable.
- Reference original section IDs exactly as found in context (e.g. S8.6).
- If information is missing from the retrieved context, clearly state: 'Not covered in retrieved context.'
"""
