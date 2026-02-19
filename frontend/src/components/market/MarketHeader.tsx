/**
 * Market Header Component
 */

import { motion } from "framer-motion";
import { Target, Users, Sparkles, Loader2 } from "lucide-react";

interface MarketHeaderProps {
    onManageCompetitors: () => void;
    onAnalyze: () => void;
    isAnalyzing: boolean;
}

export function MarketHeader({ onManageCompetitors, onAnalyze, isAnalyzing }: MarketHeaderProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border border-blue-500/10 p-8"
        >
            <div className="relative z-10 flex flex-wrap items-center justify-between gap-6">
                <div className="flex items-center gap-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <Target className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Market Gap</h1>
                        <p className="text-zinc-400 mt-2 max-w-xl">
                            Analyze competitor weaknesses to find your winning strategy.
                        </p>
                    </div>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={onManageCompetitors}
                        className="flex items-center gap-2 px-6 py-3 bg-zinc-800 hover:bg-zinc-700 rounded-xl font-medium text-white transition-all shadow-lg"
                    >
                        <Users className="w-5 h-5" />
                        <span>Manage Competitors</span>
                    </button>
                    <button
                        onClick={onAnalyze}
                        disabled={isAnalyzing}
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-medium text-white transition-all shadow-lg shadow-blue-500/20"
                    >
                        {isAnalyzing ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Analyzing...</span>
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5" />
                                <span>Analyze Market</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
            {/* Background glow */}
            <div className="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl opacity-30" />
        </motion.div>
    );
}
