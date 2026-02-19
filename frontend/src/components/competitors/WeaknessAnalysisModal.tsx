/**
 * Weakness Analysis Modal
 * 
 * Modal showing competitor weakness analysis with opportunities
 */

import { motion, AnimatePresence } from "framer-motion";
import { X, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { WeaknessAnalysis } from "@/types/api";

interface WeaknessAnalysisModalProps {
    isOpen: boolean;
    onClose: () => void;
    analysis: (WeaknessAnalysis & { competitorName?: string }) | null;
}

export function WeaknessAnalysisModal({ isOpen, onClose, analysis }: WeaknessAnalysisModalProps) {
    if (!analysis) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="bg-zinc-900/90 border border-zinc-700/50 backdrop-blur-xl rounded-2xl p-6 w-full max-w-lg shadow-2xl relative max-h-[80vh] overflow-y-auto"
                    >
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 text-zinc-500 hover:text-white"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <h2 className="text-xl font-semibold text-white mb-2">
                            Weakness Analysis: {analysis.competitorName}
                        </h2>
                        <p className="text-sm text-zinc-500 mb-6">
                            {analysis.totalComplaints} complaints analyzed
                        </p>

                        {/* Category Breakdown */}
                        {analysis.categoryBreakdown?.length > 0 && (
                            <div className="space-y-3 mb-6">
                                <h4 className="text-sm font-medium text-zinc-400">Complaint Categories</h4>
                                {analysis.categoryBreakdown.map((cat, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <div className="flex-1">
                                            <div className="flex justify-between text-sm mb-1">
                                                <span className="text-zinc-300">{cat.category}</span>
                                                <span className="text-zinc-500">{cat.percentage}%</span>
                                            </div>
                                            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-purple-500 rounded-full"
                                                    style={{ width: `${cat.percentage}%` }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Opportunities */}
                        {analysis.opportunities?.length > 0 && (
                            <div>
                                <h4 className="text-sm font-medium text-zinc-400 mb-3">Opportunities</h4>
                                <ul className="space-y-2">
                                    {analysis.opportunities.map((opp, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                                            <ChevronRight className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                            {opp}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <div className="flex justify-end mt-8">
                            <Button
                                onClick={onClose}
                                className="bg-zinc-800 hover:bg-zinc-700 text-white"
                            >
                                Close
                            </Button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
