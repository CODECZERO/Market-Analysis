/**
 * Analytics Page Hook
 */

import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { useBrandAnalytics, useBrandSpikes, useBrandSummary } from "@/hooks/brands";
import { parseLabelOrJson } from "@/utils/textParsing";

export function useAnalyticsPage() {
    const { brandId = "" } = useParams<{ brandId: string }>();

    const {
        data: analytics,
        isLoading: analyticsLoading,
        isError: analyticsError,
        error: analyticsErrorObj,
    } = useBrandAnalytics(brandId);
    const { data: summary } = useBrandSummary(brandId);
    const { data: spikes } = useBrandSpikes(brandId);

    const sentimentTrend = analytics?.sentimentTrend ?? [];
    const latestSentiment = useMemo(() => sentimentTrend.at(-1), [sentimentTrend]);
    const spikeTimeline = spikes?.timeline ?? [];
    const topics = analytics?.topics ?? summary?.dominantTopics?.map((term) => ({ term, weight: 0.12 })) ?? [];

    const summaryParagraphs = useMemo(() => {
        if (!summary?.summary) return [] as string[];
        // Clean up summary text
        let cleanText = summary.summary
            .replace(/^(AI-Generated Summary|Summary|Analysis):?\s*/i, "")
            .replace(/\*\*(AI-Generated Summary|Summary|Analysis):\*\*\s*/i, "")
            .trim();

        return cleanText
            .split(/\n+/)
            .map((line) => line.trim())
            .filter(Boolean);
    }, [summary?.summary]);

    const clusterHighlights = summary?.clusters ?? [];
    const [isSummaryExpanded, setSummaryExpanded] = useState(false);

    return {
        brandId,
        analytics,
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
        parseLabelOrJson
    };
}
