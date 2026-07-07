# Use: Vendor task instructions.

VENDOR_CONTRACT_PROMPT = """You are analyzing a vendor contract / DPA (Data Processing Agreement) or SOC2 report.
Analyze the document provided in <external_content> against DPDP Act 2023 processor obligations and general cybersecurity controls.

Structure your analysis:
### 1. DPDP Processor Compliance
- **Data Processor Oversight**: Does the contract establish clear instructions from the Data Fiduciary (the university)?
- **Data Deletion Obligations**: Is there a concrete deletion timeline when processing terminates?
- **Breach Notification**: Does the processor commit to reporting breaches immediately?
- **Cross-Border Restrictions**: Are there any restricted countries or cross-border sharing clauses?

### 2. Security Control Validation (SOC2 / ISO)
- Identify audit coverage, exceptions, or missing operational security controls.

### 3. Risk Rating & Verdict
- Overall Risk: High / Medium / Low
- Summary of risks and suggested contract modifications.
"""
