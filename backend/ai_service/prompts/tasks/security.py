# Use: IT Security Officer task prompts.
# Token target: under 200 tokens.

SECURITY_CERT_IN_DRAFT_PROMPT = """Task: Draft a formal CERT-In mandatory incident report from the incident data in <external_content>.

Output the report in this exact structure:
1. Organization Details — institution name, sector (Education / Indian University)
2. Incident Details — category (Ransomware / Unauthorized Access / Phishing / DoS / Other), date/time discovered, affected systems and IPs
3. Technical Analysis — containment status, suspected source or CVE, attack vector if known
4. Actions Taken / Planned — completed remediation steps, point of contact (name, designation, email)

Rules:
- Cite applicable CERT-In 2022 sections for each mandatory field.
- Mark any unknown field as [FILL IN: description].
- Formal, precise language — this is a regulatory submission."""
