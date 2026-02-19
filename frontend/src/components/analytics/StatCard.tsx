/**
 * Stat Card Component
 */

import { motion } from "framer-motion";

interface StatCardProps {
    icon: React.ReactNode;
    value: string | number;
    label: string;
    color: "blue" | "emerald" | "amber" | "purple";
}

export function StatCard({
    icon,
    value,
    label,
    color
}: StatCardProps) {
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
        purple: {
            bg: "bg-purple-500/10",
            border: "border-purple-500/20",
            text: "text-purple-500",
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
                    <p className="text-xl font-semibold text-white">{value}</p>
                    <p className="text-xs text-zinc-500">{label}</p>
                </div>
            </div>
        </motion.div>
    );
}
