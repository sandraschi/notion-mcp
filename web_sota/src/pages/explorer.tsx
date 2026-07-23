import { Card, CardContent } from "@/components/ui/card";
import { ExternalLink, FileText, Globe, Search as SearchIcon, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

interface NotionItem {
  id: string;
  title: string;
  type: string;
  url: string;
  last_edited: string;
}

interface PageContent {
  id: string;
  title: string;
  url: string;
  last_edited: string;
  blocks: { type: string; text: string }[];
}

export function Explorer() {
  const [items, setItems] = useState<NotionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(false);
  const [selectedPage, setSelectedPage] = useState<PageContent | null>(null);
  const [pageLoading, setPageLoading] = useState(false);

  const fetchRecent = useCallback(async () => {
    setLoading(true);
    setSearched(false);
    try {
      const res = await fetch(API_BASE + "/api/recent?limit=50");
      if (res.ok) {
        const data = await res.json();
        setItems(data.items || []);
      }
    } catch {
      console.warn("Failed to fetch recent items");
    } finally {
      setLoading(false);
    }
  }, []);

  const searchItems = useCallback(async () => {
    if (!query.trim()) { fetchRecent(); return; }
    setLoading(true);
    setSearched(true);
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
    } catch {
      console.warn("Search failed");
    } finally {
      setLoading(false);
    }
  }, [query, fetchRecent]);

  const openPage = useCallback(async (pageId: string) => {
    setPageLoading(true);
    try {
      const res = await fetch(API_BASE + `/api/page/${pageId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedPage(data);
      }
    } catch {
      console.warn("Failed to load page");
    } finally {
      setPageLoading(false);
    }
  }, []);

  useEffect(() => { fetchRecent(); }, [fetchRecent]);

  const formatDate = (iso: string) => {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      const now = new Date();
      const diff = now.getTime() - d.getTime();
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      return d.toLocaleDateString();
    } catch { return ""; }
  };

  const pages = items.filter((i) => i.type === "page");
  const databases = items.filter((i) => i.type === "database");

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Workspace Explorer</h2>
        <p className="text-slate-400">
          {searched
            ? `${items.length} results for "${query}"`
            : items.length > 0
              ? `${pages.length} pages, ${databases.length} databases`
              : "Browse your Notion workspace"}
        </p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search pages and databases..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") searchItems(); }}
            className="w-full rounded-lg border border-slate-800 bg-slate-950 pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>
        <button
          onClick={searchItems}
          disabled={loading || !query.trim()}
          className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-30 text-sm text-white transition-colors"
        >
          Search
        </button>
        {searched && (
          <button onClick={fetchRecent} className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-slate-300 transition-colors border border-slate-700">
            Clear
          </button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center p-12 text-slate-500">Loading...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Globe className="h-12 w-12 mx-auto mb-4 text-slate-700" />
          <p className="text-lg font-medium text-slate-400 mb-1">{searched ? "No results found" : "No content yet"}</p>
          <p className="text-sm">{searched ? "Try a different search term." : "Make sure your Notion integration has access to pages."}</p>
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {items.map((item) => (
            <Card key={item.id} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group cursor-pointer" onClick={() => item.type === "page" && openPage(item.id)}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 min-w-0 flex-1">
                    <div className={`p-2 rounded-lg shrink-0 ${item.type === "database" ? "bg-blue-900/20" : "bg-emerald-900/20"}`}>
                      <FileText className={`h-4 w-4 ${item.type === "database" ? "text-blue-400" : "text-emerald-400"}`} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-200 truncate max-w-[300px]">{item.title || "Untitled"}</p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {item.type === "database" ? "Database" : "Page"} {item.last_edited && ` · ${formatDate(item.last_edited)}`}
                        {item.type === "page" && <span className="text-blue-500 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">Click to view</span>}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    {item.url && (
                      <a href={item.url} target="_blank" rel="noopener noreferrer"
                        className="p-2 text-slate-500 hover:text-white transition-colors" title="Open in Notion"
                        onClick={(e) => e.stopPropagation()}>
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selectedPage && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setSelectedPage(null)}>
          <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-3xl max-h-[85vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-5 border-b border-slate-800">
              <div className="min-w-0 flex-1">
                <h3 className="text-lg font-bold text-white truncate">{selectedPage.title}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{selectedPage.blocks?.length || 0} blocks</p>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-4">
                {selectedPage.url && (
                  <a href={selectedPage.url} target="_blank" rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors" title="Open in Notion">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
                <button onClick={() => setSelectedPage(null)} className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-5 space-y-2">
              {pageLoading ? (
                <div className="text-center py-8 text-slate-500">Loading content...</div>
              ) : selectedPage.blocks && selectedPage.blocks.length > 0 ? (
                selectedPage.blocks.map((block, i) => (
                  <div key={i} className="text-sm text-slate-300 leading-relaxed">
                    {block.type === "heading_1" ? (
                      <h1 className="text-xl font-bold text-white mt-4 mb-2">{block.text}</h1>
                    ) : block.type === "heading_2" ? (
                      <h2 className="text-lg font-semibold text-white mt-3 mb-1">{block.text}</h2>
                    ) : block.type === "heading_3" ? (
                      <h3 className="text-base font-medium text-white mt-2 mb-1">{block.text}</h3>
                    ) : block.type === "bulleted_list_item" || block.type === "numbered_list_item" ? (
                      <li className="ml-4 text-slate-300">{block.text}</li>
                    ) : block.type === "to_do" ? (
                      <div className="flex items-center gap-2 text-slate-300">
                        <span className="text-slate-600">[ ]</span> {block.text}
                      </div>
                    ) : block.type === "divider" ? (
                      <hr className="border-slate-800 my-3" />
                    ) : (
                      <p className="text-slate-300">{block.text}</p>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-500">No block content available.</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
