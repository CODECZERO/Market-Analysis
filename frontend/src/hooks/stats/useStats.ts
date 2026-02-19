/**
 * Stats Hooks
 * 
 * Hooks for competitor comparison and analytics
 */

import { useQuery, keepPreviousData } from "@tanstack/react-query";
import {
    getCompetitorComparison,
    getMarketShareTrend,
    getStatsSummary
} from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type {
    CompetitorComparisonResponse,
    MarketShareTrendResponse,
    StatsSummaryResponse,
    MarketShareItem
} from "@/types/api";

// Re-export types for backward compatibility
export type {
    CompetitorComparisonResponse,
    MarketShareTrendResponse,
    StatsSummaryResponse,
    MarketShareItem
};

// =============================================================================
// HOOKS
// =============================================================================

export function useCompetitorComparison(timeframe: string = "24h") {
    return useQuery<CompetitorComparisonResponse>({
        queryKey: ["stats", "competitor-comparison", timeframe],
        queryFn: () => getCompetitorComparison(timeframe),
        refetchInterval: 60_000,
        staleTime: 30_000,
        placeholderData: keepPreviousData,
    });
}

export function useMarketShareTrend(days: number = 7) {
    return useQuery<MarketShareTrendResponse>({
        queryKey: ["stats", "market-share-trend", days],
        queryFn: () => getMarketShareTrend(days),
        refetchInterval: 300_000,
        staleTime: 120_000,
        placeholderData: keepPreviousData,
    });
}

export function useStatsSummary() {
    return useQuery<StatsSummaryResponse>({
        queryKey: ["stats", "summary"],
        queryFn: getStatsSummary,
        refetchInterval: 60_000,
        staleTime: 30_000,
        placeholderData: keepPreviousData,
    });
}
