/**
 * AI Summary Card
 */

import { motion } from "framer-motion";
import { Brain, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { parseLabelOrJson } from "@/utils/textParsing";
import DOMPurify from 'dompurify'; // ✅ SECURITY FIX: XSS Protection

interface AISummaryCardProps {
    summaryParagraphs: string[];
    clusterHighlights: any[];
    chunkSummaries: any[];
    summary: any;
    isSummaryExpanded: boolean;
    onToggleExpand: () => void;
}

export function AISummaryCard({
    summaryParagraphs,
    clusterHighlights,
    chunkSummaries,
    summary,
    isSummaryExpanded,
    onToggleExpand
}: AISummaryCardProps) {
    const maxSummaryParagraphs = isSummaryExpanded ? summaryParagraphs.length : 2;
    const maxClusterItems = isSummaryExpanded ? clusterHighlights.length : 3;
    const maxChunkHighlights = isSummaryExpanded ? chunkSummaries.length : 3;

    return (
        <Card className="border-zinc-800/50 bg-gradient-to-br from-zinc-900/50 via-zinc-900/30 to-indigo-950/20 backdrop-blur-xl overflow-hidden">
            <CardHeader className="border-b border-zinc-800/50">
                <CardTitle className="text-lg font-semibold flex items-center gap-3">
                    <motion.div
                        animate={{ rotate: [0, 5, -5, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20"
                    >
                        <Brain className="h-5 w-5 text-indigo-400" />
                    </motion.div>
                    AI-Generated Summary
                    <span className="ml-auto px-2 py-1 text-[10px] font-medium rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1">
                        <Sparkles className="h-3 w-3" />
                        Powered by AI
                    </span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
                {summaryParagraphs.length > 0 ? (
                    <div className="space-y-3 text-sm text-zinc-300 leading-relaxed">
                        {summaryParagraphs.slice(0, maxSummaryParagraphs).map((paragraph, index) => {
                            const { label, isJson } = parseLabelOrJson(paragraph);

                            if (isJson) {
                                return (
                                    <div key={`summary-${index}`} className="p-3 my-2 rounded-lg bg-indigo-500/5 border border-indigo-500/10 dark:bg-zinc-800/50 dark:border-zinc-700">
                                        <div className="flex items-start gap-2">
                                            <Sparkles className="h-4 w-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                                            <span className="text-sm text-zinc-300 font-medium">{label}</span>
                                        </div>
                                    </div>
                                );
                            }

                            // ✅ SECURITY FIX: Sanitize HTML to prevent XSS attacks
                            const sanitizedHtml = DOMPurify.sanitize(paragraph, {
                                ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a'],
                                ALLOWED_ATTR: ['href', 'target'],
                                ALLOW_DATA_ATTR: false
                            });

                            return (
                                <div
                                    key={`summary-${index}`}
                                    dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
                                    className="[&>p]:mb-3 [&>ul]:list-disc [&>ul]:pl-5 [&>li]:mb-1"
                                />
                            );
                        })}
                    </div>
                ) : (
                    <p className="text-sm text-zinc-500">No summary generated yet.</p>
                )}

                {clusterHighlights.length > 0 && (
                    <div className="pt-4 border-t border-zinc-800/50">
                        <h4 className="text-xs font-semibold uppercase tracking-wide text-zinc-500 mb-3">
                            Cluster Highlights
                        </h4>
                        <div className="grid gap-2 sm:grid-cols-2">
                            {clusterHighlights.slice(0, maxClusterItems).map((cluster) => (
                                <motion.div
                                    key={cluster.id}
                                    whileHover={{ scale: 1.02 }}
                                    className="p-3 rounded-xl bg-zinc-800/30 border border-zinc-700/50 transition-colors hover:border-zinc-600/50"
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-white truncate max-w-[200px]" title={parseLabelOrJson(cluster.label).label}>
                                            {parseLabelOrJson(cluster.label).label.length > 50
                                                ? parseLabelOrJson(cluster.label).label.substring(0, 50) + "..."
                                                : parseLabelOrJson(cluster.label).label}
                                        </span>
                                        {cluster.spike && (
                                            <span className="px-1.5 py-0.5 text-[10px] rounded-md bg-amber-500/20 text-amber-400 border border-amber-500/20">
                                                SPIKE
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs text-zinc-500 mt-1">{cluster.mentions} mentions</p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}

                {chunkSummaries && chunkSummaries.length > 0 && (
                    <div className="pt-4 border-t border-zinc-800/50">
                        <h4 className="text-xs font-semibold uppercase tracking-wide text-zinc-500 mb-3">
                            Key Insights
                        </h4>
                        <ul className="space-y-2">
                            {chunkSummaries.slice(0, maxChunkHighlights).map((item, index) => {
                                const { label } = parseLabelOrJson(item);
                                return (
                                    <li key={`chunk-${index}`} className="flex items-start gap-2 text-sm text-zinc-300">
                                        <span className="text-indigo-400 mt-1">•</span>
                                        {label}
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                )}

                {(summaryParagraphs.length > 2 || clusterHighlights.length > 3 || (chunkSummaries?.length ?? 0) > 3) && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onToggleExpand}
                        className="text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10"
                    >
                        {isSummaryExpanded ? (
                            <>
                                <ChevronUp className="h-4 w-4 mr-1" />
                                Show Less
                            </>
                        ) : (
                            <>
                                <ChevronDown className="h-4 w-4 mr-1" />
                                Show More
                            </>
                        )}
                    </Button>
                )}

                <div className="pt-4 border-t border-zinc-800/50 flex flex-wrap gap-4 text-xs text-zinc-500">
                    <span><strong className="text-zinc-400">Total mentions:</strong> {summary?.totalMentions ?? 0}</span>
                    <span><strong className="text-zinc-400">Chunks processed:</strong> {summary?.totalChunks ?? 0}</span>
                    <span><strong className="text-zinc-400">Generated:</strong> {summary ? new Date(summary.generatedAt).toLocaleString() : "n/a"}</span>
                </div>
            </CardContent>
        </Card>
    );
}
