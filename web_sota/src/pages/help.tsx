import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HelpCircle, Book, Shield, Zap, Info } from "lucide-react";

export function Help() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Help & Documentation</h2>
                <p className="text-slate-400">Reference guide for Notion Workspace MCP</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Book className="h-5 w-5 text-blue-500" />
                            <CardTitle className="text-white">Quick Start</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>1. Open the AI Command interface to manage your pages via natural language.</p>
                        <p>2. Use the Notion Tools page for direct execution of API operations.</p>
                        <p>3. Go to Settings to configure your Notion Integration Token and Model preferences.</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Shield className="h-5 w-5 text-purple-500" />
                            <CardTitle className="text-white">Notion API Keys</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Ensure you have a valid Notion Integration Token in your environment variables.</p>
                        <p>Access requires basic authentication for the web bridge.</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Zap className="h-5 w-5 text-yellow-500" />
                            <CardTitle className="text-white">MCP Standard</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Port: 10810 (Frontend) / 10811 (Backend Bridge)</p>
                        <p>Transport: Dual (STDIO + HTTP Streamable)</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Info className="h-5 w-5 text-emerald-500" />
                            <CardTitle className="text-white">About SOTA</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400">
                        <p>Part of the Sandra SOTA Fleet (January 2026). Standardized UI for unified productivity and knowledge management.</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
