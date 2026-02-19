/**
 * Competitors List
 * 
 * Displays tracked competitors with actions (analysis, delete)
 */

import { motion } from "framer-motion";
import { Users, Trash2, Eye, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Competitor } from "@/types/api";

interface CompetitorsListProps {
    competitors: Competitor[];
    loading: boolean;
    deletingId: string | null;
    onAnalyze: (id: string, name: string) => void;
    onDelete: (id: string) => void;
    onAddFirst: () => void;
}

export function CompetitorsList({
    competitors,
    loading,
    deletingId,
    onAnalyze,
    onDelete,
    onAddFirst,
}: CompetitorsListProps) {
    return (
        <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader className="pb-4 flex flex-row items-center justify-between">
                <CardTitle className="text-base font-semibold">Tracked Competitors</CardTitle>
                <span className="text-xs text-zinc-500">{competitors.length} competitors</span>
            </CardHeader>
            <CardContent className="p-0">
                {loading ? (
                    <div className="p-8 text-center text-zinc-500">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                        Loading competitors...
                    </div>
                ) : competitors.length === 0 ? (
                    <div className="p-12 text-center">
                        <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center mx-auto mb-4 border border-zinc-700">
                            <Users className="w-6 h-6 text-zinc-500" />
                        </div>
                        <h3 className="text-lg font-medium text-white mb-2">No Competitors Yet</h3>
                        <p className="text-sm text-zinc-400 mb-6 max-w-sm mx-auto">
                            Add competitors to track their mentions and compare against your brand.
                        </p>
                        <Button onClick={onAddFirst} variant="outline">
                            Add First Competitor
                        </Button>
                    </div>
                ) : (
                    <div className="divide-y divide-zinc-800">
                        {competitors.map((competitor, index) => (
                            <motion.div
                                key={competitor.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="p-4 flex items-center justify-between hover:bg-zinc-800/50 transition-all duration-200 border border-transparent hover:border-zinc-800 rounded-lg group"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20 flex items-center justify-center text-lg font-bold text-white shadow-sm">
                                        {competitor.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-white text-lg tracking-tight">{competitor.name}</h4>
                                        <div className="flex items-center gap-3 text-xs text-zinc-500 mt-1">
                                            <Badge variant="secondary" className="bg-zinc-800 text-zinc-400 font-normal">
                                                {competitor.keywords?.length || 0} keywords
                                            </Badge>
                                            <span>Added {
                                                competitor.createdAt && !isNaN(new Date(competitor.createdAt).getTime())
                                                    ? new Date(competitor.createdAt).toLocaleDateString()
                                                    : "Recently"
                                            }</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => onAnalyze(competitor.id, competitor.name)}
                                        className="text-zinc-400 hover:text-white"
                                    >
                                        <Eye className="w-4 h-4 mr-1" />
                                        Analysis
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => onDelete(competitor.id)}
                                        disabled={deletingId === competitor.id}
                                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                    >
                                        {deletingId === competitor.id ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <Trash2 className="w-4 h-4" />
                                        )}
                                    </Button>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
