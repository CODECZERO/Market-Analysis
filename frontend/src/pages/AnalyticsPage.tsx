/**
 * Analytics Page
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft, TrendingUp, Zap, MessageSquare,
  Layers, AlertTriangle
} from "lucide-react";

import { LoadingState } from "@/components/shared/LoadingState";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TopicWordCloud } from "@/components/charts/TopicWordCloud";

import { useAnalyticsPage } from "@/hooks/analytics";
import {
  SentimentBreakdownCard,
  StatCard,
  AnalyticsHeader,
  SpikeDetectionCard,
  AISummaryCard,
  AnalyticsCharts
} from "@/components/analytics";

// Animation functional variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
};

export default function AnalyticsPage() {
  const {
    brandId,
    analyticsLoading,
    analyticsError,
    analyticsErrorObj,
    summary,
    spikes,
    sentimentTrend,
    latestSentiment,
    spikeTimeline,
    topics,
    summaryParagraphs,
    clusterHighlights,
    isSummaryExpanded,
    setSummaryExpanded,
  } = useAnalyticsPage();

  if (analyticsLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingState message="Loading analytics..." />
      </div>
    );
  }

  if (analyticsError) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Card className="border-red-500/20 bg-red-500/5 max-w-md backdrop-blur-xl">
            <CardContent className="p-8 text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 mb-4">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <p className="text-sm text-red-400 mb-4">
                {analyticsErrorObj?.message ?? "Unable to load analytics"}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="border-zinc-700 hover:bg-zinc-800"
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 3D Background Orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ x: [0, 30, 0], y: [0, -20, 0], scale: [1, 1.1, 1] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-20 right-1/4 w-[400px] h-[400px] bg-indigo-500/10 rounded-full blur-[100px]"
        />
        <motion.div
          animate={{ x: [0, -20, 0], y: [0, 30, 0] }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/2 -left-20 w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[80px]"
        />
        <motion.div
          animate={{ x: [0, 15, 0], y: [0, 15, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-20 right-1/3 w-[250px] h-[250px] bg-purple-500/8 rounded-full blur-[60px]"
        />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 space-y-6 p-6 pb-24 max-w-7xl mx-auto"
      >
        {/* Back Link */}
        <motion.div variants={itemVariants}>
          <Link
            to={`/brands/${brandId}/dashboard`}
            className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors group"
          >
            <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </Link>
        </motion.div>

        {/* Header */}
        <motion.div variants={itemVariants}>
          <AnalyticsHeader />
        </motion.div>

        {/* Quick Stats */}
        <motion.div variants={itemVariants} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={<MessageSquare className="h-5 w-5" />}
            value={summary?.totalMentions ?? 0}
            label="Total Mentions"
            color="blue"
          />
          <StatCard
            icon={<TrendingUp className="h-5 w-5" />}
            value={summary?.sentiment.score?.toFixed(2) ?? "0.00"}
            label="Sentiment Score"
            color="emerald"
          />
          <StatCard
            icon={<Zap className="h-5 w-5" />}
            value={spikes?.last24hCount ?? 0}
            label="Spikes (24h)"
            color="amber"
          />
          <StatCard
            icon={<Layers className="h-5 w-5" />}
            value={summary?.totalChunks ?? 0}
            label="Chunks Analyzed"
            color="purple"
          />
        </motion.div>

        {/* Sentiment Section */}
        <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
          <SentimentBreakdownCard
            positive={latestSentiment?.positive ?? summary?.sentiment.positive ?? 0}
            neutral={latestSentiment?.neutral ?? summary?.sentiment.neutral ?? 0}
            negative={latestSentiment?.negative ?? summary?.sentiment.negative ?? 0}
          />

          <SpikeDetectionCard
            spikeDetected={summary?.spikeDetected ?? false}
            last24hCount={spikes?.last24hCount ?? 0}
            sentimentScore={summary?.sentiment.score ?? 0}
          />

          <TopicWordCloud topics={topics} clusters={summary?.clusters} />
        </motion.div>

        {/* AI Summary */}
        <motion.div variants={itemVariants}>
          <AISummaryCard
            summaryParagraphs={summaryParagraphs}
            clusterHighlights={clusterHighlights}
            chunkSummaries={summary?.chunkSummaries ?? []}
            summary={summary}
            isSummaryExpanded={isSummaryExpanded}
            onToggleExpand={() => setSummaryExpanded(!isSummaryExpanded)}
          />
        </motion.div>

        {/* Charts */}
        <motion.div variants={itemVariants}>
          <AnalyticsCharts
            sentimentTrend={sentimentTrend}
            spikeTimeline={spikeTimeline}
          />
        </motion.div>
      </motion.div>
    </div>
  );
}
