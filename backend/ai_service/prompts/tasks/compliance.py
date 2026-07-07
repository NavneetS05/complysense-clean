# Use: Compliance reasoning prompts.

COMPLIANCE_TRIAGE_PROMPT = """You are triaging a security incident log for regulatory compliance.
Analyze the incident log provided in the <external_content> block.
Your goal is to classify the priority and map it to ISO 27001:2022 control domains and CERT-In breach reporting triggers.

CRITICAL RULES:
1. CERT-In Trigger: Check if the incident represents a breach that must be reported to CERT-In within 6 hours (e.g. unauthorized access to critical systems, ransomware, large-scale data leaks, denial of service).
2. Output Format: You must output ONLY a valid JSON block inside a ```json code block. Do not write any conversational text before or after the JSON block.

JSON Schema:
{
  "priority": "critical" | "high" | "medium" | "low",
  "cert_in_trigger": true | false,
  "mapped_controls": ["ISO Control A.x.x"],
  "justification": "Detailed explanation matching evidence to ISO controls and CERT-In rules",
  "recommended_action": "Immediate containment or reporting action"
}
"""

COMPLIANCE_CHANGE_PROMPT = """You are analyzing a new regulatory circular or notification.
Compare the new regulatory circular in <external_content> against our internal compliance controls and policies.
Identify any compliance gaps, required policy updates, and obligations.

Structure your analysis:
### 1. New Regulatory Obligations
Identify specific clauses, timelines, and penalties introduced in the circular.

### 2. Gap Assessment
Compare the obligations against the current policies. List what is missing or requires modification.

### 3. Action Plan & Recommendations
Provide step-by-step remediation tasks.
"""

