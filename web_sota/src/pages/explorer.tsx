import { Card, CardContent } from "@/components/ui/card";
import { FileText } from "lucide-react";
import { useState } from "react";
import { API_BASE } from "@/lib/api";

export function Explorer() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");

  const fetchItems = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(API_BASE + "/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() }),
      });
      if (res.ok) {
        const data = await res.json();
        setItems(data.results || []);
      }
    } catch (error) {
      console.warn("Explorer fetch failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Workspace Explorer
          </h2>
          <p className="text-slate-400">
            Search and browse your Notion content
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Search pages and databases..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") fetchItems(); }}
          className="flex-1 rounded-md border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-slate-200 outline-none focus:ring-2 focus:ring-blue-500/50"
        />
        <button
          onClick={fetchItems}
          disabled={loading || !query.trim()}
          className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 disabled:opacity-30 text-sm text-white transition-colors"
        >
          <FileText className="h-4 w-4" /> Search
        </button>
      </div>

      <div className="grid gap-4">
        {loading ? (
          <div className="flex justify-center p-8 text-slate-500">
            Searching...
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {query ? "No results found." : "Enter a search query to find pages and databases."}
          </div>
        ) : (
          items.map((item: any, i: number) => (
            <Card
              key={item.id || i}
              className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group"
            >
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-slate-900 rounded-lg group-hover:bg-slate-800">
                    <FileText className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-200">
                      {item.title || "Untitled"}
                    </p>
                    <p className="text-xs text-slate-500">{item.type || "page"}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
