/**
 * Recommended Actions List Component
 */

import { motion } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface RecommendedActionsListProps {
    actions: string[];
    sourceCount: number;
    selectedAction: string | null;
    onSelectAction: (action: string | null) => void;
}

export function RecommendedActionsList({
    actions,
    sourceCount,
    selectedAction,
    onSelectAction
}: RecommendedActionsListProps) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
        >
            <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-6 flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-blue-400 mt-0.5" />
                <div>
                    <h3 className="text-blue-400 font-medium">AI Recommended Strategy</h3>
                    <p className="text-sm text-blue-400/80 mt-1">
                        Based on the analysis of {sourceCount} sources, these are the highest impact actions you should take immediately.
                    </p>
                </div>
            </div>

            {actions.map((action, idx) => (
                <Card
                    key={idx}
                    className="bg-zinc-900 border-zinc-800 hover:border-zinc-700 transition-colors group cursor-pointer"
                    onClick={() => onSelectAction(action)}
                >
                    <CardContent className="p-6 flex items-center justify-between gap-4">
                        <div className="flex items-start gap-4">
                            <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-400 font-mono font-bold group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                {String(idx + 1).padStart(2, '0')}
                            </div>
                            <p className="text-zinc-200 text-lg pt-0.5 font-medium">{action}</p>
                        </div>
                        <ArrowRight className="w-5 h-5 text-zinc-600 group-hover:translate-x-1 group-hover:text-blue-400 transition-all" />
                    </CardContent>
                </Card>
            ))}

            <div className="mt-8 pt-8 border-t border-zinc-800 text-center">
                <p className="text-zinc-500 italic">"Intelligence is the ability to adapt to change."</p>
            </div>

            {/* Action Detail Dialog */}
            <Dialog open={!!selectedAction} onOpenChange={(open) => !open && onSelectAction(null)}>
                <DialogContent className="bg-zinc-900 border-zinc-800 text-white max-w-lg">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-xl">
                            <Sparkles className="w-5 h-5 text-blue-500" />
                            Strategy Detail
                        </DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                            <p className="text-lg font-medium text-zinc-200">{selectedAction}</p>
                        </div>

                        <div className="space-y-3">
                            <h4 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Implementation Steps</h4>
                            <div className="flex gap-3">
                                <div className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center text-xs font-mono border border-blue-500/20">1</div>
                                <p className="text-sm text-zinc-300">Evaluate current resources and gaps related to this initiative.</p>
                            </div>
                            <div className="flex gap-3">
                                <div className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center text-xs font-mono border border-blue-500/20">2</div>
                                <p className="text-sm text-zinc-300">Assign a dedicated owner to drive execution within the next 30 days.</p>
                            </div>
                            <div className="flex gap-3">
                                <div className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center text-xs font-mono border border-blue-500/20">3</div>
                                <p className="text-sm text-zinc-300">Measure impact using defined KPIs and adjust strategy quarterly.</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-4">
                        <button
                            onClick={() => onSelectAction(null)}
                            className="px-4 py-2 rounded-md bg-zinc-800 hover:bg-zinc-700 text-sm font-medium transition-colors"
                        >
                            Close
                        </button>
                        <button className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-500 text-sm font-medium transition-colors">
                            Create Task
                        </button>
                    </div>
                </DialogContent>
            </Dialog>
        </motion.div>
    );
}
