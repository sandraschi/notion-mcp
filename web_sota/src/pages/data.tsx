import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Upload, Download, FileJson, FileText, CheckCircle2, Clock, Trash2, ArrowRight } from "lucide-react";

interface ExportItem {
    id: string;
    timestamp: string;
    format: string;
    size: string;
    status: string;
}

export function DataMigration() {
    const [exports, setExports] = useState<ExportItem[]>([]);
    const [exporting, setExporting] = useState(false);

    const handleExport = async (format: string) => {
        setExporting(true);
        try {
            const res = await fetch(`/api/export?format=${format}`);
            const data = await res.json();
            if (data.success) {
                // Refresh list or add new one
                setExports([
                    {
                        id: data.export_config.id,
                        timestamp: data.export_config.started_time,
                        format: format.toUpperCase(),
                        size: "24 KB",
                        status: "ready"
                    },
                    ...exports
                ]);
            }
        } catch (error) {
            console.error("Export failed", error);
        } finally {
            setExporting(false);
        }
    };

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Data & Migrations</h2>
                <p className="text-slate-400">Import/Export workspace data with high durability</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Import Box */}
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Upload className="h-5 w-5 text-emerald-500" /> Import Data
                        </CardTitle>
                        <CardDescription>Upload Markdown or JSON to ingest into Notion</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="border-2 border-dashed border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center text-center space-y-4 hover:border-emerald-500/50 transition-colors cursor-pointer group">
                            <div className="p-3 bg-slate-900 rounded-full group-hover:bg-emerald-500/10 group-hover:scale-110 transition-all">
                                <FileText className="h-6 w-6 text-slate-500 group-hover:text-emerald-500" />
                            </div>
                            <div className="space-y-1">
                                <p className="text-sm font-medium text-slate-200">Drop files here or click to browse</p>
                                <p className="text-xs text-slate-500">Supports .md, .json archives</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Export Options */}
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Download className="h-5 w-5 text-blue-500" /> Export Workspace
                        </CardTitle>
                        <CardDescription>Generate portable backups of your knowledge</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <button
                            disabled={exporting}
                            onClick={() => handleExport('json')}
                            className="w-full flex items-center justify-between p-3 bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <FileJson className="h-5 w-5 text-blue-400" />
                                <div className="text-left">
                                    <p className="text-sm font-medium text-slate-200">Full JSON Backup</p>
                                    <p className="text-xs text-slate-500">Raw structure and metadata</p>
                                </div>
                            </div>
                            <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-white transition-all transform group-hover:translate-x-1" />
                        </button>
                        <button
                            disabled={exporting}
                            onClick={() => handleExport('md')}
                            className="w-full flex items-center justify-between p-3 bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <FileText className="h-5 w-5 text-emerald-400" />
                                <div className="text-left">
                                    <p className="text-sm font-medium text-slate-200">Markdown Archive</p>
                                    <p className="text-xs text-slate-500">Readable content snapshots</p>
                                </div>
                            </div>
                            <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-white transition-all transform group-hover:translate-x-1" />
                        </button>
                    </CardContent>
                </Card>
            </div>

            {/* Previous Exports */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                    <Clock className="h-4 w-4" /> Previous Exports
                </h3>
                <div className="rounded-xl border border-slate-800 bg-slate-950/50 overflow-hidden">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-900/50 text-slate-400 font-medium">
                            <tr>
                                <th className="px-4 py-3">ID / Reference</th>
                                <th className="px-4 py-3">Format</th>
                                <th className="px-4 py-3">Size</th>
                                <th className="px-4 py-3">Status</th>
                                <th className="px-4 py-3 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {exports.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-4 py-8 text-center text-slate-500 italic">No backup history found.</td>
                                </tr>
                            ) : exports.map((exp) => (
                                <tr key={exp.id} className="hover:bg-slate-800/30 transition-colors text-slate-300">
                                    <td className="px-4 py-3 font-mono text-xs">{exp.id}</td>
                                    <td className="px-4 py-3 uppercase text-[10px] font-bold"><span className="px-1.5 py-0.5 bg-slate-800 rounded">{exp.format}</span></td>
                                    <td className="px-4 py-3">{exp.size}</td>
                                    <td className="px-4 py-3">
                                        <span className="flex items-center gap-1 text-emerald-500">
                                            <CheckCircle2 className="h-3 w-3" /> Ready
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-right space-x-2">
                                        <button title="Download Backup" className="text-slate-500 hover:text-white"><Download className="h-4 w-4" /></button>
                                        <button title="Delete Export" className="text-slate-500 hover:text-red-400"><Trash2 className="h-4 w-4" /></button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
