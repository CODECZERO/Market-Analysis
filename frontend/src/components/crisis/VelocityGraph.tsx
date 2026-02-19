/**
 * Velocity Graph Component
 * 
 * Real-time mention velocity bar chart
 */

import { motion } from "framer-motion";
import { Zap, Clock } from "lucide-react";
import type { VelocityPoint } from "./CrisisTypes";

interface VelocityGraphProps {
    data: VelocityPoint[];
}

export function VelocityGraph({ data }: VelocityGraphProps) {
    const maxMentions = Math.max(...data.map((d) => d.mentionsPerMinute), 1);
    const hasData = data.some(d => d.mentionsPerMinute > 0);

    // Show empty state when no activity
    if (!hasData) {
        return (
            <div className="rounded-xl bg-zinc-900/30 backdrop-blur-sm border border-zinc-800/50 p-4">
                <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                            <Zap className="w-3.5 h-3.5 text-blue-500" />
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-white">Mention Velocity</h3>
                            <p className="text-[10px] text-zinc-500">Real-time mention volume per minute</p>
                        </div>
                    </div>
                </div>
                <div className="h-32 flex items-center justify-center">
                    <div className="text-center">
                        <div className="w-10 h-10 rounded-lg bg-zinc-800/50 flex items-center justify-center mx-auto mb-2">
                            <Zap className="w-5 h-5 text-zinc-600" />
                        </div>
                        <p className="text-sm text-zinc-400">No activity detected</p>
                        <p className="text-xs text-zinc-600 mt-0.5">Velocity data will appear when mentions are processed</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="rounded-xl bg-zinc-900/30 backdrop-blur-sm border border-zinc-800/50 p-4">
            <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                        <Zap className="w-3.5 h-3.5 text-blue-500" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-white">Mention Velocity</h3>
                        <p className="text-[10px] text-zinc-500">Real-time mention volume per minute</p>
                    </div>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 bg-zinc-900/50 px-2.5 py-1 rounded-full border border-zinc-800">
                    <Clock className="w-3 h-3" />
                    <span>Last 30 Minutes</span>
                </div>
            </div>

            <div className="h-32 flex items-end gap-1 px-2">
                {data.map((point, i) => {
                    const height = Math.max(8, (point.mentionsPerMinute / maxMentions) * 100);
                    const isNegative = point.sentiment < -0.3;
                    const isPositive = point.sentiment > 0.3;

                    return (
                        <motion.div
                            key={i}
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: `${height}%`, opacity: 1 }}
                            transition={{ delay: i * 0.01 }}
                            className="relative flex-1 group"
                        >
                            <div
                                className={`w-full h-full rounded-t-sm transition-all duration-300 opacity-60 group-hover:opacity-100 ${isNegative ? "bg-red-500" : isPositive ? "bg-green-500" : "bg-blue-500"
                                    }`}
                            />

                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-20 min-w-max">
                                <div className="bg-zinc-900 text-white text-xs rounded py-1 px-2 border border-zinc-700 shadow-xl">
                                    {point.mentionsPerMinute.toFixed(1)}/min
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            <div className="flex justify-between text-xs text-zinc-600 mt-3 border-t border-zinc-800/50 pt-2 font-mono">
                <span>30m ago</span>
                <span>15m ago</span>
                <span>Just now</span>
            </div>
        </div>
    );
}
