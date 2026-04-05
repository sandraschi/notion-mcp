import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Search, FileText, Database, ExternalLink, RefreshCcw } from "lucide-react";

interface ExplorerItem {
    id: string;
    title: string;
    type: string;
    last_edited: string;
    url: string;
}

export function Explorer() {
    const [items, setItems] = useState<ExplorerItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState("");

    const fetchItems = async () => {
        setLoading(true);
        try {
            // In a real SOTA implementation, this would call an endpoint that lists recent pages
            // For now, we use the search tool if available, or a mock list
            // The fetch call below is currently unused as items are hardcoded for simulation.
            // In a real scenario, this would be used to fetch data: await fetch('/api/explorer');
            // Simulation logic
            setItems([
                { id: "1", title: "Project Alpha Roadmap", type: "page", last_edited: "2 hours ago", url: "https://notion.so/..." },
                { id: "2", title: "Engineering Wiki", type: "database", last_edited: "5 hours ago", url: "https://notion.so/..." },
                { id: "3", title: "Weekly Sync Notes", type: "page", last_edited: "Yesterday", url: "https://notion.so/..." },
                { id: "4", title: "Component Library", type: "database", last_edited: "2 days ago", url: "https://notion.so/..." },
            ]);
        } catch (error) {
            console.error("Explorer fetch failed", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Workspace Explorer</h2>
                    <p className="text-slate-400">Browse and manage your Notion content</p>
                </div>
                <button
                    onClick={fetchItems}
                    className="flex items-center gap-2 rounded-md bg-slate-900 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
                >
                    <RefreshCcw className="h-4 w-4" /> Refresh
                </button>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                    type="text"
                    placeholder="Search pages and databases..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full rounded-md border border-slate-800 bg-slate-950 px-10 py-2 text-sm text-slate-200 outline-none focus:ring-2 focus:ring-blue-500/50"
                />
            </div>

            <div className="grid gap-4">
                {loading ? (
                    <div className="flex justify-center p-8 text-slate-500">Scanning workspace...</div>
                ) : (
                    items.map((item) => (
                        <Card key={item.id} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group">
                            <CardContent className="p-4 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="p-2 bg-slate-900 rounded-lg group-hover:bg-slate-800">
                                        {item.type === 'page' ? <FileText className="h-5 w-5 text-emerald-400" /> : <Database className="h-5 w-5 text-blue-400" />}
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-slate-200">{item.title}</p>
                                        <p className="text-xs text-slate-500">Edited {item.last_edited}</p>
                                    </div>
                                </div>
                                <a
                                    href={item.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    title={`Open ${item.title} in Notion`}
                                    className="p-2 text-slate-500 hover:text-white transition-colors"
                                >
                                    <ExternalLink className="h-4 w-4" />
                                </a>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
}
