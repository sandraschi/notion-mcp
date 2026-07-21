import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowUp, Bot, Download, Eraser, Mic, MicOff, Send, User, Volume2 } from "lucide-react";
import { API_BASE } from "@/lib/api";
import { createStt, initSpeechService, isSttAvailable, isTtsAvailable, speak } from "@/common/speech-service";

const STORAGE_KEY = "notion-mcp-chat-history";
const PERSONALITY_KEY = "notion-mcp-chat-personality";
const MAX_MESSAGES = 100;

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

interface Skill { name: string; path: string; }

const PERSONALITIES: Record<string, string> = {
  "research-assistant": "You are a thorough research assistant. Provide detailed, well-structured responses with citations where applicable. Prioritize accuracy over speed.",
  "expert-reviewer": "You are an expert reviewer. Analyze content critically, identify gaps, and provide constructive feedback. Be direct and honest.",
  "quick-summarizer": "You are a quick summarizer. Provide concise, bullet-point summaries. Get to the point immediately without preamble.",
  "custom": "",
};

const EXAMPLE_PROMPTS = [
  { group: "Search", prompts: ["Find pages about machine learning", "Search for recent project updates", "Show me my research database"] },
  { group: "Analysis", prompts: ["Summarize my recent pages", "What are the most active databases?", "Find content similar to this topic"] },
  { group: "Actions", prompts: ["Create a new page for meeting notes", "Show recent workspace changes", "What can you help me with?"] },
];

