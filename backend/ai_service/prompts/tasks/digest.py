# Use: Morning compliance digest generation prompts.
# Token target: under 180 tokens.

DIGEST_TASK_PROMPT = """Task: Generate a personalized compliance morning digest for the user's role and institution using the context provided.

Structure the digest exactly as:
### 🔴 Priority Actions (Overdue or Due Today)
- Top 3 tasks requiring immediate attention — include control ID and brief reason.

### 🟡 Upcoming Deadlines (Next 7 Days)
- Key regulatory reporting deadlines or control due dates approaching.

### ⚠️ Risk Alerts
- Open incidents, failed controls, or expiring vendor certifications.

### ✅ Quick Win
- One action completable today in under 30 minutes.

Rules: Be concise. Plain language. Cite frameworks only for mandatory regulatory deadlines. If no data is available for a section, write "None identified." """
