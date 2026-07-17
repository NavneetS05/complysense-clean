import { RoleChatPage } from "../../components/shared/RoleChatPage";

export default function Chat() {
  return (
    <RoleChatPage
      title="Compliance AI Assistant"
      context="Ask about controls, evidence gaps, and overall compliance posture."
      endpoint="/api/v1/ai/compliance/chat"
      placeholder="Ask about controls, gaps, or evidence review..."
      prompts={[
        "Summarize open compliance gaps.",
        "What evidence items need immediate attention?",
        "Which controls are most at risk this month?",
      ]}
    />
  );
}
