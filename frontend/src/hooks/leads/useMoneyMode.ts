/**
 * Money Mode Hook
 * 
 * Manages leads fetching, status updates, and pitch generation.
 */

import { useState, useEffect } from "react";
import { getLeads, getLeadStats, updateLeadStatus } from "@/lib/api";
import { aiService } from "@/services/ai.service";
import { useBrands } from "@/hooks/useBrands";
import type { Lead, LeadStats } from "@/types/api";

export function useMoneyMode() {
    const { data: brands } = useBrands();
    const activeBrand = brands?.[0];
    const brandId = activeBrand?.slug;

    const [leads, setLeads] = useState<Lead[]>([]);
    const [stats, setStats] = useState<LeadStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
    const [generatingPitch, setGeneratingPitch] = useState(false);
    const [generatedPitch, setGeneratedPitch] = useState<string | null>(null);

    const fetchData = async () => {
        if (!brandId) return;
        setLoading(true);
        setError(null);
        try {
            const [leadsData, statsData] = await Promise.all([
                getLeads(brandId, 50),
                getLeadStats(brandId)
            ]);
            setLeads(leadsData.leads || []);
            setStats(statsData);
        } catch (error) {
            console.error("Failed to fetch money mode data:", error);
            setError("Failed to load opportunities. Please check your connection.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (brandId) fetchData();
    }, [brandId]);

    const generatePitch = async (lead: Lead) => {
        setGeneratingPitch(true);
        setGeneratedPitch(null);
        try {
            const pitch = await aiService.generatePitch(
                brandId || "brand",
                lead.sourceText || "",
                lead.painPoint || ""
            );
            setGeneratedPitch(pitch);
        } catch (error) {
            console.error("Failed to generate pitch:", error);
            setGeneratedPitch("AI service unavailable. Please check your API configuration.");
        } finally {
            setGeneratingPitch(false);
        }
    };

    const updateStatus = async (leadId: string, status: string) => {
        try {
            await updateLeadStatus(leadId, status);
            setLeads((prev) =>
                prev.map((l) => (l.id === leadId ? { ...l, status } : l))
            );
        } catch (error) {
            console.error("Failed to update status:", error);
        }
    };

    const handleSelectLead = (lead: Lead) => {
        setSelectedLead(lead);
        setGeneratedPitch(lead.generatedPitch);
    };

    return {
        leads,
        stats,
        loading,
        error,
        selectedLead,
        generatingPitch,
        generatedPitch,
        fetchData,
        generatePitch,
        updateStatus,
        handleSelectLead,
        brandId,
    };
}
