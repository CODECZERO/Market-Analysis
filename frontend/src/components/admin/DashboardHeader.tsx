/**
 * Dashboard Header Component
 */

import { Shield, Clock, LogOut } from "lucide-react";
import type { DashboardOverview } from "@/hooks/admin/useAdminDashboard";
import type { User } from "@/contexts/AuthContext";

interface DashboardHeaderProps {
    user: User | null;
    lastUpdated: string | undefined;
    onLogout: () => void;
}

export function DashboardHeader({ user, lastUpdated, onLogout }: DashboardHeaderProps) {
    return (
        <header className="bg-zinc-900/80 border-b border-zinc-800 px-6 py-4 backdrop-blur-md sticky top-0 z-10">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-xl flex items-center justify-center border border-purple-500/30">
                        <Shield className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold flex items-center gap-2">
                            Admin Dashboard
                            <span className="px-2 py-0.5 text-[10px] rounded bg-purple-500/20 text-purple-400 border border-purple-500/30">
                                ADMIN
                            </span>
                        </h1>
                        <p className="text-zinc-500 text-sm flex items-center gap-2">
                            <Clock className="h-3 w-3" />
                            Last updated: {lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : "Loading..."}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-sm text-zinc-400">{user?.email}</span>
                    <button
                        onClick={onLogout}
                        className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm transition border border-zinc-700 flex items-center gap-2"
                    >
                        <LogOut className="h-4 w-4" />
                        Logout
                    </button>
                </div>
            </div>
        </header>
    );
}
