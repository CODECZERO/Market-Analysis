/**
 * Competitors API Module
 * 
 * Competitor management and analysis endpoints
 */

import { api } from "./client";
import type { CompetitorsListResponse, WeaknessAnalysis } from "@/types/api";

export async function getCompetitors(brandId: string): Promise<CompetitorsListResponse> {
    const res = await api.get<any>(`/api/brands/${brandId}/competitors`);
    return res.data.data || res.data;
}

export async function getWeaknessAnalysis(brandId: string, competitorId: string): Promise<WeaknessAnalysis> {
    const res = await api.get<any>(`/api/brands/${brandId}/competitors/${competitorId}/weaknesses`);
    return res.data.data || res.data;
}

export async function addCompetitor(brandId: string, data: {
    name: string;
    keywords: string[];
    sources: string[];
    enabled: boolean;
}): Promise<any> {
    const res = await api.post(`/api/brands/${brandId}/competitors`, data);
    return res.data.data || res.data;
}

export async function autoDetectCompetitors(brandId: string): Promise<{
    suggestedCompetitors: Array<{
        name: string;
        keywords: string[];
        confidence: number;
        reason: string;
    }>;
}> {
    const res = await api.post(`/api/brands/${brandId}/competitors/auto-detect`);
    return res.data.data || res.data;
}
