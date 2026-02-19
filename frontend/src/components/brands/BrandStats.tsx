/**
 * Brand Stats Grid
 * 
 * Displays high-level metrics for the brand list page
 */

import { motion } from "framer-motion";
import { Users, TrendingUp, Zap, Clock } from "lucide-react";

interface BrandStatsProps {
    brandCount: number;
}

export function BrandStats({ brandCount }: BrandStatsProps) {
    return (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
                icon={<Users className="h-4 w-4" />}
                value={brandCount}
                label="Active Brands"
                color="blue"
            />
            <StatCard
                icon={<TrendingUp className="h-4 w-4" />}
                value="—"
                label="Mentions Today"
                color="emerald"
            />
            <StatCard
                icon={<Zap className="h-4 w-4" />}
                value="—"
                label="Hot Leads"
                color="amber"
            />
            <StatCard
                icon={<Clock className="h-4 w-4" />}
                value="Live"
                label="Monitoring"
                color="green"
                pulse
            />
        </div>
    );
}

function StatCard({
    icon,
    value,
    label,
    color,
    pulse
}: {
    icon: React.ReactNode;
    value: string | number;
    label: string;
    color: "blue" | "emerald" | "amber" | "green";
    pulse?: boolean;
}) {
    const colors = {
        blue: {
            bg: "bg-blue-500/10",
            border: "border-blue-500/20",
            text: "text-blue-500",
        },
        emerald: {
            bg: "bg-emerald-500/10",
            border: "border-emerald-500/20",
            text: "text-emerald-500",
        },
        amber: {
            bg: "bg-amber-500/10",
            border: "border-amber-500/20",
            text: "text-amber-500",
        },
        green: {
            bg: "bg-green-500/10",
            border: "border-green-500/20",
            text: "text-green-500",
        }
    };

    const c = colors[color];

    return (
        <motion.div
            whileHover={{ y: -4, scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300 }}
            className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-800 hover:border-blue-500/30 transition-colors"
        >
            <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-lg ${c.bg} ${c.border} border flex items-center justify-center`}>
                    <span className={c.text}>{icon}</span>
                </div>
                <div>
                    <div className="flex items-center gap-2">
                        <p className="text-xl font-semibold text-white">{value}</p>
                        {pulse && (
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-zinc-500">{label}</p>
                </div>
            </div>
        </motion.div>
    );
}
