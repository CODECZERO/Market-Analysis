/**
 * Brands API Module
 * 
 * All brand-related API endpoints
 */

import { api, isWaitingResponse } from "./client";
import type {
    BrandListResponse,
    CreateBrandRequest,
    CreateBrandResponse,
    BrandDetailResponse,
    DeleteBrandResponse,
    BrandSummaryResponse,
    BrandSpikesResponse,
    BrandAnalyticsResponse,
    EntityData,
    SuggestionsResponse,
} from "@/types/api";

// ============================================================================
// BRAND CRUD
// ============================================================================

export async function getBrands(): Promise<BrandListResponse> {
    const MAX_WAIT_ATTEMPTS = 10;
    const WAIT_RETRY_DELAY = 3000;

    for (let attempt = 0; attempt < MAX_WAIT_ATTEMPTS; attempt++) {
        const res = await api.get<any>("/api/brands");

        // Handle wrapped response
        const data = res.data.data || res.data.brands || res.data;

        if (isWaitingResponse(data)) {
            console.log(`[API] Backend processing... ${data.message}`);
            await new Promise((r) => setTimeout(r, WAIT_RETRY_DELAY));
            continue;
        }

        return Array.isArray(data) ? data : (data.brands || []);
    }

    throw new Error("Backend is still processing after maximum wait attempts");
}

export async function createBrand(payload: CreateBrandRequest): Promise<CreateBrandResponse> {
    // Backend expects { brand: "string" } where brand is the brand name
    const backendPayload = {
        brand: payload.brandName,
    };
    const res = await api.post<any>("/api/brands/set", backendPayload);
    return res.data.data || res.data;
}

export async function getBrand(slug: string): Promise<BrandDetailResponse> {
    const res = await api.get<any>(`/api/brands/${slug}`);
    return res.data.data || res.data;
}

export async function deleteBrand(brand: string): Promise<DeleteBrandResponse> {
    const res = await api.delete<any>(`/api/brands/${brand}`);
    return res.data.data || res.data;
}

// ============================================================================
// BRAND DATA (Summary, Spikes, Analytics)
// ============================================================================

export async function getBrandSummary(
    brand: string,
    params?: { fromDate?: string; toDate?: string }
): Promise<BrandSummaryResponse> {
    const res = await api.get<any>(`/api/brands/${brand}/summary`, { params });
    const data = res.data.data || res.data;
    // Check if wrapped in 'summary' property but distinguish from 'summary' string field
    // BrandSummaryResponse has 'brand', 'clusters', etc.
    // If data.summary is an object and has 'brand', it might be the wrapper.
    // Safest: check if data matches interface. If not, try data.summary.
    if (data.brand && data.clusters) return data;
    return data.summary && typeof data.summary === 'object' && !Array.isArray(data.summary) ? data.summary : data;
}

export async function getBrandSpikes(
    brand: string,
    params?: { fromDate?: string; toDate?: string }
): Promise<BrandSpikesResponse> {
    const res = await api.get<any>(`/api/brands/${brand}/spikes`, { params });
    const data = res.data.data || res.data;
    return data.spikes || data; // Unwrap if wrapped in 'spikes'
}

export async function getBrandAnalytics(
    brand: string,
    params?: { fromDate?: string; toDate?: string }
): Promise<BrandAnalyticsResponse> {
    const res = await api.get<any>(`/api/brands/${brand}/analytics`, { params });
    const data = res.data.data || res.data;
    return data.analytics || data; // Unwrap if wrapped in 'analytics'
}

// ============================================================================
// ENTITIES & SUGGESTIONS
// ============================================================================

export async function getBrandEntities(brandId: string): Promise<EntityData> {
    const res = await api.get<any>(`/api/brands/${brandId}/entities`);
    return res.data.data || res.data;
}

export async function getBrandSuggestions(brandId: string): Promise<SuggestionsResponse> {
    const res = await api.get<any>(`/api/brands/${brandId}/suggestions`);
    return res.data.data || res.data;
}