function SpeakButton({ text }: { text: string }) {
  const [speaking, setSpeaking] = useState(false);
  if (!isTtsAvailable()) return null;
  return (
    <button
      onClick={() => {
        if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); return; }
        setSpeaking(true);
        speak(text).then((s) => { s.done.then(() => setSpeaking(false)); }).catch(() => setSpeaking(false));
      }}
      className="p-1.5 rounded transition-colors text-slate-400 hover:text-white"
      title={speaking ? "Stop" : "Speak"}
    >
      <Volume2 className="h-3.5 w-3.5" />
    </button>
  );
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try { const saved = localStorage.getItem(STORAGE_KEY); return saved ? JSON.parse(saved) : []; } catch { return []; }
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [personalityId, setPersonalityId] = useState(() => {
    try { return localStorage.getItem(PERSONALITY_KEY) || "research-assistant"; } catch { return "research-assistant"; }
  });
  const [customPrompt, setCustomPrompt] = useState("");
  const [skillName, setSkillName] = useState<string | null>(null);
  const [providerStatus, setProviderStatus] = useState<"detecting" | "online" | "offline">("detecting");
  const [listening, setListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState("");
  const recognitionRef = useRef<ReturnType<typeof createStt> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { initSpeechService(); }, []);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_MESSAGES)));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(PERSONALITY_KEY, personalityId);
  }, [personalityId]);

  useEffect(() => {
    fetch(`${API_BASE}/api/skills`)
      .then((r) => r.json())
      .then((data) => {
        const skills: Skill[] = data.skills || [];
        if (skills.length > 0) setSkillName(skills[0].name);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/api/llm-discovery`)
      .then((r) => r.json())
      .then((data) => setProviderStatus(data.llms?.length > 0 ? "online" : "offline"))
      .catch(() => setProviderStatus("offline"));
  }, []);

  useEffect(() => {
    if (!isSttAvailable()) return;
    recognitionRef.current = createStt(
      (transcript, isFinal) => {
        if (isFinal) {
          setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
          setInterimTranscript("");
        } else {
          setInterimTranscript(transcript);
        }
      },
      () => setListening(false),
    );
    return () => { recognitionRef.current?.stop(); };
  }, []);

  const buildSystemPrompt = useCallback(() => {
    if (personalityId === "custom") return customPrompt || "You are a helpful Notion assistant.";
    const role = PERSONALITIES[personalityId] || "You are a helpful Notion assistant.";
    return `You are an expert Notion workspace manager with access to pages, databases, comments, and RAG search.\n\n---\n\n## Role\n${role}`;
  }, [personalityId, customPrompt]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: input.trim(), ts: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const systemPrompt = buildSystemPrompt();
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.content, system_prompt: systemPrompt }),
      });
      const data = await res.json();
      const reply = data.reply || data.message || "No response received.";
      setMessages((prev) => [...prev, { role: "assistant", content: reply, ts: new Date().toISOString() }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Error connecting to backend. Please check that the server is running.", ts: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, buildSystemPrompt]);

  const handleExport = useCallback(() => {
    if (messages.length === 0) return;
    const lines = messages.map((m) => `[${m.ts || "unknown"}] ${m.role === "user" ? "User" : "Assistant"}: ${m.content}`);
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `notion-mcp-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }, [messages]);

  const handleClear = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const toggleMic = useCallback(() => {
    if (!recognitionRef.current) return;
    if (listening) { recognitionRef.current.stop(); }
    else { recognitionRef.current.start(); setListening(true); }
  }, [listening]);

  const providerDot = providerStatus === "online" ? "bg-emerald-500" : providerStatus === "offline" ? "bg-red-500" : "bg-gray-500";
  const providerLabel = providerStatus === "online" ? "Ollama / LM Studio" : providerStatus === "offline" ? "Not detected" : "Detecting...";

  return (
    <div data-testid="chat-page" className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div data-testid="chat-controls" className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Notion Intelligence</h2>
          <p className="text-slate-400">RAG-powered chat via Local LLM</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-800">
            <span className={`w-2 h-2 rounded-full ${providerDot} animate-pulse`} />
            <span className="text-xs text-slate-400">{providerLabel}</span>
          </div>
          {skillName && (
            <div className="bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-800 text-xs text-slate-400">
              skill:{skillName}
            </div>
          )}
          <select
            data-testid="personality-select"
            value={personalityId}
            onChange={(e) => setPersonalityId(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none"
          >
            <option value="research-assistant">Research Assistant</option>
            <option value="expert-reviewer">Expert Reviewer</option>
            <option value="quick-summarizer">Quick Summarizer</option>
            <option value="custom">Custom</option>
          </select>
          <button
            data-testid="chat-export"
            onClick={handleExport}
            disabled={messages.length === 0}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed border border-slate-800 bg-slate-900"
            title="Export chat"
          >
            <Download className="h-4 w-4" />
          </button>
          <button
            data-testid="chat-clear"
            onClick={handleClear}
            disabled={messages.length === 0}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed border border-slate-800 bg-slate-900"
            title="Clear chat"
          >
            <Eraser className="h-4 w-4" />
          </button>
        </div>
      </div>

      {personalityId === "custom" && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-3">
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Write your custom system prompt here..."
            className="w-full bg-transparent text-xs text-slate-300 focus:outline-none resize-none h-16"
          />
        </div>
      )}

      <div className="flex-1 border border-slate-800 bg-slate-950/50 rounded-lg flex flex-col overflow-hidden">
        <div data-testid="chat-messages" className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
              <Bot className="h-10 w-10 text-slate-600" />
              <p className="text-slate-400 text-sm max-w-md">
                Ask me anything about your Notion workspace. I can search pages, query databases, and summarize content.
              </p>
              <div data-testid="example-prompts" className="flex flex-wrap gap-2 justify-center max-w-lg mt-2">
                {EXAMPLE_PROMPTS.flatMap((g) => g.prompts).map((p, i) => (
                  <button
                    key={i}
                    onClick={() => { setInput(p); inputRef.current?.focus(); }}
                    className="px-3 py-1.5 text-xs bg-slate-900 border border-slate-700 rounded-full text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === "user" ? "" : ""}`}>
              <div className={`h-8 w-8 rounded-full flex items-center justify-center border shrink-0 ${msg.role === "user" ? "bg-slate-800 border-slate-700" : "bg-blue-900/20 border-blue-800"}`}>
                {msg.role === "user" ? <User className="h-4 w-4 text-slate-400" /> : <Bot className="h-4 w-4 text-blue-400" />}
              </div>
              <div className="flex-1 space-y-1.5 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-200">{msg.role === "user" ? "You" : "Notion AI"}</span>
                  {msg.ts && <span className="text-[10px] text-slate-600">{new Date(msg.ts).toLocaleTimeString()}</span>}
                </div>
                <div className={`text-sm text-slate-300 p-3 rounded-lg border inline-block max-w-[85%] ${msg.role === "user" ? "bg-slate-900/50 border-slate-800" : "bg-blue-950/10 border-blue-900/30"}`}>
                  <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                </div>
                {msg.role === "assistant" && <SpeakButton text={msg.content} />}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full flex items-center justify-center border bg-blue-900/20 border-blue-800 shrink-0">
                <Bot className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex items-center gap-2 text-xs text-blue-400">
                <span className="animate-pulse">Thinking</span>
                <span className="animate-ping">...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-900/30">
          <div className="flex gap-2 items-center">
            {isSttAvailable() && (
              <button
                onClick={toggleMic}
                title={listening ? "Stop recording" : "Voice input"}
                className={`p-2 rounded-lg border transition-colors ${listening ? "bg-red-900/30 border-red-700 text-red-400" : "bg-slate-900 border-slate-700 text-slate-400 hover:text-white"}`}
              >
                {listening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>
            )}
            <input
              ref={inputRef}
              data-testid="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder={listening && interimTranscript ? interimTranscript : "Ask about your Notion workspace..."}
            />
            <button
              data-testid="chat-send"
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4 text-white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
