/**
 * Opportunity Engine Component
 */

import { motion } from "framer-motion";
import { Sparkles, Zap, Target } from "lucide-react";
import { TypewriterText } from "@/components/shared/TypewriterText";

interface OpportunityEngineProps {
    analysis: string | null;
    loading: boolean;
}

export function OpportunityEngine({ analysis, loading }: OpportunityEngineProps) {
    if (loading) {
        return (
            <div className="bg-zinc-900/30 backdrop-blur-sm rounded-xl p-8 border border-zinc-800/50 flex flex-col items-center justify-center text-center space-y-4">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
                    <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-blue-400 animate-pulse" />
                </div>
                <h3 className="text-lg font-medium text-white">Analyzing Market Data...</h3>
                <p className="text-sm text-zinc-500 max-w-sm">Our AI is scanning thousands of data points to identify gaps in your competitors' offerings.</p>
            </div>
        );
    }

    if (!analysis) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-zinc-900/30 backdrop-blur-sm rounded-xl border border-zinc-800/50 overflow-hidden"
        >
            <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-b border-blue-500/10 p-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    Strategic Opportunities
                </h2>
            </div>
            <div className="p-8">
                <div className="prose prose-invert max-w-none prose-p:text-zinc-300 prose-headings:text-white prose-strong:text-blue-200">
                    <TypewriterText text={analysis} />
                </div>

                <div className="mt-8 flex justify-end">
                    <button className="text-sm text-zinc-500 hover:text-white flex items-center gap-2 transition-colors">
                        <Target className="w-4 h-4" />
                        Export Strategy Report
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
