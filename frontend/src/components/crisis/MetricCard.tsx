/**
 * Metric Card Component
 * 
 * Reusable metric display card with icon and color variants
 */

import { motion } from "framer-motion";

interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    value: string;
    description: string;
    color: "blue" | "amber" | "emerald" | "red";
}

export function MetricCard({ icon, label, value, description, color }: MetricCardProps) {
    const colors = {
        blue: "bg-blue-500/10 border-blue-500/20 text-blue-500 group-hover:border-blue-500/40",
        amber: "bg-amber-500/10 border-amber-500/20 text-amber-500 group-hover:border-amber-500/40",
        emerald: "bg-emerald-500/10 border-emerald-500/20 text-emerald-500 group-hover:border-emerald-500/40",
        red: "bg-red-500/10 border-red-500/20 text-red-500 group-hover:border-red-500/40",
    };

    return (
        <motion.div
            whileHover={{ y: -1 }}
            className="group p-3 rounded-xl bg-zinc-900/40 border border-zinc-800/50 transition-all hover:bg-zinc-900/60"
        >
            <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-lg border flex items-center justify-center transition-colors shrink-0 ${colors[color]}`}>
                    {icon}
                </div>
                <div className="min-w-0">
                    <p className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider truncate">{label}</p>
                    <p className="text-lg font-bold text-white leading-tight">{value}</p>
                    <p className="text-[10px] text-zinc-500 truncate">{description}</p>
                </div>
            </div>
        </motion.div>
    );
}
