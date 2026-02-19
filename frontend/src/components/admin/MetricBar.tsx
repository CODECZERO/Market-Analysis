/**
 * Metric Bar Component
 * 
 * Animated horizontal bar for showing metrics with percentages
 */

import { motion } from "framer-motion";

type MetricColor = "purple" | "blue" | "emerald";

interface MetricBarProps {
    label: string;
    value: number;
    max: number;
    color?: MetricColor;
}

const COLORS: Record<MetricColor, string> = {
    purple: "bg-purple-500",
    blue: "bg-blue-500",
    emerald: "bg-emerald-500",
};

export function MetricBar({
    label,
    value,
    max,
    color = "purple",
}: MetricBarProps) {
    const percentage = max > 0 ? (value / max) * 100 : 0;

    return (
        <div className="flex items-center gap-4">
            <span className="text-zinc-400 text-sm w-36">{label}</span>
            <div className="flex-1 bg-zinc-800 rounded-full h-2">
                <motion.div
                    className={`${COLORS[color]} h-2 rounded-full`}
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                />
            </div>
            <span className="text-white font-semibold text-sm w-16 text-right">
                {value.toLocaleString()}
            </span>
        </div>
    );
}
