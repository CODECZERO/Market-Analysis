/**
 * Brand Dashboard Hook
 * 
 * Aggregates all data needed for the brand dashboard.
 * Handles WebSocket subscriptions, data transformation, and session tracking.
 */

import { useMemo, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { initializeSession, trackActivity, getTimeSinceLogout } from "@/lib/sessionTracker";
import { useWebSocket } from "@/contexts/WebSocketContext";

import {
    useBrandAnalytics,
    useBrandSpikes,
    useBrandSummary,
    useLiveMentions,
    useBrandEntities,
    useBrandSuggestions,
    useBrandTrends,
    useBrandInfluencers,
    useBrandLaunches
} from "@/hooks/brands";
import { useCompetitorComparison } from "@/hooks/useStats";

export function useBrandDashboard() {
    const { brandId = "" } = useParams<{ brandId: string }>();
    const queryClient = useQueryClient();
    const { subscribeToBrand, unsubscribeFromBrand, lastMessage, isConnected } = useWebSocket();

    // Subscribe to WebSocket updates
    useEffect(() => {
        if (brandId) {
            subscribeToBrand(brandId);
            return () => unsubscribeFromBrand(brandId);
        }
    }, [brandId, subscribeToBrand, unsubscribeFromBrand]);

    // Handle WebSocket updates
    useEffect(() => {
        if (lastMessage && lastMessage.brand === brandId) {
            queryClient.invalidateQueries({ queryKey: ["brand", brandId] });
            queryClient.invalidateQueries({ queryKey: ["liveMentions", brandId] });
            queryClient.invalidateQueries({ queryKey: ["summary", brandId] });
            queryClient.invalidateQueries({ queryKey: ["spikes", brandId] });
            queryClient.invalidateQueries({ queryKey: ["analytics", brandId] });
        }
    }, [lastMessage, brandId, queryClient]);

    // Session & Activity Tracking
    useEffect(() => {
        const session = initializeSession();
        if (session.isFirstLoad && session.logoutTime) {
            const timeSince = getTimeSinceLogout();
            if (timeSince) {
                console.info(`Loading updates from ${timeSince} ago...`);
            }
        }
    }, []);

    useEffect(() => {
        const handleActivity = () => trackActivity();
        window.addEventListener('click', handleActivity, { passive: true });
        window.addEventListener('keydown', handleActivity, { passive: true });
        window.addEventListener('scroll', handleActivity, { passive: true });
        const interval = setInterval(handleActivity, 60000);
        return () => {
            window.removeEventListener('click', handleActivity);
            window.removeEventListener('keydown', handleActivity);
            window.removeEventListener('scroll', handleActivity);
            clearInterval(interval);
        };
    }, []);

    // Data Hooks
    const { data: summary, isLoading: summaryLoading } = useBrandSummary(brandId);
    const { data: spikes, isLoading: spikesLoading } = useBrandSpikes(brandId);
    const { data: mentions, isLoading: mentionsLoading } = useLiveMentions(brandId);
    const { data: analytics, isLoading: analyticsLoading } = useBrandAnalytics(brandId);
    const { data: comparison, isLoading: comparisonLoading } = useCompetitorComparison("24h");
    const { data: entities, isLoading: entitiesLoading } = useBrandEntities(brandId);
    const { data: suggestions, isLoading: suggestionsLoading } = useBrandSuggestions(brandId);
    const { data: trends, isLoading: trendsLoading } = useBrandTrends(brandId);
    const { data: influencers, isLoading: influencersLoading } = useBrandInfluencers(brandId);
    const { data: launches, isLoading: launchesLoading } = useBrandLaunches(brandId);

    // Transformations
    const sentimentTrend = useMemo(() => analytics?.sentimentTrend ?? [], [analytics]);
    const spikeTimeline = useMemo(() => spikes?.timeline ?? [], [spikes]);

    const transformedMentions = useMemo(() => {
        if (!mentions || !Array.isArray(mentions)) return [];
        return mentions.map((m: any) => ({
            id: m.id || String(Math.random()),
            text: m.text || "",
            intent: m.intent || "GENERAL",
            strategic_tag: m.strategic_tag || "NONE",
            sentiment_score: m.sentiment_score ?? (m.sentiment === "positive" ? 0.5 : m.sentiment === "negative" ? -0.5 : 0),
            is_competitor: m.is_competitor || false,
            source_platform: m.source || m.metadata?.platform,
            source_url: m.metadata?.url,
            author: m.metadata?.author,
            created_at: m.createdAt,
            priority: m.priority,
            action_suggested: m.action_suggested,
        }));
    }, [mentions]);

    const battlefieldData = useMemo(() => {
        if (!comparison?.market_share?.length) return null;
        const myBrand = comparison.market_share[0];
        const competitor = comparison.market_share[1];
        if (!myBrand || !competitor) return null;
        return {
            myBrand: {
                name: myBrand.name,
                mentionCount: myBrand.value,
                avgSentiment: comparison.sentiment.me,
                positiveCount: myBrand.sentimentCounts?.positive ?? 0,
                negativeCount: myBrand.sentimentCounts?.negative ?? 0,
                neutralCount: myBrand.sentimentCounts?.neutral ?? 0,
                trend: comparison.sentiment.me > comparison.sentiment.competitor ? "up" as const : "stable" as const,
                isCompetitor: false,
            },
            competitor: {
                name: competitor.name,
                mentionCount: competitor.value,
                avgSentiment: comparison.sentiment.competitor,
                positiveCount: competitor.sentimentCounts?.positive ?? 0,
                negativeCount: competitor.sentimentCounts?.negative ?? 0,
                neutralCount: competitor.sentimentCounts?.neutral ?? 0,
                trend: comparison.sentiment.competitor > 0 ? "up" as const : "down" as const,
                isCompetitor: true,
            },
        };
    }, [comparison]);

    const handleDraftReply = useCallback((mention: any) => {
        console.log("Draft reply for:", mention);
    }, []);

    const isInitialLoading = (summaryLoading || spikesLoading || mentionsLoading) && (!summary && !spikes && !mentions);

    return {
        brandId,
        isConnected,
        isInitialLoading,
        data: {
            summary,
            spikes,
            mentions,
            analytics,
            comparison,
            entities,
            suggestions,
            trends,
            influencers,
            launches,
        },
        loading: {
            summary: summaryLoading,
            spikes: spikesLoading,
            mentions: mentionsLoading,
            analytics: analyticsLoading,
            comparison: comparisonLoading,
            entities: entitiesLoading,
            suggestions: suggestionsLoading,
            trends: trendsLoading,
            influencers: influencersLoading,
            launches: launchesLoading,
        },
        derived: {
            sentimentTrend,
            spikeTimeline,
            transformedMentions,
            battlefieldData,
        },
        actions: {
            handleDraftReply,
        }
    };
}
