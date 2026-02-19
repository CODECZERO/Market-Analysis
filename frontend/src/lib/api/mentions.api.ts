/**
 * Mentions API Module
 * 
 * Live mentions and timeline data endpoints
 */

import { api } from "./client";
import type { LiveMentionsResponse } from "@/types/api";

export async function getLiveMentions(
    brand: string,
    params?: { fromDate?: string; toDate?: string }
): Promise<LiveMentionsResponse> {
    const res = await api.get<any>(`/api/brands/${brand}/live`, { params });
    const data = res.data.data || res.data;
    return Array.isArray(data) ? data : (data.mentions || []);
}
