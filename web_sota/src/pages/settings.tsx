import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Save, RefreshCw, Cpu, Database } from "lucide-react";

export function Settings() {
    const [provider, setProvider] = useState("ollama");
    const [model, setModel] = useState("gemini-1.5-pro");
    const [endpoint, setEndpoint] = useState("http://localhost:11434");

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
                <p className="text-slate-400">Configure Notion Workspace and AI reasoning preferences</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Cpu className="h-5 w-5 text-blue-500" />
                            <CardTitle className="text-white">Local LLM Configuration</CardTitle>
                        </div>
                        <CardDescription className="text-slate-400">Select your preferred AI provider for workspace operations</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Provider</Label>
                            <Select value={provider} onValueChange={setProvider}>
                                <SelectTrigger className="bg-slate-900 border-slate-800 text-slate-100">
                                    <SelectValue placeholder="Select provider" />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-900 border-slate-800 text-slate-100">
                                    <SelectItem value="ollama">Ollama (Default)</SelectItem>
                                    <SelectItem value="lmstudio">LM Studio</SelectItem>
                                    <SelectItem value="openai">OpenAI Compatible</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">API Endpoint</Label>
                            <Input
                                value={endpoint}
                                onChange={(e) => setEndpoint(e.target.value)}
                                className="bg-slate-900 border-slate-800 text-slate-100"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Model Name</Label>
                            <Input
                                value={model}
                                onChange={(e) => setModel(e.target.value)}
                                className="bg-slate-900 border-slate-800 text-slate-100"
                            />
                        </div>
                        <div className="flex gap-2 pt-2">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                                <Save className="mr-2 h-4 w-4" /> Save Preferences
                            </Button>
                            <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
                                <RefreshCw className="mr-2 h-4 w-4" /> Refresh Models
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">App Information</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-1">
                        <p>Notion Hub v0.1.0 (SOTA)</p>
                        <p>Dual Transport: STDIO + HTTP (10811)</p>
                        <p>Frontend Port: 10810</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
