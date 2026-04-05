import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/common/utils';
import {
    LayoutDashboard,
    MessageSquare,
    Search,
    Settings,
    ChevronLeft,
    ChevronRight,
    Globe,
    Puzzle,
    Database
} from 'lucide-react';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
    const location = useLocation();

    const navItems = [
        { name: "Dashboard", icon: LayoutDashboard, path: "/" },
        { name: "Notion Explorer", icon: Globe, path: "/explorer" },
        { name: "Semantic Search", icon: Search, path: "/search" },
        { name: "AI Producer Chat", icon: MessageSquare, path: "/chat" },
        { name: "Plugin Registry", icon: Puzzle, path: "/plugins" },
        { name: "Data & Migration", icon: Database, path: "/data" },
        { name: "Tools & Status", icon: Settings, path: "/status" },
    ];

    return (
        <aside className={cn(
            "flex flex-col border-r border-slate-800 bg-slate-950 transition-all duration-300",
            collapsed ? "w-16" : "w-64"
        )}>
            <div className="flex h-16 items-center justify-between px-4">
                {!collapsed && (
                    <div className="flex items-center gap-2 font-bold text-white">
                        <div className="h-6 w-6 rounded bg-blue-600"></div>
                        <span>NotionMCP</span>
                    </div>
                )}
                <button onClick={onToggle} className="rounded-md p-1.5 text-slate-400 hover:bg-slate-900 hover:text-white">
                    {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                </button>
            </div>

            <nav className="flex-1 space-y-1 p-2">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={cn(
                                "group relative flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-slate-800 hover:text-white",
                                isActive ? "bg-slate-800 text-white" : "text-slate-400",
                                collapsed ? "justify-center" : "justify-start"
                            )}
                        >
                            <item.icon className={cn("h-5 w-5", !collapsed && "mr-3", isActive && "text-blue-400")} />
                            {!collapsed && <span>{item.name}</span>}

                            {collapsed && (
                                <div className="absolute left-full ml-2 hidden rounded bg-slate-800 px-2 py-1 text-xs text-white group-hover:block z-50 whitespace-nowrap border border-slate-700">
                                    {item.name}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}
