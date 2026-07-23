import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Cpu, Database, FileText, Users } from "lucide-react";
import { API_BASE } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";

interface StatusData {
  authenticated: boolean;
  workspace: string;
  server_running: boolean;
}

interface BackendStats {
  total_requests: number;
  total_errors: number;
  success_rate: number;
}

interface LlmInfo {
  name: string;
  provider: string;
  url: string;
}

export function Status() {
  const [status, setStatus] = useState<StatusData | null>(null);
  const [stats, setStats] = useState<BackendStats | null>(null);
  const [llms, setLlms] = useState<LlmInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, llmsRes] = await Promise.all([
        fetch(API_BASE + "/api/status"),
        fetch(API_BASE + "/api/llm-discovery"),
      ]);
      const statusData = await statusRes.json();
      const llmsData = await llmsRes.json();
      setStatus(statusData);
      setLlms(llmsData.llms || []);
      if (statusData.authenticated) {
        const statsRes = await fetch(API_BASE + "/api/stats");
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      }
    } catch {
      console.warn("Status fetch failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const notionDot = status?.authenticated ? "bg-emerald-500" : "bg-red-500";
  const notionLabel = status?.authenticated ? "Connected" : "No token set";

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">System Status</h2>
        <p className="text-slate-400">Backend, API, and LLM connectivity</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">API Requests</CardTitle>
            <FileText className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.total_requests ?? "?"}</div>
            <p className="text-xs text-slate-400">This session</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">API Errors</CardTitle>
            <Database className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.total_errors ?? "?"}</div>
            <p className="text-xs text-slate-400">This session</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Success Rate</CardTitle>
            <Users className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats?.success_rate != null ? `${(stats.success_rate * 100).toFixed(0)}%` : "?"}
            </div>
            <p className="text-xs text-slate-400">Notion API calls</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">LLMs Found</CardTitle>
            <Cpu className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{llms.length}</div>
            <p className="text-xs text-slate-400">{llms.length > 0 ? "Ollama / LM Studio" : "None detected"}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Services</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center">
              <span className={`flex h-2 w-2 mr-2 rounded-full ${status?.server_running ? "bg-emerald-500" : "bg-red-500"}`}></span>
              <div className="ml-2 space-y-1">
                <p className="text-sm font-medium text-white">Backend Server</p>
                <p className="text-xs text-slate-400">Port 10811 {status?.server_running ? "Running" : "Down"}</p>
              </div>
            </div>
            <div className="flex items-center">
              <span className={`flex h-2 w-2 mr-2 rounded-full ${notionDot}`}></span>
              <div className="ml-2 space-y-1">
                <p className="text-sm font-medium text-white">Notion API</p>
                <p className="text-xs text-slate-400">{notionLabel}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {llms.length > 0 && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Local LLMs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {llms.map((llm, i) => (
                <div key={i} className="flex items-center justify-between border-b border-slate-800 pb-2 last:border-0 last:pb-0">
                  <div>
                    <p className="text-sm text-slate-200">{llm.name}</p>
                    <p className="text-xs text-slate-500">{llm.provider} at {llm.url}</p>
                  </div>
                  <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase rounded border border-emerald-500/20">Detected</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
