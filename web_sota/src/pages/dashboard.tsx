import { AuthSetup } from "@/components/auth/auth-setup";
import { Card, CardContent } from "@/components/ui/card";
import { BookOpen, ChevronRight, Cpu, ExternalLink, FileText, Globe, MessageSquare, Search, Wrench } from "lucide-react";
import { API_BASE } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface RecentItem {
  id: string;
  title: string;
  type: string;
  url: string;
  last_edited: string;
}

export function Dashboard() {
  const [items, setItems] = useState<RecentItem[]>([]);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [toolCount, setToolCount] = useState(0);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, toolsRes] = await Promise.all([
        fetch(API_BASE + "/api/status"),
        fetch(API_BASE + "/api/tools"),
      ]);
      const statusData = await statusRes.json();
      const toolsData = await toolsRes.json();
      setAuthenticated(statusData.authenticated);
      setToolCount(toolsData.tools?.length || 0);

      if (statusData.authenticated) {
        const recentRes = await fetch(API_BASE + "/api/recent?limit=30");
        if (recentRes.ok) {
          const recentData = await recentRes.json();
          setItems(recentData.items || []);
        }
      }
    } catch {
      console.warn("Dashboard fetch failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (authenticated === false) {
    return <AuthSetup />;
  }

  const pages = items.filter((i) => i.type === "page");

  return (
    <div className="space-y-8" data-testid="dashboard">
      <div className="bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 border border-slate-800 rounded-xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center">
            <BookOpen className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">notion-mcp</h1>
            <p className="text-sm text-slate-400">MCP server for Notion workspace management</p>
          </div>
        </div>
        <p className="text-slate-400 max-w-2xl mb-6 leading-relaxed">
          Browse, search, and manage your Notion pages and databases through a local MCP server.
          {toolCount > 0 && ` ${toolCount} tools available — pages, databases, comments, RAG search, automations, and more.`}
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to="/explorer" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm text-white transition-colors">
            <Search className="h-4 w-4" /> Browse Content <ChevronRight className="h-3.5 w-3.5" />
          </Link>
          <Link to="/chat" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors border border-slate-700">
            <MessageSquare className="h-4 w-4" /> AI Chat
          </Link>
          <Link to="/tools" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors border border-slate-700">
            <Wrench className="h-4 w-4" /> {toolCount} Tools
          </Link>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Globe className="h-12 w-12 mx-auto mb-4 text-slate-700" />
          <p className="text-lg font-medium text-slate-400 mb-1">No content yet</p>
          <p className="text-sm">Make sure your integration has access to pages in your workspace, then check the Explorer.</p>
          <Link to="/explorer" className="inline-flex items-center gap-1.5 mt-4 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors border border-slate-700">
            <Search className="h-4 w-4" /> Browse Content
          </Link>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Recent Content</h2>
            <p className="text-xs text-slate-500">{items.length} items</p>
          </div>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {items.slice(0, 18).map((item) => (
              <Card key={item.id} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className={`p-2 rounded-lg shrink-0 ${item.type === "database" ? "bg-blue-900/20" : "bg-emerald-900/20"}`}>
                        <FileText className={`h-4 w-4 ${item.type === "database" ? "text-blue-400" : "text-emerald-400"}`} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-200 truncate max-w-[180px]">{item.title}</p>
                        <p className="text-xs text-slate-500 mt-0.5">{item.type === "database" ? "Database" : "Page"}</p>
                      </div>
                    </div>
                    {item.url && (
                      <a href={item.url} target="_blank" rel="noopener noreferrer"
                        className="p-1.5 text-slate-500 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
