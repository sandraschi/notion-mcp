import { AuthSetup } from "@/components/auth/auth-setup";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Cpu,
  Database,
  FileText,
  RefreshCcw,
  Users,
} from "lucide-react";
import { API_BASE } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";

interface Status {
  authenticated: boolean;
  workspace: string;
  server_running: boolean;
}

interface BackendStats {
  total_requests: number;
  total_errors: number;
  success_rate: number;
}

interface Llm {
  name: string;
  provider: string;
  url: string;
}

export function Dashboard() {
  const [status, setStatus] = useState<Status | null>(null);
  const [stats, setStats] = useState<BackendStats | null>(null);
  const [llms, setLlms] = useState<Llm[]>([]);
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
    } catch (error) {
      console.warn("Dashboard fetch failed", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading)
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );

  if (status && !status.authenticated) {
    return <AuthSetup />;
  }

  const notionDot = status?.authenticated ? "bg-emerald-500" : "bg-red-500";
  const notionLabel = status?.authenticated ? "Connected" : "No token set";

  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Notion Dashboard
          </h2>
          <p className="text-slate-400">
            {status?.workspace || "Workspace"} — overview and connectivity
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-pages">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              API Requests
            </CardTitle>
            <FileText className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats?.total_requests ?? "?"}
            </div>
            <p className="text-xs text-slate-400">Total this session</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-databases">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              API Errors
            </CardTitle>
            <Database className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats?.total_errors ?? "?"}
            </div>
            <p className="text-xs text-slate-400">Errors this session</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Success Rate
            </CardTitle>
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
            <CardTitle className="text-sm font-medium text-slate-200">
              LLM Status
            </CardTitle>
            <RefreshCcw className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {llms.length > 0 ? `${llms.length} found` : "None"}
            </div>
            <p className="text-xs text-slate-400">
              {llms.length > 0 ? "Ollama / LM Studio" : "No local LLM detected"}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">
              Local LLMs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {llms.length === 0 ? (
                <p className="text-sm text-slate-500">
                  No local LLMs detected. Start Ollama or LM Studio to enable AI features.
                </p>
              ) : (
                llms.map((llm, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between border-b border-slate-800 pb-2 last:border-0 last:pb-0"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-slate-900 rounded-md">
                        <Cpu className="h-4 w-4 text-emerald-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">
                          {llm.name}
                        </p>
                        <p className="text-xs text-slate-500">
                          {llm.provider} at {llm.url}
                        </p>
                      </div>
                    </div>
                    <div className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase rounded border border-emerald-500/20">
                      Detected
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3 border-slate-800 bg-slate-950/50" data-testid="kpi-system">
          <CardHeader>
            <CardTitle className="text-white">System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <span className={`flex h-2 w-2 mr-2 rounded-full ${status?.server_running ? "bg-emerald-500" : "bg-red-500"}`}></span>
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    Backend Server
                  </p>
                  <p className="text-xs text-slate-400">
                    Port 10811 {status?.server_running ? "Running" : "Down"}
                  </p>
                </div>
              </div>
              <div className="flex items-center">
                <span className={`flex h-2 w-2 mr-2 rounded-full ${notionDot}`}></span>
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    Notion API
                  </p>
                  <p className="text-xs text-slate-400">{notionLabel}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
