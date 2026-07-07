# Use: Security task instructions.

SECURITY_CERT_IN_DRAFT_PROMPT = """You are preparing a formal cybersecurity incident reporting draft for CERT-In (Indian Computer Emergency Response Team).
Review the incident logs/details provided in the <external_content> block.

Draft the report containing these official sections:
### CERT-In Incident Report Draft
1. **Reporting Organization Details**:
   - Organization Name: [Institution Name]
   - Sector: Education / Indian University

2. **Incident Details**:
   - Category of Incident (e.g. Ransomware, Unauthorized Access, Phishing, DoS)
   - Date and time of incident discovery
   - System/Application affected

3. **Technical Analysis**:
   - Containment status
   - Suspected source / IP address / vulnerability details (if available)

4. **Action Taken / Planned**:
   - Initial remediation actions
   - Point of contact

Make sure to cite CERT-In rules where relevant: "Per CERT-In 2022, Section [Section ID]:".
"""
