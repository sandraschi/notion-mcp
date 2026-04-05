import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    FileText,
    Database,
    Users,
    History,
    RefreshCcw,
    Cpu
} from "lucide-react";
import { AuthSetup } from "@/components/auth/auth-setup";

interface Status {
    authenticated: boolean;
    workspace: string;
    server_running: boolean;
}

interface Stats {
    pages: number;
    databases: number;
    users: number;
}

interface Llm {
    name: string;
    provider: string;
    url: string;
}

export function Dashboard() {
    const [status, setStatus] = useState<Status | null>(null);
    const [stats, setStats] = useState<Stats | null>(null);
    const [llms, setLlms] = useState<Llm[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statusRes, llmsRes] = await Promise.all([
                    fetch('/api/status'),
                    fetch('/api/llm-discovery')
                ]);
                const statusData = await statusRes.json();
                const llmsData = await llmsRes.json();
                setStatus(statusData);
                setLlms(llmsData.llms || []);

                // Fetch stats only if authenticated
                if (statusData.authenticated) {
                    const statsRes = await fetch('/api/stats');
                    const statsData = await statsRes.json();
                    setStats(statsData);
                }
            } catch (error) {
                console.error("Plugins fetch failed", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
    );

    if (status && !status.authenticated) {
        return <AuthSetup />;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Notion Workspace Dashboard</h2>
                    <p className="text-slate-400">Workspace overview and real-time connectivity</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Total Pages</CardTitle>
                        <FileText className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{stats?.pages || 0}</div>
                        <p className="text-xs text-slate-400">Live from Notion</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Databases</CardTitle>
                        <Database className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{stats?.databases || 0}</div>
                        <p className="text-xs text-slate-400">Active structures</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Collaborators</CardTitle>
                        <Users className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{stats?.users || 0}</div>
                        <p className="text-xs text-slate-400">Active users</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Sync Status</CardTitle>
                        <History className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">Healthy</div>
                        <p className="text-xs text-slate-400">LanceDB RAG Online</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Local LLM Grid (Glom On)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {llms.length === 0 ? (
                                <p className="text-sm text-slate-500">No local LLMs detected (check Ollama/LM Studio)</p>
                            ) : llms.map((llm, i) => (
                                <div key={i} className="flex items-center justify-between border-b border-slate-800 pb-2 last:border-0 last:pb-0">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-slate-900 rounded-md">
                                            <Cpu className="h-4 w-4 text-emerald-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-slate-200">{llm.name}</p>
                                            <p className="text-xs text-slate-500">{llm.provider} • {llm.url}</p>
                                        </div>
                                    </div>
                                    <div className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase rounded border border-emerald-500/20">Active</div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">System Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Button title="Refresh Workspace Metadata" variant="ghost" size="icon" className="text-slate-500 hover:text-white">
                            <RefreshCcw className="h-4 w-4" />
                        </Button>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">FastMCP 3.1 Endpoint</p>
                                    <p className="text-xs text-slate-400">Port 10811 • SOTA Active</p>
                                </div>
                            </div>
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2 bg-emerald-500 rounded-full"></span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">Notion API</p>
                                    <p className="text-xs text-slate-400">Connected • Austrian Efficiency</p>
                                </div>
                            </div>
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2 bg-blue-500 rounded-full"></span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">LanceDB RAG</p>
                                    <p className="text-xs text-slate-400">Operational • Semantic Storage</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
