import { RoleChatPage } from "../../components/shared/RoleChatPage";

export default function Chat() {
  return (
    <RoleChatPage
      title="Security AI Assistant"
      context="Use AI to get incident context and security posture guidance."
      endpoint="/api/v1/ai/security/chat"
      placeholder="Ask about incidents, controls, or evidence..."
      prompts={[
        "Summarize the latest incident context.",
        "What controls should I review next?",
        "Explain the security exposure in simple terms.",
      ]}
    />
  );
}
