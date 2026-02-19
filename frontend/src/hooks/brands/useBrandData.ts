/**
 * Brand Data Hooks
 * 
 * Hooks for brand summary, spikes, analytics, mentions, entities, suggestions
 */

import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useSessionAwareQuery } from "@/hooks/core/useSessionAwareQuery";
import {
    getBrandSummary,
    getBrandSpikes,
    getBrandAnalytics,
    getLiveMentions,
    getBrandEntities,
    getBrandSuggestions,
} from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type {
    BrandSummaryResponse,
    BrandSpikesResponse,
    BrandAnalyticsResponse,
    LiveMentionsResponse,
    EntityData,
    SuggestionsResponse,
} from "@/types/api";

export function useBrandSummary(brandId: string) {
    return useSessionAwareQuery<BrandSummaryResponse>({
        queryKey: queryKeys.brandSummary(brandId),
        queryFn: (params) => getBrandSummary(brandId, params),
        enabled: Boolean(brandId),
        refetchInterval: 60_000,
        staleTime: 5 * 60 * 1000,
        gcTime: 24 * 60 * 60 * 1000,
    });
}

export function useBrandSpikes(brandId: string) {
    return useSessionAwareQuery<BrandSpikesResponse>({
        queryKey: queryKeys.brandSpikes(brandId),
        queryFn: (params) => getBrandSpikes(brandId, params),
        enabled: Boolean(brandId),
        refetchInterval: 60_000,
        staleTime: 5 * 60 * 1000,
        gcTime: 24 * 60 * 60 * 1000,
    });
}

export function useBrandAnalytics(brandId: string) {
    return useSessionAwareQuery<BrandAnalyticsResponse>({
        queryKey: queryKeys.analytics(brandId),
        queryFn: (params) => getBrandAnalytics(brandId, params),
        enabled: Boolean(brandId),
        refetchInterval: 60_000,
        staleTime: 5 * 60 * 1000,
        gcTime: 24 * 60 * 60 * 1000,
    });
}

export function useLiveMentions(brandId: string) {
    return useSessionAwareQuery<LiveMentionsResponse>({
        queryKey: queryKeys.liveMentions(brandId),
        queryFn: (params) => getLiveMentions(brandId, params),
        enabled: Boolean(brandId),
        refetchInterval: 10_000,
        staleTime: 2 * 60 * 1000,
        gcTime: 12 * 60 * 60 * 1000,
    });
}

export function useLiveMentionsFiltered(brandId: string, fromDate?: string, toDate?: string) {
    const hasDateFilter = Boolean(fromDate || toDate);

    return useSessionAwareQuery<LiveMentionsResponse>({
        queryKey: [...queryKeys.liveMentions(brandId), fromDate, toDate],
        queryFn: (params) => getLiveMentions(brandId, { ...params, fromDate, toDate }),
        enabled: Boolean(brandId),
        refetchInterval: hasDateFilter ? false : 10_000,
        staleTime: hasDateFilter ? 5 * 60 * 1000 : 2 * 60 * 1000,
        gcTime: 12 * 60 * 60 * 1000,
    });
}

export function useBrandEntities(brandId: string) {
    return useQuery<EntityData>({
        queryKey: queryKeys.entities(brandId),
        queryFn: () => getBrandEntities(brandId),
        enabled: Boolean(brandId),
        refetchInterval: 60_000,
        placeholderData: keepPreviousData,
    });
}

export function useBrandSuggestions(brandId: string) {
    return useQuery<SuggestionsResponse>({
        queryKey: queryKeys.suggestions(brandId),
        queryFn: () => getBrandSuggestions(brandId),
        enabled: Boolean(brandId),
        refetchInterval: 60_000,
        placeholderData: keepPreviousData,
    });
}
