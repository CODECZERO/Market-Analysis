/**
 * Live Page Hook
 * 
 * Manages state and logic for the Live Mentions page.
 */

import { useState } from "react";
import { useParams } from "react-router-dom";
import { useLiveMentionsFiltered } from "@/hooks/brands";

export function useLivePage() {
    const { brandId = "" } = useParams<{ brandId: string }>();

    // Date + Time filter state
    const [fromDate, setFromDate] = useState<string>("");
    const [fromTime, setFromTime] = useState<string>("00:00");
    const [toDate, setToDate] = useState<string>("");
    const [toTime, setToTime] = useState<string>("23:59");
    const [showFilters, setShowFilters] = useState(false);

    // Combine date + time into ISO strings for API
    const fromDateTime = fromDate ? `${fromDate}T${fromTime}:00` : undefined;
    const toDateTime = toDate ? `${toDate}T${toTime}:59` : undefined;

    const {
        data: mentions = [],
        isLoading,
        isError,
        error,
        refetch,
        isFetching
    } = useLiveMentionsFiltered(brandId, fromDateTime, toDateTime);

    const clearFilters = () => {
        setFromDate("");
        setFromTime("00:00");
        setToDate("");
        setToTime("23:59");
    };

    return {
        brandId,
        mentions,
        isLoading,
        isError,
        error,
        refetch,
        isFetching,
        filters: {
            fromDate, setFromDate,
            fromTime, setFromTime,
            toDate, setToDate,
            toTime, setToTime,
            show: showFilters,
            toggle: () => setShowFilters(!showFilters),
            clear: clearFilters
        }
    };
}
