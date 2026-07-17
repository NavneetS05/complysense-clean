import { RoleChatPage } from "../../components/shared/RoleChatPage";

export default function Chat() {
  return (
    <RoleChatPage
      title="Audit AI Assistant"
      context="Query evidence quality, assessments, and audit follow-up questions."
      endpoint="/api/v1/ai/audit/chat"
      placeholder="Ask about assessments, evidence, or audit findings..."
      prompts={[
        "Summarize the highest-priority audit observations.",
        "Which controls need stronger evidence?",
        "Explain the assessment gaps in executive language.",
      ]}
    />
  );
}
