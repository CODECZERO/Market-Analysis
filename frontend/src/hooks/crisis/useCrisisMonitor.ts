/**
 * Crisis Monitor Hook
 * 
 * Manages fetching and updating of crisis metrics and alerts.
 */

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useBrands } from "@/hooks/useBrands";
import type { CrisisMetrics, AlertEvent, VelocityPoint } from "@/components/crisis";

export function useCrisisMonitor() {
    const { data: brands } = useBrands();
    const activeBrand = brands?.[0];
    const brandId = activeBrand?.slug;

    const [metrics, setMetrics] = useState<CrisisMetrics>({
        riskScore: 0,
        severity: "normal",
        velocityMultiplier: 1,
        sentimentIntensity: 0,
        mentionCount: 0,
        reasons: [],
    });
    const [alerts, setAlerts] = useState<AlertEvent[]>([]);
    const [velocityData, setVelocityData] = useState<VelocityPoint[]>([]);
    const [isLive, setIsLive] = useState(true);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchCrisisData = async () => {
        try {
            if (!brandId) return;

            // Fetch metrics
            const metricsRes = await api.get(`/api/v1/crisis/metrics`);
            if (metricsRes.data) {
                const data = metricsRes.data;
                setMetrics({
                    riskScore: data.riskScore ?? 0,
                    severity: data.severity ?? "normal",
                    velocityMultiplier: data.velocityMultiplier ?? 1,
                    sentimentIntensity: data.sentimentIntensity ?? 0,
                    mentionCount: data.mentionCount ?? 0,
                    reasons: data.reasons ?? [],
                });
            }

            // Fetch events
            const eventsRes = await api.get(`/api/v1/crisis/events`);
            if (eventsRes.data && Array.isArray(eventsRes.data)) {
                setAlerts(eventsRes.data.map((e: any) => ({
                    id: e.id,
                    monitorId: e.monitorId,
                    riskScore: e.riskScore,
                    severity: e.severity,
                    triggeredReasons: e.triggeredReasons || [],
                    recommendedAction: e.recommendedAction || "Monitor closely",
                    createdAt: e.createdAt,
                    isResolved: e.isResolved,
                })));
            }

            setError(null);
        } catch (err: any) {
            console.error("Failed to fetch crisis data:", err);
            setError("Unable to load crisis data");
        } finally {
            setLoading(false);
        }
    };

    const resolveAlert = async (alertId: string) => {
        try {
            api.patch(`/api/v1/crisis/events/${alertId}/resolve`)
                .catch(e => console.warn("Resolve API not implemented yet", e));
            setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, isResolved: true } : a));
        } catch (err) {
            console.error("Failed to resolve alert:", err);
        }
    };

    // Initial fetch
    useEffect(() => {
        if (brandId) fetchCrisisData();
        else if (brands && brands.length === 0) {
            setLoading(false);
            setError("No brands found. create a brand first.");
        }
    }, [brandId, brands]);

    // Polling
    useEffect(() => {
        if (!isLive || !brandId) return;
        const interval = setInterval(() => fetchCrisisData(), 30000);
        return () => clearInterval(interval);
    }, [isLive, brandId]);

    // Generate velocity data based on metrics (deterministic, not random)
    // This will show flat baseline when no activity, or scaled based on actual mention count
    useEffect(() => {
        const now = Date.now();
        const baseRate = metrics.mentionCount > 0 ? metrics.mentionCount / 60 : 0;
        const sentimentValue = metrics.sentimentIntensity > 0.5 ? -0.3 : 0.2;

        // Create deterministic data points - more recent = higher activity when there's data
        const data: VelocityPoint[] = Array.from({ length: 30 }, (_, i) => {
            // Scale factor: more recent points get higher weight
            const recencyFactor = i / 29; // 0 to 1
            const rate = baseRate > 0 ? baseRate * (0.5 + recencyFactor * 0.5) : 0;

            return {
                timestamp: new Date(now - (30 - i) * 60000).toISOString(),
                mentionsPerMinute: rate,
                sentiment: sentimentValue,
            };
        });
        setVelocityData(data);
    }, [metrics.mentionCount, metrics.sentimentIntensity]);

    return {
        metrics,
        alerts,
        velocityData,
        isLive,
        setIsLive,
        loading,
        error,
        resolveAlert,
        refetch: fetchCrisisData
    };
}
