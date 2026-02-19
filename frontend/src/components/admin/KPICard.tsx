/**
 * KPI Card Component
 * 
 * Displays key performance indicator with gradient background
 */

import type { ReactNode } from "react";

type KPIColor = "purple" | "emerald" | "blue" | "amber";

interface KPICardProps {
    icon: ReactNode;
    title: string;
    value: number;
    growth?: string;
    color?: KPIColor;
}

const GRADIENTS: Record<KPIColor, string> = {
    purple: "from-zinc-900 via-zinc-900 to-purple-950/20",
    emerald: "from-zinc-900 via-zinc-900 to-emerald-950/20",
    blue: "from-zinc-900 via-zinc-900 to-blue-950/20",
    amber: "from-zinc-900 via-zinc-900 to-amber-950/20",
};

const ICON_BGS: Record<KPIColor, string> = {
    purple: "bg-purple-500/10 border-purple-500/20",
    emerald: "bg-emerald-500/10 border-emerald-500/20",
    blue: "bg-blue-500/10 border-blue-500/20",
    amber: "bg-amber-500/10 border-amber-500/20",
};

export function KPICard({
    icon,
    title,
    value,
    growth,
    color = "purple",
}: KPICardProps) {
    return (
        <div className={`bg-gradient-to-br ${GRADIENTS[color]} p-6 rounded-xl border border-zinc-800`}>
            <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl border ${ICON_BGS[color]}`}>
                    {icon}
                </div>
                {growth && (
                    <span className="text-emerald-400 text-xs font-medium bg-emerald-500/10 px-2 py-1 rounded">
                        {growth}
                    </span>
                )}
            </div>
            <p className="text-3xl font-bold text-white">{value.toLocaleString()}</p>
            <p className="text-zinc-500 text-sm mt-1">{title}</p>
        </div>
    );
}
