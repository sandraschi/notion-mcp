import { AuthSetup } from "@/components/auth/auth-setup";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, FileText, Globe } from "lucide-react";
import { API_BASE } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";

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
  const [dbCount, setDbCount] = useState(0);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const statusRes = await fetch(API_BASE + "/api/status");
      const statusData = await statusRes.json();
      const authed = statusData.authenticated;
      setAuthenticated(authed);

      if (authed) {
        const recentRes = await fetch(API_BASE + "/api/recent?limit=30");
        if (recentRes.ok) {
          const recentData = await recentRes.json();
          setItems(recentData.items || []);
          setDbCount(recentData.items.filter((i: any) => i.type === "database").length);
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
  const databases = items.filter((i) => i.type === "database");

  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Notion Dashboard
          </h2>
          <p className="text-slate-400">
            {items.length > 0 ? `${pages.length} pages, ${databases.length} databases` : "Recent workspace content"}
          </p>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Globe className="h-12 w-12 mx-auto mb-4 text-slate-700" />
          <p className="text-lg font-medium text-slate-400 mb-1">No content found</p>
          <p className="text-sm">Make sure your integration has access to pages in your workspace.</p>
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <Card key={item.id} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className={`p-2 rounded-lg shrink-0 ${item.type === "database" ? "bg-blue-900/20" : "bg-emerald-900/20"}`}>
                      <FileText className={`h-4 w-4 ${item.type === "database" ? "text-blue-400" : "text-emerald-400"}`} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate max-w-[200px]">{item.title}</p>
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
      )}
    </div>
  );
}
