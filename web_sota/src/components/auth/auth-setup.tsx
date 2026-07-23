import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";
import { CheckCircle, ExternalLink, Info, Key, Loader2, Share2, ShieldCheck, XCircle } from "lucide-react";

export function AuthSetup() {
  const [token, setToken] = useState("");
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; msg: string } | null>(null);

  const handleSave = async () => {
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
      if (data.authenticated) {
        setResult({ ok: true, msg: "Connected to Notion! Reloading..." });
        setTimeout(() => window.location.reload(), 1500);
      } else {
        setResult({ ok: false, msg: data.message || "Invalid token or connection failed." });
      }
    } catch {
      setResult({ ok: false, msg: "Could not reach the backend server. Is it running on port 10811?" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 bg-blue-500/10 rounded-full mb-4">
          <ShieldCheck className="h-8 w-8 text-blue-500" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-white">
          Connect to Notion
        </h2>
        <p className="text-slate-400 max-w-lg mx-auto">
          Enter your Notion integration token below to connect. No .env file editing needed.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50 max-w-xl mx-auto">
        <CardHeader>
          <CardTitle className="text-base text-white flex items-center gap-2">
            <Key className="h-4 w-4 text-emerald-500" />
            Notion Token
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            value={token}
            onChange={(e) => setToken(e.target.value)}
            type="password"
            placeholder="secret_your_integration_token_here"
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
          />
          <button
            onClick={handleSave}
            disabled={saving || !token.trim()}
            className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-medium text-white transition-colors flex items-center justify-center gap-2"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Key className="h-4 w-4" />}
            {saving ? "Connecting..." : "Connect to Notion"}
          </button>
          {result && (
            <div className={`flex items-center gap-2 text-sm ${result.ok ? "text-emerald-400" : "text-red-400"}`}>
              {result.ok ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
              {result.msg}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2 max-w-2xl mx-auto">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-blue-400 font-bold mb-2">1</div>
            <CardTitle className="text-base text-white">Get a Token</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-400 space-y-3">
            <p>Visit the Notion Developers portal to create a new internal integration.</p>
            <a href="https://www.notion.so/my-integrations" target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">
              Open Notion Integrations <ExternalLink className="h-3 w-3" />
            </a>
            <ol className="list-decimal list-inside space-y-1 text-xs text-slate-500">
              <li>Click "New integration"</li>
              <li>Name it "NotionMCP"</li>
              <li>Copy the "Internal Integration Secret"</li>
              <li>Paste it above and click Connect</li>
            </ol>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-purple-400 font-bold mb-2">2</div>
            <CardTitle className="text-base text-white">Share Pages</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-400 space-y-3">
            <p>Go to Notion, open the pages you want the integration to access, and connect it.</p>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Share2 className="h-3 w-3" /> Page menu {"->"} Connections {"->"} Add "NotionMCP"
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
