/**
 * Market Gap Page
 * 
 * Analyze competitor weaknesses and identify strategic opportunities.
 * Refactored to use extracted SRP-compliant components.
 */

import { motion, AnimatePresence } from "framer-motion";
import { Users, TrendingUp, AlertTriangle, Plus } from "lucide-react";

import { useMarketGap } from "@/hooks/market";
import {
    MarketHeader,
    MarketStats,
    OpportunityEngine,
    MarketHeatmap,
    MarketCompetitorCard,
} from "@/components/market";
import { CompetitorManagementModal } from "@/components/competitors/CompetitorManagementModal";

export default function MarketGapPage() {
    const {
        competitors,
        analysis,
        analyzing,
        error,
        showManageModal,
        setShowManageModal,
        brandId,
        loadCompetitors,
        analyzeMarket,
    } = useMarketGap();

    return (
        <div className="min-h-screen bg-[#0a0a0b] text-white p-6 pb-24">
            <div className="max-w-7xl mx-auto space-y-6">
                <MarketHeader
                    onManageCompetitors={() => setShowManageModal(true)}
                    onAnalyze={analyzeMarket}
                    isAnalyzing={analyzing}
                />

                {error && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 flex items-center gap-2"
                    >
                        <AlertTriangle className="w-5 h-5" />
                        {error}
                    </motion.div>
                )}

                {/* Main Content Grid */}
                <div className="grid lg:grid-cols-12 gap-6">
                    {/* Left Column: Competitors & Opportunities */}
                    <div className="lg:col-span-8 space-y-6">
                        <MarketStats competitors={competitors} />

                        {/* Competitor Analysis Cards */}
                        <div>
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                    <Users className="w-5 h-5 text-blue-500" />
                                    Competitor Analysis
                                </h2>
                            </div>
                            <div>
                                <AnimatePresence>
                                    {competitors.length === 0 ? (
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="bg-zinc-900/30 backdrop-blur-sm rounded-2xl p-12 border border-zinc-800/50 border-dashed text-center"
                                        >
                                            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-6">
                                                <Users className="w-10 h-10 text-blue-400" />
                                            </div>
                                            <h3 className="text-xl font-bold text-white mb-3">No Competitors Yet</h3>
                                            <p className="text-zinc-400 mb-6 max-w-md mx-auto leading-relaxed">
                                                Start tracking your competitors to unlock powerful market insights and identify strategic opportunities.
                                            </p>
                                            <button
                                                onClick={() => setShowManageModal(true)}
                                                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-medium text-white transition-all shadow-lg shadow-blue-500/20"
                                            >
                                                <Plus className="w-5 h-5" />
                                                <span>Add First Competitor</span>
                                            </button>
                                        </motion.div>
                                    ) : (
                                        competitors.map((competitor, index) => (
                                            <MarketCompetitorCard key={competitor.id} competitor={competitor} index={index} />
                                        ))
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* AI Opportunity Engine */}
                        <OpportunityEngine analysis={analysis ? analysis.opportunities.join("\n\n") : null} loading={analyzing} />
                    </div>

                    {/* Right Column: Heatmap & Quick Stats */}
                    <div className="lg:col-span-4 space-y-6">
                        <section className="bg-zinc-900/30 backdrop-blur-sm rounded-2xl border border-zinc-800/50 p-6">
                            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-purple-500" />
                                Sentiment Heatmap
                            </h2>
                            <MarketHeatmap competitors={competitors} />
                        </section>

                        {analysis && analysis.opportunities.length > 0 && (
                            <div className="bg-gradient-to-br from-indigo-900/20 to-purple-900/20 rounded-2xl border border-indigo-500/20 p-6">
                                <h3 className="font-semibold text-indigo-300 mb-2">Pro Tip</h3>
                                <p className="text-sm text-indigo-100/70 leading-relaxed">
                                    {analysis.opportunities[0]}
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Competitor Management Modal */}
            {showManageModal && brandId && (
                <CompetitorManagementModal
                    brandId={brandId}
                    onClose={() => setShowManageModal(false)}
                    onCompetitorAdded={() => {
                        loadCompetitors();
                        setShowManageModal(false);
                    }}
                />
            )}
        </div>
    );
}
