/**
 * Session-Aware Query Hook
 * 
 * Wraps React Query's useQuery to handle first-load historical data fetching.
 * When a user returns after logout, this hook automatically fetches data from
 * their logout time to present.
 */

import { useQuery, type UseQueryOptions, type QueryKey } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { getSessionInfo, getTimeRange, markSessionLoaded, getTimeSinceLogout } from '@/lib/sessionTracker';

interface TimeRangeParams {
    fromDate?: string;
    toDate?: string;
}

type QueryFnWithTimeRange<T> = (params?: TimeRangeParams) => Promise<T>;

interface SessionAwareQueryOptions<T> extends Omit<UseQueryOptions<T>, 'queryKey' | 'queryFn'> {
    queryKey: QueryKey;
    queryFn: QueryFnWithTimeRange<T>;
    enableHistoricalLoad?: boolean;
}

export function useSessionAwareQuery<T>({
    queryKey,
    queryFn,
    enableHistoricalLoad = true,
    ...restOptions
}: SessionAwareQueryOptions<T>) {
    const [hasLoadedHistory, setHasLoadedHistory] = useState(false);
    const [showHistoryToast, setShowHistoryToast] = useState(false);

    const sessionInfo = getSessionInfo();
    const timeRange = getTimeRange();

    const shouldFetchHistory =
        enableHistoricalLoad &&
        sessionInfo?.isFirstLoad &&
        sessionInfo?.logoutTime &&
        !hasLoadedHistory &&
        timeRange !== null;

    const effectiveQueryKey = shouldFetchHistory
        ? [...queryKey, 'historical', sessionInfo.logoutTime]
        : queryKey;

    useEffect(() => {
        if (shouldFetchHistory && !showHistoryToast) {
            const timeSince = getTimeSinceLogout();
            if (timeSince) {
                console.info(`Loading updates from ${timeSince} ago...`);
                setShowHistoryToast(true);
            }
        }
    }, [shouldFetchHistory, showHistoryToast]);

    const query = useQuery({
        queryKey: effectiveQueryKey,
        queryFn: async () => {
            if (shouldFetchHistory && timeRange) {
                const data = await queryFn(timeRange);
                setHasLoadedHistory(true);
                markSessionLoaded();
                return data;
            }
            return queryFn();
        },
        ...restOptions,
    });

    return {
        ...query,
        isLoadingHistory: shouldFetchHistory && query.isLoading,
    };
}

export function useSessionTimeRange() {
    const sessionInfo = getSessionInfo();
    const timeRange = getTimeRange();

    return {
        timeRange: sessionInfo?.isFirstLoad ? timeRange : null,
        sessionInfo,
        timeSinceLogout: getTimeSinceLogout(),
    };
}
