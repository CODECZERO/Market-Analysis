import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { api } from "@/lib/api";

export interface WebSource {
    url: string;
    title: string;
    source_name: string;
    snippet: string;
}

export interface WebAnalysis {
    summary: string;
    sentiment: "positive" | "neutral" | "negative" | "mixed";
    key_themes: string[];
    notable_mentions: Array<{
        source: string;
        highlight: string;
        sentiment: string;
    }>;
    opportunities: string[];
    risks: string[];
    recommended_actions: string[];
}

export interface WebInsightsData {
    brand: string;
    status: "pending" | "complete" | "error";
    message?: string;
    sources: WebSource[];
    analysis: WebAnalysis;
    cached: boolean;
    generated_at: string;
}

export function useWebInsights() {
    const { brandId } = useParams<{ brandId: string }>();
    const [data, setData] = useState<WebInsightsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [minTimeElapsed, setMinTimeElapsed] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedAction, setSelectedAction] = useState<string | null>(null);

    useEffect(() => {
        if (!brandId) return;

        const fetchInsights = async () => {
            try {
                const res = await api.get(`/api/brands/${brandId}/web-insights`);
                setData(res.data);
            } catch (err: any) {
                console.error("Failed to fetch web insights:", err);
                setError(err.message || "Failed to fetch web insights");
            } finally {
                setLoading(false);
            }
        };

        fetchInsights();
    }, [brandId]);

    const handleTerminalComplete = () => {
        setMinTimeElapsed(true);
    };

    return {
        brandId,
        data,
        loading,
        error,
        minTimeElapsed,
        selectedAction,
        setSelectedAction,
        handleTerminalComplete
    };
}
