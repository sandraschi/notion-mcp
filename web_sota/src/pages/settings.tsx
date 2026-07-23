import { API_BASE } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CheckCircle, Cpu, Key, Loader2, ShieldCheck, XCircle } from "lucide-react";

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    useEffect(() => {
        fetch(API_BASE + "/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <div className="space-y-3">
            <Select value={selectedProvider} onValueChange={(v) => { setSelectedProvider(v); save(v, ""); }}>
                <SelectTrigger className="bg-slate-900 border-slate-800 text-slate-100">
                    <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 text-slate-100">
                    <SelectItem value="ollama">Ollama</SelectItem>
                    <SelectItem value="lm_studio">LM Studio</SelectItem>
                </SelectContent>
            </Select>
            <Select value={selectedModel} onValueChange={(v) => { setSelectedModel(v); save(selectedProvider, v); }}>
                <SelectTrigger className="bg-slate-900 border-slate-800 text-slate-100">
                    <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 text-slate-100">
                    {models.map((m) => <SelectItem key={m.name} value={m.name}>{m.name}</SelectItem>)}
                </SelectContent>
            </Select>
        </div>
    );
}

function NotionTokenSettings() {
    const [token, setToken] = useState("");
    const [saving, setSaving] = useState(false);
    const [result, setResult] = useState<{ ok: boolean; msg: string } | null>(null);
    const [status, setStatus] = useState<"checking" | "connected" | "disconnected">("checking");

    useEffect(() => {
        fetch(`${API_BASE}/api/status`)
            .then((r) => r.json())
            .then((d) => setStatus(d.authenticated ? "connected" : "disconnected"))
            .catch(() => setStatus("disconnected"));
    }, []);

    const handleSave = useCallback(async () => {
        if (!token.trim()) return;
        setSaving(true);
        setResult(null);
        try {
            const r = await fetch(`${API_BASE}/api/configure/token`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: token.trim() }),
            });
            const data = await r.json();
            setResult({ ok: data.authenticated, msg: data.message || (data.authenticated ? "Connected!" : "Token rejected.") });
            if (data.authenticated) setStatus("connected");
        } catch {
            setResult({ ok: false, msg: "Backend unreachable." });
        } finally {
            setSaving(false);
        }
    }, [token]);

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${status === "connected" ? "bg-emerald-500" : status === "disconnected" ? "bg-red-500" : "bg-gray-500"} animate-pulse`} />
                <span className="text-sm text-slate-300">
                    {status === "connected" ? "Connected to Notion" : status === "disconnected" ? "Not connected" : "Checking..."}
                </span>
            </div>
            <div className="flex gap-2">
                <input
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    type="password"
                    placeholder="Paste your Notion token here..."
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                />
                <button
                    onClick={handleSave}
                    disabled={saving || !token.trim()}
                    className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-30 disabled:cursor-not-allowed text-sm text-white transition-colors flex items-center gap-2"
                >
                    {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Key className="h-4 w-4" />}
                    Save
                </button>
            </div>
            {result && (
                <div className={`flex items-center gap-2 text-sm ${result.ok ? "text-emerald-400" : "text-red-400"}`}>
                    {result.ok ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                    {result.msg}
                </div>
            )}
            <p className="text-xs text-slate-500">
                Get your token at{" "}
                <a href="https://www.notion.so/my-integrations" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    notion.so/my-integrations
                </a>
            </p>
        </div>
    );
}

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
                <p className="text-slate-400">Configure Notion Workspace and AI reasoning preferences</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <ShieldCheck className="h-5 w-5 text-emerald-500" />
                            <CardTitle className="text-white">Notion Connection</CardTitle>
                        </div>
                        <CardDescription className="text-slate-400">API token and connection status</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <NotionTokenSettings />
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Cpu className="h-5 w-5 text-blue-500" />
                            <CardTitle className="text-white">Local LLM Configuration</CardTitle>
                        </div>
                        <CardDescription className="text-slate-400">Provider and model selection</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <LLMSettings />
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">App Information</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-1">
                        <p>Notion Hub v0.1.0 (SOTA)</p>
                        <p>Dual Transport: STDIO + HTTP (10811)</p>
                        <p>Frontend Port: 10810</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
