import { useState } from "react";
import { Send } from "lucide-react";
import { PageShell } from "../../pages/PageShell";
import { api } from "../../lib/api";
import { CitationChip } from "./CitationChip";

type Message = { role: "user" | "assistant"; content: string };
type Citation = { framework?: string; source?: string; section?: string; title?: string };

interface RoleChatPageProps {
  title: string;
  context: string;
  endpoint: string;
  placeholder: string;
  prompts: string[];
}

export function RoleChatPage({ title, context, endpoint, placeholder, prompts }: RoleChatPageProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(text = input) {
    const query = text.trim();
    if (!query || loading) return;

    setInput("");
    setError(null);
    setLoading(true);

    const nextMessages: Message[] = [...messages, { role: "user", content: query }];
    setMessages(nextMessages);

    try {
      const { data } = await api.post(endpoint, { query, conversation_id: conversationId });
      setConversationId(data.conversation_id ?? null);
      setMessages([...nextMessages, { role: "assistant", content: data.response || "No answer returned." }]);
      setCitations(data.citations || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reach the AI assistant.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <PageShell title={title} context={context} />
      <section className="card" style={{ minHeight: 640, display: "grid", gridTemplateRows: "1fr auto", gap: 16 }}>
        <div style={{ overflow: "auto", display: "grid", alignContent: "start", gap: 12 }}>
          {messages.length === 0 ? (
            <div className="flex gap-2" style={{ flexWrap: "wrap" }}>
              {prompts.map((prompt) => (
                <button key={prompt} className="btn btn-secondary btn-sm" onClick={() => void send(prompt)}>
                  {prompt}
                </button>
              ))}
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={`${message.role}-${index}`} style={{ display: "flex", justifyContent: message.role === "user" ? "flex-end" : "flex-start" }}>
                <div style={{ maxWidth: "78%", border: "1px solid var(--border)", borderRadius: 8, padding: 12, background: message.role === "user" ? "var(--primary-light)" : "var(--surface-secondary)" }}>
                  <MarkdownLite text={message.content} />
                </div>
              </div>
            ))
          )}

          {loading ? <div className="text-sm text-secondary-color">Thinking...</div> : null}
          {error ? (
            <div className="form-error">
              {error}
              <button className="btn btn-ghost btn-sm" onClick={() => void send([...messages].reverse().find((message) => message.role === "user")?.content || "")}>Retry</button>
            </div>
          ) : null}

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
            placeholder={placeholder}
            rows={3}
          />
          <button className="btn btn-primary" onClick={() => void send()} disabled={loading || !input.trim()}>
            <Send size={16} />
          </button>
        </div>
      </section>
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
