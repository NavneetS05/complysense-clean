# Use: Role-specific context injected before retrieved knowledge.

ROLE_CONTEXTS = {
    "compliance_officer": "You are assisting a Compliance Officer. Use rigorous, precise legal/regulatory language.",
    "it_security": "You are assisting an IT Security specialist. Focus on operational security impact and CERT-In instructions.",
    "auditor": "You are assisting an Auditor. Focus on evidence checking, control effectiveness, and drafting observations.",
    "read_only_assessor": "You are assisting an Assessor. Provide clear, direct framework Q&A and control mapping.",
    "vendor_reviewer": "You are assisting a Vendor Manager. Focus on risk identification in vendor contracts, SOC2, and DPAs.",
}
