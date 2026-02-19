/**
 * Advanced Intelligence Section
 */

import { motion } from "framer-motion";
import { Brain, Users } from "lucide-react";
import { SectionHeader } from "@/components/shared";
import { BusinessInsightsCard } from "@/components/dashboard/BusinessInsightsCard";
import { EntityCloud } from "@/components/dashboard/EntityCloud";
import { SuggestionsFeed } from "@/components/dashboard/SuggestionsFeed";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { InfluencerList } from "@/components/dashboard/InfluencerCard";
import { QuickAccessCards } from "@/components/dashboard/EnhancedSummaryCards";

interface AdvancedIntelligenceProps {
    summary: any;
    entities: any;
    suggestions: any;
    trends: any;
    influencers: any;
    loading: {
        entities: boolean;
        suggestions: boolean;
        trends: boolean;
        influencers: boolean;
    };
}

export function AdvancedIntelligence({
    summary,
    entities,
    suggestions,
    trends,
    influencers,
    loading
}: AdvancedIntelligenceProps) {
    return (
        <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.4 }}
        >
            <SectionHeader
                icon={Brain}
                title="Advanced Intelligence"
                subtitle="AI-powered insights for sales, risk, and strategy"
            />

            {/* Business Intelligence Card */}
            <div className="mb-4">
                <BusinessInsightsCard summary={summary ?? null} />
            </div>

            {/* Entities & Suggestions Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <EntityCloud data={entities ?? null} isLoading={loading.entities} />
                <SuggestionsFeed data={suggestions ?? null} isLoading={loading.suggestions} />
            </div>

            {/* Trends & Influencers Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <TrendChart trend={trends ?? null} isLoading={loading.trends} />
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-4">
                        <Users className="w-4 h-4 text-purple-400" />
                        <h3 className="text-sm font-semibold text-white">Top Influencers</h3>
                    </div>
                    <InfluencerList
                        influencers={influencers?.influencers ?? []}
                        isLoading={loading.influencers}
                    />
                </div>
            </div>

            <QuickAccessCards />
        </motion.section>
    );
}
