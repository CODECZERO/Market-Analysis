/**
 * Leads API Module (Money Mode)
 * 
 * Sales leads and opportunity tracking endpoints
 */

import { api } from "./client";
import type { LeadsListResponse, LeadStats } from "@/types/api";

export async function getLeads(brandId: string, limit = 20): Promise<LeadsListResponse> {
    const res = await api.get<any>(`/api/brands/${brandId}/leads?limit=${limit}`);
    return res.data.data || res.data;
}

export async function getLeadStats(brandId: string): Promise<LeadStats> {
    const res = await api.get<any>(`/api/brands/${brandId}/leads/stats`);
    return res.data.data || res.data;
}

export async function generatePitch(leadId: string): Promise<{ pitch: string }> {
    const res = await api.post<any>(`/api/v1/leads/${leadId}/generate-pitch`);
    return res.data.data || res.data;
}

export async function updateLeadStatus(leadId: string, status: string): Promise<void> {
    await api.patch(`/api/v1/leads/${leadId}/status`, { status });
}
