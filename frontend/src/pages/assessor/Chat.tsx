// Use: Real read-only assessor RAG chat with persisted history.

import { useEffect, useState } from "react";
import { Send } from "lucide-react";
import { PageShell } from "../PageShell";
import { api } from "../../lib/api";
import { CitationChip } from "../../components/shared/CitationChip";

type Message = { role: "user" | "assistant"; content: string };
type Conversation = { conversation_id: string; title: string; updated_at?: string };
type Citation = { framework?: string; source?: string; section?: string; title?: string };

const prompts = [
  "Summarize current ISO 27001 readiness.",
  "Which DPDP obligations have the largest open gaps?",
  "Explain the latest audit findings in executive language.",
];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadConversations() {
    const { data } = await api.get<Conversation[]>("/api/v1/assessor/conversations");
    setConversations(data);
  }

  useEffect(() => {
    void loadConversations();
  }, []);

  async function loadConversation(id: string) {
    const { data } = await api.get<{ conversation_id: string; messages: Message[] }>(`/api/v1/assessor/conversations/${id}`);
    setConversationId(data.conversation_id);
    setMessages(data.messages);
    setCitations([]);
    setError(null);
  }

  async function send(text = input) {
    const query = text.trim();
    if (!query || loading) return;
    setInput("");
    setError(null);
    setLoading(true);
    const nextMessages: Message[] = [...messages, { role: "user", content: query }];
    setMessages(nextMessages);
    try {
      const { data } = await api.post("/api/v1/ai/assessor/chat", { query, conversation_id: conversationId });
      setConversationId(data.conversation_id);
      setMessages([...nextMessages, { role: "assistant", content: data.response || "No answer returned." }]);
      setCitations(data.citations || []);
      await loadConversations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reach assessor chat.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell title="Q&A Interface" context="Read-only regulatory and audit report Q&A." />
      <div style={{ display: "grid", gridTemplateColumns: "280px minmax(0, 1fr)", gap: 16 }}>
        <aside className="card" style={{ maxHeight: 640, overflow: "auto" }}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="card-title">History</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => { setConversationId(null); setMessages([]); setCitations([]); }}>New</button>
          </div>
          <div className="divide-y">
            {conversations.length === 0 ? <p className="text-sm text-secondary-color">No saved Q&A yet.</p> : conversations.map((conv) => (
              <button key={conv.conversation_id} className="dropdown-item" onClick={() => void loadConversation(conv.conversation_id)} style={{ display: "block", padding: "10px 0" }}>
                <div className="truncate font-medium">{conv.title}</div>
                <div className="text-xs text-secondary-color">{conv.updated_at ? new Date(conv.updated_at).toLocaleString() : ""}</div>
              </button>
            ))}
          </div>
        </aside>

        <section className="card" style={{ minHeight: 640, display: "grid", gridTemplateRows: "1fr auto", gap: 16 }}>
          <div style={{ overflow: "auto", display: "grid", alignContent: "start", gap: 12 }}>
            {messages.length === 0 ? (
              <div className="flex gap-2" style={{ flexWrap: "wrap" }}>
                {prompts.map((prompt) => <button key={prompt} className="btn btn-secondary btn-sm" onClick={() => void send(prompt)}>{prompt}</button>)}
              </div>
            ) : messages.map((message, index) => (
              <div key={`${message.role}-${index}`} style={{ display: "flex", justifyContent: message.role === "user" ? "flex-end" : "flex-start" }}>
                <div style={{ maxWidth: "78%", border: "1px solid var(--border)", borderRadius: 8, padding: 12, background: message.role === "user" ? "var(--primary-light)" : "var(--surface-secondary)" }}>
                  <MarkdownLite text={message.content} />
                </div>
              </div>
            ))}
            {loading ? <div className="text-sm text-secondary-color">Thinking...</div> : null}
            {error ? <div className="form-error">{error} <button className="btn btn-ghost btn-sm" onClick={() => void send([...messages].reverse().find((message) => message.role === "user")?.content || "")}>Retry</button></div> : null}
            {citations.length > 0 ? (
              <div>
                {citations.map((citation, index) => (
                  <CitationChip key={index} framework={citation.framework || citation.source || citation.title || "Source"} section={citation.section} />
                ))}
              </div>
            ) : null}
          </div>

          <div className="flex gap-2">
            <textarea
              className="form-textarea"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void send();
                }
              }}
              placeholder="Ask a read-only assessment question..."
              rows={3}
            />
            <button className="btn btn-primary" onClick={() => void send()} disabled={loading || !input.trim()}><Send size={16} /></button>
          </div>
        </section>
      </div>
    </div>
  );
}

function MarkdownLite({ text }: { text: string }) {
  return (
    <div style={{ whiteSpace: "pre-wrap" }}>
      {text.split("\n").map((line, index) => {
        const cleaned = line.replace(/^#{1,6}\s*/, "").replace(/\*\*(.*?)\*\*/g, "$1");
        return <p key={index} style={{ margin: index === 0 ? 0 : "6px 0 0" }}>{cleaned}</p>;
      })}
    </div>
  );
}
