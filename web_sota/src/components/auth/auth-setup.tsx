import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, ShieldCheck, Share2, Info } from "lucide-react";

export function AuthSetup() {
    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <div className="text-center space-y-2">
                <div className="inline-flex p-3 bg-blue-500/10 rounded-full mb-4">
                    <ShieldCheck className="h-8 w-8 text-blue-500" />
                </div>
                <h2 className="text-3xl font-bold tracking-tight text-white">Notion Integration Required</h2>
                <p className="text-slate-400">NotionMCP requires a SOTA Integration Token to communicate with your workspace.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-blue-400 font-bold mb-2">1</div>
                        <CardTitle className="text-base text-white">Create Integration</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Visit the Notion Developers portal to create a new internal integration.</p>
                        <a
                            href="https://www.notion.so/my-integrations"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
                        >
                            Open Integrations <ExternalLink className="h-3 w-3" />
                        </a>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-emerald-400 font-bold mb-2">2</div>
                        <CardTitle className="text-base text-white">Configure Token</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Copy your "Internal Integration Secret" and add it to your environment.</p>
                        <div className="p-2 bg-slate-900 rounded border border-slate-800 font-mono text-[10px] text-slate-300">
                            NOTION_TOKEN=secret_...
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-purple-400 font-bold mb-2">3</div>
                        <CardTitle className="text-base text-white">Share Pages</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Go to Notion, open the pages you want to use, and "Add Connection" to your integration.</p>
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                            <Share2 className="h-3 w-3" /> Top Right {"->"} ... {"->"} Connect to
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-blue-500/20 bg-blue-500/5">
                <CardContent className="pt-6">
                    <div className="flex gap-4">
                        <Info className="h-5 w-5 text-blue-400 shrink-0" />
                        <div className="space-y-1">
                            <p className="text-sm font-medium text-blue-200">Server Running Check</p>
                            <p className="text-xs text-blue-400/70">
                                This dashboard requires the Notion MCP Python server to be running on port 10811.
                                If you see this message even after setting the token, ensure `uv run server.py` is active.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
