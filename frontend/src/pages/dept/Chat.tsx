import { RoleChatPage } from "../../components/shared/RoleChatPage";

export default function Chat() {
  return (
    <RoleChatPage
      title="Department AI Assistant"
      context="Ask about control requirements, evidence readiness, and self-assessment guidance."
      endpoint="/api/v1/ai/dept/chat"
      placeholder="Ask about control requirements or evidence readiness..."
      prompts={[
        "Translate this control requirement into plain English.",
        "What evidence would best support this control?",
        "What should I review before submission?",
      ]}
    />
  );
}
