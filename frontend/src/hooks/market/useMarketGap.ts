/**
 * Market Gap Hook
 * 
 * Manages competitors fetching and market analysis.
 */

import { useState, useEffect } from "react";
import { getCompetitors as fetchCompetitors, getWeaknessAnalysis } from "@/lib/api";
import { useBrands } from "@/hooks/useBrands";
import type { Competitor, WeaknessAnalysis } from "@/types/api";

export function useMarketGap() {
    const { data: brands } = useBrands();
    const activeBrand = brands?.[0];
    const brandId = activeBrand?.slug;

    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);
    const [analysis, setAnalysis] = useState<WeaknessAnalysis | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showManageModal, setShowManageModal] = useState(false);

    const loadCompetitors = async () => {
        if (!brandId) return;
        try {
            const data = await fetchCompetitors(brandId);
            setCompetitors(data.competitors || []);
        } catch (err) {
            console.error("Failed to load competitors", err);
            setError("Failed to load competitor data");
        }
    };

    useEffect(() => {
        if (brandId) loadCompetitors();
    }, [brandId]);

    const analyzeMarket = async () => {
        if (competitors.length === 0) {
            setError("No competitors to analyze. Add competitors first.");
            return;
        }

        setAnalyzing(true);
        setError(null);

        try {
            // Analyze the first competitor for now (demo logic)
            const targetId = competitors[0].id;
            if (!brandId) return;
            const data = await getWeaknessAnalysis(brandId, targetId);
            setAnalysis(data);
        } catch (err) {
            console.error("Analysis failed", err);
            setError("Market analysis failed. Please try again.");
        } finally {
            setAnalyzing(false);
        }
    };

    return {
        competitors,
        selectedCompetitor,
        analysis,
        analyzing,
        error,
        showManageModal,
        setShowManageModal,
        brandId,
        loadCompetitors,
        analyzeMarket,
    };
}
