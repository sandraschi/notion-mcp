import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search as SearchIcon, BookOpen, ExternalLink, Filter } from "lucide-react";

export function SemanticSearch() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const res = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await res.json();
            setResults(data);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Semantic Search</h2>
                    <p className="text-slate-400">Discover knowledge across Notion using meaning and intent</p>
                </div>
            </div>

            <div className="flex gap-2">
                <div className="relative flex-1">
                    <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <Input
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="Search for concepts, projects, or technical notes..."
                        className="pl-10 bg-slate-950 border-slate-800 text-white focus:ring-blue-500"
                    />
                </div>
                <Button onClick={handleSearch} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
                    {loading ? "Searching..." : "Search"}
                </Button>
                <Button variant="outline" className="border-slate-800 text-slate-400 hover:text-white">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                </Button>
            </div>

            <div className="grid gap-4">
                {results.length === 0 && !loading && (
                    <div className="flex flex-col items-center justify-center py-20 bg-slate-950/20 border border-dashed border-slate-800 rounded-lg">
                        <SearchIcon className="h-12 w-12 text-slate-800 mb-4" />
                        <p className="text-slate-500">Enter a query to start semantic discovery</p>
                    </div>
                )}

                {results.map((result, i) => (
                    <Card key={i} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group">
                        <CardHeader className="flex flex-row items-start justify-between pb-2">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-slate-900 rounded-md">
                                    <BookOpen className="h-5 w-5 text-blue-400" />
                                </div>
                                <div>
                                    <CardTitle className="text-lg text-white group-hover:text-blue-400 transition-colors">
                                        {result.title}
                                    </CardTitle>
                                    <p className="text-xs text-slate-500">{result.url || "Workspace Resource"}</p>
                                </div>
                            </div>
                            <Button variant="ghost" size="icon" className="text-slate-600 hover:text-white">
                                <ExternalLink className="h-4 w-4" />
                            </Button>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-slate-300 leading-relaxed mb-4">
                                {result.content}
                            </p>
                            <div className="flex items-center gap-4 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                <span className="flex items-center">
                                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-2"></div>
                                    Relevance: {Math.round((1 - result._distance) * 100)}%
                                </span>
                                <span>Updated: {new Date(result.last_edited).toLocaleDateString()}</span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
