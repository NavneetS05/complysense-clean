# Use: Output formatting rules injected into system prompt.
# Token target: ~90 tokens. Injected by prompt_builder.py into every call.

FORMATTING_INSTRUCTIONS = """Output format rules:
- Use GitHub-Flavored Markdown: ### headings, bullet lists, tables.
- JSON endpoints: return ONLY a ```json block — no surrounding prose or commentary.
- Citations: place "Per [Framework], Section [ID]:" inline before each claim, never as end bibliography.
- Missing info: write exactly 'Not found in retrieved context.'"""
