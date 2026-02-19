/**
 * Market Stats Component
 */

import { Competitor } from "@/types/api";

interface MarketStatsProps {
    competitors: Competitor[];
}

export function MarketStats({ competitors }: MarketStatsProps) {
    return (
        <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-zinc-900/30 backdrop-blur-sm p-6 rounded-2xl border border-zinc-800/50">
                <h3 className="text-sm font-medium text-zinc-500 mb-1">Market Share</h3>
                <div className="text-3xl font-bold text-white mb-4">
                    {(100 / (competitors.length + 1)).toFixed(1)}%
                    <span className="text-sm font-normal text-zinc-500 ml-2">est.</span>
                </div>
                <div className="h-2 bg-zinc-800 rounded-full overflow-hidden flex">
                    <div className="h-full bg-blue-500 w-[20%]" />
                    {competitors.map((c, i) => (
                        <div
                            key={i}
                            className="h-full opacity-50 border-l border-zinc-900"
                            style={{ backgroundColor: c.color || "#6b7280", width: `${80 / (competitors.length || 1)}%` }}
                        />
                    ))}
                </div>
            </div>
            <div className="bg-zinc-900/30 backdrop-blur-sm p-6 rounded-2xl border border-zinc-800/50">
                <h3 className="text-sm font-medium text-zinc-500 mb-1">Untapped Potential</h3>
                <div className="text-3xl font-bold text-emerald-400 mb-4">High</div>
                <p className="text-xs text-zinc-400">
                    3 major features missing in competitor products identified.
                </p>
            </div>
        </div>
    );
}
