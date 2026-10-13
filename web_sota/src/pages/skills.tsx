import { BookOpen } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

interface Skill {
  name: string;
  path: string;
}

export function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/skills`)
      .then((r) => r.json())
      .then((d) => setSkills(d.skills || []))
      .catch(() => setSkills([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6" data-testid="skills-page">
      <div>
        <h2
          data-testid="skills-title"
          className="text-2xl font-bold tracking-tight text-white"
        >
          Skills
        </h2>
        <p className="text-slate-300">
          Domain workflows served over MCP (`skill://`) and the Chat page
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center p-12 text-slate-300">
          Loading...
        </div>
      ) : skills.length === 0 ? (
        <div className="text-center py-16 text-slate-300">
          <BookOpen className="h-12 w-12 mx-auto mb-4 text-slate-700" />
          <p className="text-lg font-medium text-slate-200 mb-1">
            No skills registered
          </p>
          <p className="text-sm">
            Add a SKILL.md under notion_mcp/skills/ on the backend.
          </p>
        </div>
      ) : (
        <div
          data-testid="skills-grid"
          className="grid gap-3 md:grid-cols-2 lg:grid-cols-3"
        >
          {skills.map((s) => (
            <Card key={s.name} className="border-slate-800 bg-slate-950/50">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-900/20 rounded-md">
                    <BookOpen className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <CardTitle className="text-lg text-white">
                      {s.name}
                    </CardTitle>
                    <CardDescription className="text-sm text-slate-300 font-mono">
                      skill://{s.name}/SKILL.md
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-300">
                  Load automatically into chat prompts and MCP clients.
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
