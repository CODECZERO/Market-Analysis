/**
 * Brand Dashboard Page
 * 
 * Modularized dashboard using extracted sections and data hook.
 */

import { motion } from "framer-motion";

import { useBrandDashboard } from "@/hooks/dashboard";

import { EnhancedSummaryCards } from "@/components/dashboard/EnhancedSummaryCards";
import { GettingStarted } from "@/components/dashboard/GettingStarted";
import { LoadingState } from "@/components/shared/LoadingState";

import {
  AdvancedIntelligence,
  CommandCenter,
  LiveFeedSection,
  AnalyticsSection
} from "@/components/dashboard/sections";

export default function BrandDashboardPage() {
  const {
    brandId,
    isConnected,
    isInitialLoading,
    data,
    loading,
    derived,
    actions
  } = useBrandDashboard();

  if (isInitialLoading) {
    return <LoadingState message="Loading brand dashboard..." />;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="space-y-6 pb-24"
    >
      <GettingStarted brandId={brandId} />

      {/* 1. High-Level Summary Cards */}
      <section>
        <EnhancedSummaryCards
          summary={data.summary}
          spikes={data.spikes}
          mentions={data.mentions}
          sentimentTrend={derived.sentimentTrend}
          spikeTimeline={derived.spikeTimeline}
        />
      </section>

      {/* 2. Advanced Intelligence Section */}
      <AdvancedIntelligence
        summary={data.summary}
        entities={data.entities}
        suggestions={data.suggestions}
        trends={data.trends}
        influencers={data.influencers}
        loading={loading}
      />

      {/* 3. Command Center Section */}
      <CommandCenter
        isConnected={isConnected}
        transformedMentions={derived.transformedMentions}
        battlefieldData={derived.battlefieldData}
        launches={data.launches}
        loading={loading}
        onDraftReply={actions.handleDraftReply}
      />

      {/* 4. Live Data Section */}
      <LiveFeedSection
        summary={data.summary}
        mentions={data.mentions || []}
        isLoading={loading.mentions}
      />

      {/* 5. Analytics Charts */}
      <AnalyticsSection
        sentimentTrend={derived.sentimentTrend}
        spikeTimeline={derived.spikeTimeline}
      />
    </motion.div>
  );
}
