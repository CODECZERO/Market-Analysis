import { useMemo } from "react";
import { MessageSquare, ExternalLink, TrendingUp, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { motion, AnimatePresence } from "framer-motion";

// =============================================================================
// TYPES
// =============================================================================

interface Mention {
    id: string;
    text: string;
    intent: "HOT_LEAD" | "CHURN_RISK" | "BUG_REPORT" | "FEATURE_REQUEST" | "PRAISE" | "GENERAL";
    strategic_tag: "OPPORTUNITY_TO_STEAL" | "CRITICAL_ALERT" | "NONE";
    sentiment_score: number;
    is_competitor: boolean;
    source_platform?: string;
    source_url?: string;
    author?: string;
    created_at?: string;
    priority?: string;
    action_suggested?: string;
}

interface MoneyFeedProps {
    mentions: Mention[];
    onDraftReply?: (mention: Mention) => void;
    isLoading?: boolean;
}

// =============================================================================
// LEAD ITEM COMPONENT
// =============================================================================

function LeadItem({ mention, onDraftReply }: { mention: Mention; onDraftReply?: (m: Mention) => void }) {
    const isStealOpportunity = mention.strategic_tag === "OPPORTUNITY_TO_STEAL";

    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-colors"
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                <div className="flex items-center gap-2">
                    <span className={`
                        px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wide
                        ${isStealOpportunity
                            ? "bg-violet-500/10 text-violet-400 border border-violet-500/20"
                            : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"}
                    `}>
                        {isStealOpportunity ? "Opportunity" : "Lead"}
                    </span>
                    {mention.priority === "P0_CRITICAL" && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold text-white bg-rose-500">
                            P0
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2 text-[10px] text-zinc-500">
                    {mention.source_platform && (
                        <span className="capitalize">{mention.source_platform}</span>
                    )}
                    {mention.author && (
                        <span className="text-zinc-600">@{mention.author}</span>
                    )}
                </div>
            </div>

            {/* Content */}
            <p className="text-sm text-zinc-300 leading-relaxed mb-3 line-clamp-2 break-words">
                {mention.text}
            </p>

            {/* AI Recommendation */}
            {mention.action_suggested && (
                <div className="mb-3 py-2 px-3 rounded bg-zinc-800/50 border-l-2 border-zinc-700">
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium mb-0.5">Suggestion</p>
                    <p className="text-xs text-zinc-400">{mention.action_suggested}</p>
                </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-zinc-800/50 flex-wrap gap-2">
                <div className="flex items-center gap-1.5">
                    <div className={`w-1.5 h-1.5 rounded-full ${mention.sentiment_score > 0 ? "bg-emerald-500" : "bg-rose-500"}`} />
                    <span className="text-[10px] text-zinc-500">
                        {(mention.sentiment_score * 100).toFixed(0)}% sentiment
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    {mention.source_url && (
                        <a
                            href={mention.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 rounded bg-zinc-800 text-zinc-500 hover:text-white transition-colors"
                        >
                            <ExternalLink className="w-3 h-3" />
                        </a>
                    )}
                    <Button
                        size="sm"
                        onClick={() => onDraftReply?.(mention)}
                        className={`
                            h-7 text-[10px] font-medium rounded px-2.5
                            ${isStealOpportunity
                                ? "bg-violet-600 hover:bg-violet-500"
                                : "bg-emerald-600 hover:bg-emerald-500"}
                        `}
                    >
                        <MessageSquare className="w-3 h-3 mr-1" />
                        Reply
                    </Button>
                </div>
            </div>
        </motion.div>
    );
}

// =============================================================================
// MONEY FEED COMPONENT
// =============================================================================

export function MoneyFeed({ mentions, onDraftReply, isLoading }: MoneyFeedProps) {
    const moneyMentions = useMemo(() => {
        return mentions.filter(
            (m) => m.intent === "HOT_LEAD" || m.strategic_tag === "OPPORTUNITY_TO_STEAL"
        );
    }, [mentions]);

    const leadCount = moneyMentions.filter((m) => m.intent === "HOT_LEAD").length;
    const stealCount = moneyMentions.filter((m) => m.strategic_tag === "OPPORTUNITY_TO_STEAL").length;
    const totalOpportunities = leadCount + stealCount;

    return (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-zinc-800">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                            <TrendingUp className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-white">Money Feed</h3>
                            <p className="text-[11px] text-zinc-500">High-intent opportunities</p>
                        </div>
                    </div>
                    {totalOpportunities > 0 && (
                        <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                            <ArrowUpRight className="w-3 h-3 text-emerald-400" />
                            <span className="text-xs font-medium text-emerald-400">{totalOpportunities}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Content */}
            <div className="h-[280px]">
                {isLoading && mentions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-6">
                        <div className="w-6 h-6 rounded-full border-2 border-zinc-700 border-t-emerald-500 animate-spin mb-3" />
                        <p className="text-xs text-zinc-500">Scanning channels...</p>
                    </div>
                ) : moneyMentions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-6">
                        <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center mb-3">
                            <TrendingUp className="w-5 h-5 text-zinc-600" />
                        </div>
                        <h4 className="text-xs font-medium text-zinc-400 mb-1">No Leads Yet</h4>
                        <p className="text-[11px] text-zinc-600 max-w-[200px]">
                            Monitoring for pricing complaints and buying intent signals.
                        </p>
                    </div>
                ) : (
                    <ScrollArea className="h-full p-4">
                        <div className="space-y-3">
                            <AnimatePresence>
                                {moneyMentions.map((mention) => (
                                    <LeadItem
                                        key={mention.id}
                                        mention={mention}
                                        onDraftReply={onDraftReply}
                                    />
                                ))}
                            </AnimatePresence>
                        </div>
                    </ScrollArea>
                )}
            </div>
        </div>
    );
}

export default MoneyFeed;
