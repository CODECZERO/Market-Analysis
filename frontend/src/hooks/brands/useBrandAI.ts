/**
 * Brand AI Hooks
 * 
 * Hooks for AI-powered features: trends, influencers, launches
 */

import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { getBrandTrends, getBrandInfluencers, getBrandLaunches } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { TrendPrediction, InfluencersResponse, LaunchesResponse } from "@/types/api";

export function useBrandTrends(brandId: string) {
    return useQuery<TrendPrediction>({
        queryKey: queryKeys.trends(brandId),
        queryFn: () => getBrandTrends(brandId),
        enabled: Boolean(brandId),
        refetchInterval: 120_000,
        placeholderData: keepPreviousData,
    });
}

export function useBrandInfluencers(brandId: string) {
    return useQuery<InfluencersResponse>({
        queryKey: queryKeys.influencers(brandId),
        queryFn: () => getBrandInfluencers(brandId),
        enabled: Boolean(brandId),
        refetchInterval: 60_000,
        placeholderData: keepPreviousData,
    });
}

export function useBrandLaunches(brandId: string) {
    return useQuery<LaunchesResponse>({
        queryKey: ["launches", brandId],
        queryFn: () => getBrandLaunches(brandId),
        enabled: Boolean(brandId),
        refetchInterval: 120_000,
        placeholderData: keepPreviousData,
    });
}
