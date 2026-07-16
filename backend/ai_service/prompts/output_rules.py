# Use: Output formatting rules injected into system prompt.
# Token target: ~90 tokens. Injected by prompt_builder.py into every call.

FORMATTING_INSTRUCTIONS = """Output format rules:
- Use GitHub-Flavored Markdown: ### headings, bullet lists, tables.
- JSON endpoints: return ONLY a ```json block — no surrounding prose or commentary.
- Citations: place a grounded citation inline before each factual claim, using the retrieved framework and section information only.
- Missing info: write exactly 'Not found in retrieved context.'
- If multiple frameworks apply, keep the answer organized by framework and cite each one separately.
- For privacy or consent questions, prefer DPDP; for incident reporting, prefer CERT-In; for security controls, prefer ISO 27001 or NIST; for institutional policy or accreditation, prefer UGC or NAAC.
- Do not include unsupported legal interpretations or generic advice not anchored in the retrieved context."""
