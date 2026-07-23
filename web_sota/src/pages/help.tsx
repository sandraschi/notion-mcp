import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

const TABS = [
  { id: "about-notion", label: "About Notion" },
  { id: "note-apps-comparison", label: "Note Apps Comparison" },
  { id: "API", label: "API Reference" },
  { id: "Configuration", label: "Configuration" },
  { id: "Troubleshooting", label: "Troubleshooting" },
];

export function Help() {
  const [activeTab, setActiveTab] = useState(TABS[0].id);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchDoc = useCallback(async (name: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/docs/${name}`);
      const data = await res.json();
      setContent(data.content || "# Not found");
    } catch {
      setContent("Failed to load document.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchDoc(activeTab); }, [activeTab, fetchDoc]);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Help & Documentation</h2>
        <p className="text-slate-400">Guides, reference, and comparisons</p>
      </div>

      <div className="flex gap-1 border-b border-slate-800 overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-blue-500 text-white"
                : "border-transparent text-slate-500 hover:text-slate-300 hover:border-slate-600"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="min-h-[60vh]">
        {loading ? (
          <div className="flex justify-center py-12 text-slate-500">Loading...</div>
        ) : (
          <div className="prose prose-invert max-w-none text-sm text-slate-300 space-y-3">
            {content.split("\n").map((line, i) => {
              if (line.startsWith("# ")) return <h1 key={i} className="text-2xl font-bold text-white mt-6 mb-3">{line.replace("# ", "")}</h1>;
              if (line.startsWith("## ")) return <h2 key={i} className="text-xl font-semibold text-white mt-5 mb-2">{line.replace("## ", "")}</h2>;
              if (line.startsWith("### ")) return <h3 key={i} className="text-lg font-medium text-white mt-4 mb-1">{line.replace("### ", "")}</h3>;
              if (line.startsWith("- **")) {
                const match = line.match(/- \*\*(.+?)\*\*:?\s*(.*)/);
                if (match) return <p key={i} className="text-slate-300 ml-4"><strong className="text-slate-200">{match[1]}</strong>{match[2] ? `: ${match[2]}` : ""}</p>;
              }
              if (line.startsWith("- ")) return <li key={i} className="text-slate-300 ml-4">{line.replace("- ", "")}</li>;
              if (line.startsWith("|")) return null;
              if (line.startsWith("```")) return null;
              if (line.trim() === "---") return <hr key={i} className="border-slate-800 my-6" />;
              if (line.trim() === "") return <div key={i} className="h-2" />;
              return <p key={i} className="text-slate-300 leading-relaxed">{line}</p>;
            })}
          </div>
        )}
      </div>
    </div>
  );
}
