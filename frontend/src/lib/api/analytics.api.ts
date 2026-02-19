/**
 * Analytics API Module
 * 
 * AI features, trends, influencers, and launch predictions
 */

import { api } from "./client";
import type { TrendPrediction, InfluencersResponse, LaunchesResponse } from "@/types/api";

// ============================================================================
// TRENDS & INFLUENCERS
// ============================================================================

export async function getBrandTrends(brandId: string): Promise<TrendPrediction> {
    const res = await api.get<any>(`/api/brands/${brandId}/trends`);
    return res.data.data || res.data;
}

export async function getBrandInfluencers(brandId: string): Promise<InfluencersResponse> {
    const res = await api.get<any>(`/api/brands/${brandId}/influencers`);
    return res.data.data || res.data;
}

// ============================================================================
// LAUNCH PREDICTIONS (The Oracle)
// ============================================================================

export async function getBrandLaunches(brandId: string): Promise<LaunchesResponse> {
    const res = await api.get<any>(`/api/brands/${brandId}/launches`);
    return res.data.data || res.data;
}

// ============================================================================
// MARKET STATS & COMPARISON
// ============================================================================

import type {
    CompetitorComparisonResponse,
    MarketShareTrendResponse,
    StatsSummaryResponse
} from "@/types/api";

export async function getCompetitorComparison(timeframe: string = "24h"): Promise<CompetitorComparisonResponse> {
    const res = await api.get<any>(`/api/stats/competitor-comparison`, {
        params: { timeframe },
    });
    return res.data.data || res.data;
}

export async function getMarketShareTrend(days: number = 7): Promise<MarketShareTrendResponse> {
    const res = await api.get<any>(`/api/stats/market-share-trend`, {
        params: { days },
    });
    return res.data.data || res.data;
}

export async function getStatsSummary(): Promise<StatsSummaryResponse> {
    const res = await api.get<any>(`/api/stats/summary`);
    const data = res.data.data || res.data;
    // StatsSummaryResponse has total_mentions_24h etc.
    // If data.summary exists and is object, return it.
    return (data.summary && typeof data.summary === 'object') ? data.summary : data;
}
