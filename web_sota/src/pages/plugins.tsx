import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CheckCircle2, Plus, Cpu, Zap } from "lucide-react";

interface Plugin {
    id: string;
    name: string;
    description: string;
    status: 'installed' | 'available';
    author: string;
}

export function Plugins() {
    const [plugins, setPlugins] = useState<Plugin[]>([]);

    const fetchPlugins = async () => {
        try {
            const res = await fetch('/api/plugins');
            const data = await res.json();
            setPlugins(data.plugins || []);
        } catch (error) {
            console.error("Plugins fetch failed", error);
        }
    };

    const installPlugin = async (id: string) => {
        try {
            await fetch(`/api/plugins/install/${id}`, { method: 'POST' });
            fetchPlugins();
        } catch (error) {
            console.error("Install failed", error);
        }
    };

    useEffect(() => {
        fetchPlugins();
    }, []);

    const installed = plugins.filter(p => p.status === 'installed');
    const available = plugins.filter(p => p.status === 'available');

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Plugin Registry</h2>
                <p className="text-slate-400">Extend NotionMCP with SOTA integrations and local scripts</p>
            </div>

            <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-widest">Active Plugins</h3>
                <div className="grid gap-4 md:grid-cols-2">
                    {installed.length === 0 ? (
                        <div className="col-span-2 p-8 border border-dashed border-slate-800 rounded-lg text-center text-slate-500">
                            No local plugins active. Start by building a script in the `plugins/` directory.
                        </div>
                    ) : installed.map((plugin) => (
                        <Card key={plugin.id} className="border-slate-800 bg-slate-900/30">
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <div className="p-1.5 bg-emerald-500/10 rounded">
                                            <Cpu className="h-4 w-4 text-emerald-500" />
                                        </div>
                                        <CardTitle className="text-base text-white">{plugin.name}</CardTitle>
                                    </div>
                                    <span className="flex items-center gap-1 text-[10px] text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-bold uppercase">
                                        <CheckCircle2 className="h-3 w-3" /> Active
                                    </span>
                                </div>
                                <CardDescription className="text-slate-400">{plugin.description}</CardDescription>
                            </CardHeader>
                        </Card>
                    ))}
                </div>
            </div>

            <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-widest">SOTA Marketplace (Notion Ecosystem)</h3>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {available.map((plugin) => (
                        <Card key={plugin.id} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-all group">
                            <CardHeader className="pb-4">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="p-2 bg-slate-900 rounded-lg group-hover:bg-slate-800">
                                        <Zap className="h-5 w-5 text-blue-400" />
                                    </div>
                                    <button
                                        onClick={() => installPlugin(plugin.id)}
                                        className="text-xs font-medium text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                    >
                                        <Plus className="h-3 w-3" /> Connect
                                    </button>
                                </div>
                                <CardTitle className="text-base text-white">{plugin.name}</CardTitle>
                                <CardDescription className="text-xs text-slate-500 line-clamp-2">
                                    {plugin.description}
                                </CardDescription>
                            </CardHeader>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}
