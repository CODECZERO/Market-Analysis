/**
 * Signup Sources Chart Component
 * 
 * Displays signup source breakdown with progress bars
 */

import { TrendingUp } from "lucide-react";

interface SignupSource {
    source: string;
    count: number;
    percentage: number;
}

interface SignupSourcesChartProps {
    sources: SignupSource[];
}

export function SignupSourcesChart({ sources }: SignupSourcesChartProps) {
    return (
        <div className="bg-gradient-to-br from-zinc-900 via-zinc-900 to-blue-950/10 rounded-xl p-6 border border-zinc-800">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-400" />
                Signup Sources (30d)
            </h2>
            <div className="space-y-3">
                {sources.length > 0 ? (
                    sources.map((source) => (
                        <div key={source.source} className="flex items-center justify-between">
                            <span className="text-zinc-400 capitalize text-sm">{source.source}</span>
                            <div className="flex items-center gap-3">
                                <div className="w-24 bg-zinc-800 rounded-full h-1.5">
                                    <div
                                        className="bg-blue-500 h-1.5 rounded-full transition-all"
                                        style={{ width: `${source.percentage}%` }}
                                    />
                                </div>
                                <span className="text-zinc-500 text-xs w-16 text-right">
                                    {source.count} ({source.percentage}%)
                                </span>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="text-zinc-600 text-sm">No signup data available</p>
                )}
            </div>
        </div>
    );
}
