import { motion } from "framer-motion";
import { User, ExternalLink, Twitter, MessageCircle, Users } from "lucide-react";
import type { Influencer } from "@/types/api";

interface InfluencerCardProps {
    influencer: Influencer;
    index: number;
}

export function InfluencerCard({ influencer, index }: InfluencerCardProps) {
    const getSentimentColor = () => {
        switch (influencer.sentiment) {
            case "positive":
                return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
            case "negative":
                return "bg-red-500/20 text-red-400 border-red-500/30";
            default:
                return "bg-gray-500/20 text-gray-400 border-gray-500/30";
        }
    };

    const getSourceIcon = () => {
        switch (influencer.source?.toLowerCase()) {
            case "twitter":
            case "x":
                return <Twitter className="w-4 h-4 text-blue-400" />;
            case "reddit":
                return <MessageCircle className="w-4 h-4 text-orange-400" />;
            default:
                return <User className="w-4 h-4 text-purple-400" />;
        }
    };

    const formatFollowers = (count: number) => {
        if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
        if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
        return count.toString();
    };

    const author = influencer.metadata?.author || "Unknown Author";
    const url = influencer.metadata?.url;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-4 rounded-xl border border-white/10 hover:border-purple-500/50 transition-all"
        >
            <div className="flex items-start gap-4">
                {/* Avatar placeholder */}
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                    <User className="w-6 h-6 text-white" />
                </div>

                <div className="flex-1 min-w-0">
                    {/* Author and source */}
                    <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-white truncate">{author}</span>
                        {getSourceIcon()}
                        {url && (
                            <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-purple-400 transition-colors"
                            >
                                <ExternalLink className="w-4 h-4" />
                            </a>
                        )}
                    </div>

                    {/* Followers and influence score */}
                    <div className="flex items-center gap-4 text-sm text-gray-400 mb-2">
                        <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {formatFollowers(influencer.author_followers)} followers
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-purple-500" />
                            Score: {influencer.influence_score.toFixed(2)}
                        </span>
                    </div>

                    {/* Text preview */}
                    <p className="text-sm text-gray-300 line-clamp-2">{influencer.text}</p>
                </div>

                {/* Sentiment badge */}
                <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getSentimentColor()}`}>
                    {influencer.sentiment}
                </div>
            </div>
        </motion.div>
    );
}

// List component for multiple influencers
interface InfluencerListProps {
    influencers: Influencer[];
    isLoading?: boolean;
}

export function InfluencerList({ influencers, isLoading }: InfluencerListProps) {
    if (isLoading) {
        return (
            <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                    <div key={i} className="glass-card p-4 rounded-xl animate-pulse">
                        <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-full bg-white/10" />
                            <div className="flex-1 space-y-2">
                                <div className="h-4 bg-white/10 rounded w-1/3" />
                                <div className="h-3 bg-white/10 rounded w-1/2" />
                                <div className="h-3 bg-white/10 rounded w-full" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (!influencers?.length) {
        return (
            <div className="glass-card p-6 rounded-xl border border-white/10 text-center">
                <User className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400">No influencers detected yet.</p>
                <p className="text-sm text-gray-500 mt-1">
                    High-influence mentions will appear here as they're processed.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {influencers.slice(0, 5).map((influencer, index) => (
                <InfluencerCard key={influencer.id} influencer={influencer} index={index} />
            ))}
        </div>
    );
}
