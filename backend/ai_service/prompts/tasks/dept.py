# Use: Department task instructions.

DEPT_TRANSLATE_PROMPT = """You are translating complex regulatory controls into plain action steps.
Explain the compliance controls in <external_content> using simple, action-oriented English that a department staff member can easily execute.

Rules:
1. Do not use complex legal jargon.
2. Outline specific steps: Step 1, Step 2, etc.
3. List the evidence artifacts that the department must produce to satisfy this control.
"""

DEPT_PREFLIGHT_PROMPT = """You are performing a pre-flight evidence compliance check on an uploaded document.
Review the extracted text of the document provided in <external_content> against the compliance requirement details.

CRITICAL RULES:
1. Check if the document actually contains the necessary evidence to satisfy the target control criteria.
2. Output Format: You must output ONLY a valid JSON block inside a ```json code block. Do not write any conversational text before or after the JSON block.

JSON Schema:
{
  "status": "pass" | "fail",
  "confidence": 0.0 - 1.0,
  "missing_elements": ["List of specific missing details or document sections"],
  "feedback": "Actionable feedback explaining how to fix the evidence document to make it pass"
}
"""
