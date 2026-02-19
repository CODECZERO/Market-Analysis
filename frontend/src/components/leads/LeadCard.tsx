/**
 * Lead Card Component
 * 
 * Displays a sales lead with platform info, score, and actions
 */

import { motion } from "framer-motion";
import type { Lead } from "@/types/api";

const PLATFORM_COLORS: Record<string, string> = {
    reddit: "#FF4500",
    twitter: "#1DA1F2",
    hackernews: "#FF6600",
    producthunt: "#DA552F",
    aggregator: "#6366F1",
    news: "#10B981",
};

interface LeadCardProps {
    lead: Lead;
    index: number;
    isSelected: boolean;
    onSelect: () => void;
    onStatusChange: (id: string, status: string) => void;
}

export function LeadCard({
    lead,
    index,
    isSelected,
    onSelect,
    onStatusChange,
}: LeadCardProps) {
    const platformColor = PLATFORM_COLORS[lead.sourcePlatform?.toLowerCase() || ""] || "#6B7280";

    const getRelativeTime = (dateStr: string) => {
        try {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) return "just now";
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            return date.toLocaleDateString();
        } catch {
            return "recently";
        }
    };

    const formatAuthor = (author: string | undefined) => {
        if (!author || author === "Anonymous" || author === "unknown") {
            return "Unknown User";
        }
        return author.startsWith("@") ? author : `@${author}`;
    };

    const getScoreStyle = (score: number) => {
        if (score >= 80) return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
        if (score >= 60) return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";
        if (score >= 40) return "bg-orange-500/10 text-orange-400 border-orange-500/20";
        return "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
    };

    const getScoreLabel = (score: number) => {
        if (score >= 80) return "Hot";
        if (score >= 60) return "Warm";
        if (score >= 40) return "Cool";
        return "Cold";
    };

    const score = lead.leadScore || lead.confidence * 100 || 50;

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
            onClick={onSelect}
            className={`
                group relative bg-zinc-900/30 rounded-xl p-4 border transition-all cursor-pointer
                ${isSelected
                    ? "border-emerald-500/50 shadow-lg shadow-emerald-500/5 bg-emerald-500/5"
                    : "border-zinc-800/50 hover:border-zinc-700 hover:bg-zinc-900/50"
                }
            `}
        >
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2.5">
                    <div
                        className="w-9 h-9 rounded-lg flex items-center justify-center text-white shadow-md shrink-0"
                        style={{ backgroundColor: platformColor }}
                    >
                        <span className="font-bold text-xs">{(lead.sourcePlatform || "?")[0].toUpperCase()}</span>
                    </div>
                    <div>
                        <div className="flex items-center gap-1.5">
                            <p className="text-sm font-semibold text-zinc-200">{formatAuthor(lead.sourceAuthor || undefined)}</p>
                            <span className="text-[10px] text-zinc-500">•</span>
                            <span className="text-[10px] text-zinc-500 capitalize">{lead.sourcePlatform || "unknown"}</span>
                        </div>
                        <p className="text-[10px] text-zinc-500">{getRelativeTime(lead.createdAt)}</p>
                    </div>
                </div>
                <div className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getScoreStyle(score)}`}>
                    {getScoreLabel(score)} • {Math.round(score)}
                </div>
            </div>

            <p className="text-sm text-zinc-300 mb-4 leading-relaxed line-clamp-2 group-hover:line-clamp-none transition-all">
                "{lead.sourceText}"
            </p>

            <div className="flex items-center justify-between pt-3 border-t border-zinc-800/50">
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-[10px] text-emerald-400 border border-emerald-500/20 font-medium">
                    {lead.intentType?.replace(/_/g, " ") || "commercial intent"}
                </span>

                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-zinc-500">Conf.</span>
                        <div className="w-12 h-1 bg-zinc-800 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                                style={{ width: `${(lead.confidence || 0.7) * 100}%` }}
                            />
                        </div>
                        <span className="text-[10px] text-zinc-400">{Math.round((lead.confidence || 0.7) * 100)}%</span>
                    </div>

                    {lead.status === "new" && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onStatusChange(lead.id, "qualified");
                            }}
                            className="text-[10px] font-medium text-emerald-400 hover:text-emerald-300 hover:underline"
                        >
                            Qualify
                        </button>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
