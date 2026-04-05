import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send, Bot, User, Cpu, BookOpen } from "lucide-react";

interface Message {
    role: 'user' | 'bot';
    text: string;
    context?: { title: string; url: string; content: string }[];
}

export function Chat() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'bot', text: 'Hello! I am your RAG-powered Notion assistant. How can I help you manage your workspace today?' }
    ]);
    const [input, setInput] = useState("");
    const [llms, setLlms] = useState<{ name: string; provider: string; url: string }[]>([]);
    const [selectedLlm, setSelectedLlm] = useState<string>("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetch('/api/llm-discovery')
            .then(res => res.json())
            .then(data => {
                setLlms(data.llms || []);
                if (data.llms?.length > 0) setSelectedLlm(data.llms[0].url);
            });
    }, []);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMsg: Message = { role: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input, model_url: selectedLlm })
            });
            const data = await res.json();
            setMessages(prev => [...prev, {
                role: 'bot',
                text: data.reply,
                context: data.context
            }]);
        } catch {
            setMessages(prev => [...prev, { role: 'bot', text: "Error connecting to backend." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Notion Intelligence</h2>
                    <p className="text-slate-400">RAG-powered chat via Local LLM</p>
                </div>
                <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800">
                    <Cpu className="h-4 w-4 text-emerald-500 ml-2" />
                    <select
                        value={selectedLlm}
                        onChange={(e) => setSelectedLlm(e.target.value)}
                        className="bg-transparent text-xs text-slate-200 focus:outline-none p-1"
                        aria-label="Select LLM model"
                        title="Select LLM model"
                    >
                        {llms.length === 0 && <option value="">No LLMs detected</option>}
                        {llms.map((llm, i) => (
                            <option key={i} value={`${llm.provider}|${llm.url}|${llm.name}`}>
                                {llm.name} ({llm.provider})
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden">
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex gap-3 ${msg.role === 'user' ? '' : ''}`}>
                            <div className={`h-8 w-8 rounded-full flex items-center justify-center border ${msg.role === 'user' ? 'bg-slate-800 border-slate-700' : 'bg-blue-900/20 border-blue-800'
                                }`}>
                                {msg.role === 'user' ? <User className="h-4 w-4 text-slate-400" /> : <Bot className="h-4 w-4 text-blue-400" />}
                            </div>
                            <div className="flex-1 space-y-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium text-slate-200">{msg.role === 'user' ? 'Operator' : 'Notion AI'}</span>
                                </div>
                                <div className={`text-sm text-slate-300 p-3 rounded-md border inline-block ${msg.role === 'user' ? 'bg-slate-900/50 border-slate-800' : 'bg-blue-950/10 border-blue-900/30'
                                    }`}>
                                    <p>{msg.text}</p>

                                    {msg.context && msg.context.length > 0 && (
                                        <div className="mt-3 pt-3 border-t border-blue-900/20 space-y-2">
                                            <p className="text-[10px] font-bold text-blue-400 uppercase tracking-wider">Citations from Notion:</p>
                                            {msg.context.map((ctx, ci) => (
                                                <div key={ci} className="flex items-start gap-2 bg-slate-950/50 p-2 rounded border border-slate-800">
                                                    <BookOpen className="h-3 w-3 text-slate-500 mt-0.5" />
                                                    <div>
                                                        <p className="text-[11px] font-medium text-slate-300">{ctx.title}</p>
                                                        <p className="text-[10px] text-slate-500 line-clamp-2">{ctx.content}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                    {loading && <div className="text-xs text-blue-500 animate-pulse pl-11">RAG engine searching Notion...</div>}
                </CardContent>
                <div className="p-4 border-t border-slate-800 bg-slate-900/30">
                    <div className="flex gap-2">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            className="flex-1 bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                            placeholder="Ask me about your Notion knowledge..."
                        />
                        <Button onClick={handleSend} disabled={loading} size="icon" className="bg-blue-600 hover:bg-blue-700">
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
