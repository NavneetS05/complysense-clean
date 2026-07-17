import { RoleChatPage } from "../../components/shared/RoleChatPage";

export default function Chat() {
  return (
    <RoleChatPage
      title="Vendor AI Assistant"
      context="Ask about vendor risk, contract exposure, and DPDP posture."
      endpoint="/api/v1/ai/vendor/chat"
      placeholder="Ask about vendor obligations or contract clauses..."
      prompts={[
        "What are the main vendor risks in this contract?",
        "Summarize the DPDP exposure for this vendor.",
        "Which clauses should I review first?",
      ]}
    />
  );
}
