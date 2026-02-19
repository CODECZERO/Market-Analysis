/**
 * Market Gap Competitor Card
 * 
 * Displays competitor analysis with strengths and weaknesses
 */

import { motion } from "framer-motion";
import { TrendingUp, ArrowDownRight, ArrowUpRight } from "lucide-react";
import type { Competitor } from "@/types/api";

interface CompetitorCardProps {
    competitor: Competitor;
    index: number;
}

export function MarketCompetitorCard({ competitor, index }: CompetitorCardProps) {
    const score = competitor.sentimentScore ?? 50;
    const weaknesses = competitor.weaknesses ?? [];
    const strengths = competitor.strengths ?? [];

    const sentimentColor = score > 70
        ? "text-green-400"
        : score > 40
            ? "text-amber-400"
            : "text-red-400";

    const sentimentBg = score > 70
        ? "from-green-500/10 to-emerald-500/5"
        : score > 40
            ? "from-amber-500/10 to-yellow-500/5"
            : "from-red-500/10 to-rose-500/5";

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group relative bg-gradient-to-br from-zinc-900/50 to-zinc-900/30 backdrop-blur-lg rounded-2xl p-6 border border-zinc-800/50 hover:border-blue-500/40 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 overflow-hidden"
        >
            <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${sentimentBg} rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -mr-16 -mt-16`} />

            <div className="relative z-10">
                <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                        <div
                            className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg ring-2 ring-zinc-800/50 group-hover:ring-blue-500/30 transition-all duration-300"
                            style={{ backgroundColor: competitor.color }}
                        >
                            {competitor.name[0]}
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
                                {competitor.name}
                            </h3>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="text-xs text-zinc-400 bg-zinc-800/80 px-3 py-1 rounded-full border border-zinc-700/50 flex items-center gap-1.5">
                                    <TrendingUp className="w-3 h-3" />
                                    {competitor.shareOfVoice}% Share
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col items-end">
                        <div className={`text-3xl font-bold ${sentimentColor} flex items-center gap-1`}>
                            {score}%
                        </div>
                        <span className="text-xs text-zinc-500 uppercase tracking-wide mt-1">Sentiment</span>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-red-500/5 rounded-xl p-4 border border-red-500/10">
                        <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <ArrowDownRight className="w-4 h-4" /> Weaknesses
                        </h4>
                        <ul className="space-y-2.5">
                            {weaknesses.map((w, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                                    <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                                    <span className="leading-relaxed">{w}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="bg-green-500/5 rounded-xl p-4 border border-green-500/10">
                        <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <ArrowUpRight className="w-4 h-4" /> Strengths
                        </h4>
                        <ul className="space-y-2.5">
                            {strengths.map((s, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-1.5 flex-shrink-0" />
                                    <span className="leading-relaxed">{s}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
