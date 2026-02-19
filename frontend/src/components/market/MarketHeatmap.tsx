/**
 * Market Heatmap Component
 * 
 * Displays sentiment heatmap for competitors
 */

import { motion } from "framer-motion";
import type { Competitor } from "@/types/api";

interface MarketHeatmapProps {
    competitors: Competitor[];
}

export function MarketHeatmap({ competitors }: MarketHeatmapProps) {
    const getSentimentColor = (score: number) => {
        if (score > 70) return "#22c55e";
        if (score > 40) return "#f59e0b";
        return "#ef4444";
    };

    const getSentimentLabel = (score: number) => {
        if (score > 70) return "Positive";
        if (score > 40) return "Mixed";
        return "Negative";
    };

    const getSentimentTextColor = (score: number) => {
        if (score > 70) return "text-green-400";
        if (score > 40) return "text-amber-400";
        return "text-red-400";
    };

    return (
        <div className="space-y-6">
            {competitors.map((comp, i) => {
                const score = comp.sentimentScore ?? 50;
                return (
                    <div key={comp.id}>
                        <div className="flex justify-between text-sm mb-2">
                            <span className="font-medium text-zinc-300">{comp.name}</span>
                            <span className={getSentimentTextColor(score)}>
                                {getSentimentLabel(score)}
                            </span>
                        </div>
                        <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${score}%` }}
                                transition={{ duration: 1, delay: i * 0.2 }}
                                className="h-full rounded-full"
                                style={{ backgroundColor: getSentimentColor(score) }}
                            />
                        </div>
                    </div>
                );
            })}

            <div className="pt-4 border-t border-zinc-800/50">
                <div className="flex justify-between text-xs text-zinc-500">
                    <span>Negative</span>
                    <span>Neutral</span>
                    <span>Positive</span>
                </div>
                <div className="mt-2 h-1 bg-gradient-to-r from-red-500 via-amber-500 to-green-500 rounded-full opacity-30" />
            </div>
        </div>
    );
}
