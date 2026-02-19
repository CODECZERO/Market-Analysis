/**
 * Competitors Hook
 * 
 * Manages full lifecycle of competitors data: CRUD, Comparison, Auto-detection.
 */

import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { api } from "@/lib/api";
import type { Competitor, ComparisonData, WeaknessAnalysis } from "@/types/api";

export function useCompetitors() {
    const { brandId } = useParams<{ brandId: string }>();

    // Data state
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [comparison, setComparison] = useState<ComparisonData | null>(null);
    const [selectedWeakness, setSelectedWeakness] = useState<(WeaknessAnalysis & { competitorName?: string }) | null>(null);
    const [loading, setLoading] = useState(true);

    // Modal state
    const [showAddModal, setShowAddModal] = useState(false);
    const [showWeaknessModal, setShowWeaknessModal] = useState(false);
    const [newName, setNewName] = useState("");
    const [newKeywords, setNewKeywords] = useState("");
    const [creating, setCreating] = useState(false);
    const [deleting, setDeleting] = useState<string | null>(null);

    // Auto-detect state
    const [autoDetecting, setAutoDetecting] = useState(false);
    const [suggestedCompetitors, setSuggestedCompetitors] = useState<any[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    useEffect(() => {
        if (brandId) {
            fetchCompetitors();
            fetchComparison();
        }
    }, [brandId]);

    const fetchCompetitors = async () => {
        try {
            const { data } = await api.get(`/api/brands/${brandId}/competitors`);
            setCompetitors(data.data?.competitors || data.competitors || []);
        } catch (error) {
            console.error("Failed to fetch competitors:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchComparison = async () => {
        try {
            const { data } = await api.get(`/api/brands/${brandId}/competitors/comparison`);
            setComparison(data.data || data);
        } catch (error) {
            console.error("Failed to fetch comparison:", error);
        }
    };

    const handleCreate = async (name: string, keywords: string) => {
        if (!name.trim()) return;
        setCreating(true);

        try {
            await api.post(`/api/brands/${brandId}/competitors`, {
                name: name,
                keywords: keywords.split(",").map(k => k.trim()).filter(Boolean),
            });

            setShowAddModal(false);
            setNewName("");
            setNewKeywords("");
            fetchCompetitors();
            fetchComparison();
        } catch (error) {
            console.error("Failed to create competitor:", error);
        } finally {
            setCreating(false);
        }
    };

    const handleDelete = async (competitorId: string) => {
        setDeleting(competitorId);
        try {
            await api.delete(`/api/brands/${brandId}/competitors/${competitorId}`);
            setCompetitors(prev => prev.filter(c => c.id !== competitorId));
            fetchComparison();
        } catch (error) {
            console.error("Failed to delete competitor:", error);
        } finally {
            setDeleting(null);
        }
    };

    const fetchWeakness = async (competitorId: string, competitorName: string) => {
        try {
            const { data } = await api.get(`/api/brands/${brandId}/competitors/${competitorId}/weaknesses`);
            setSelectedWeakness({ ...data, competitorName });
            setShowWeaknessModal(true);
        } catch (error) {
            console.error("Failed to fetch weakness analysis:", error);
        }
    };

    const handleAutoDetect = async () => {
        setAutoDetecting(true);
        setSuggestedCompetitors([]);

        try {
            const { data: firstResponse } = await api.post(`/api/brands/${brandId}/competitors/auto-detect`);

            if (firstResponse.suggestedCompetitors?.length > 0) {
                setSuggestedCompetitors(firstResponse.suggestedCompetitors);
                setShowSuggestions(true);
            } else if (firstResponse.status === "pending") {
                // Poll for results
                let attempts = 0;
                const maxAttempts = 60;
                const pollInterval = 3000;

                const poll = async () => {
                    if (attempts >= maxAttempts) {
                        setAutoDetecting(false);
                        return;
                    }

                    attempts++;
                    await new Promise(resolve => setTimeout(resolve, pollInterval));

                    const { data } = await api.post(`/api/brands/${brandId}/competitors/auto-detect`);
                    if (data.suggestedCompetitors?.length > 0) {
                        setSuggestedCompetitors(data.suggestedCompetitors);
                        setShowSuggestions(true);
                        setAutoDetecting(false);
                    } else if (data.status === "pending") {
                        await poll();
                    }
                };

                await poll();
            }
        } catch (error) {
            console.error("Failed to auto-detect competitors:", error);
        } finally {
            setAutoDetecting(false);
        }
    };

    const handleAddSuggested = async (suggested: any) => {
        setCreating(true);
        try {
            await api.post(`/api/brands/${brandId}/competitors`, {
                name: suggested.name,
                keywords: suggested.keywords || [],
            });
            setSuggestedCompetitors(prev => prev.filter(s => s.name !== suggested.name));
            fetchCompetitors();
            fetchComparison();
        } catch (error) {
            console.error("Failed to add competitor:", error);
        } finally {
            setCreating(false);
        }
    };

    return {
        competitors,
        comparison,
        selectedWeakness,
        loading,
        showAddModal,
        setShowAddModal,
        showWeaknessModal,
        setShowWeaknessModal,
        newName,
        setNewName,
        newKeywords,
        setNewKeywords,
        creating,
        deleting,
        autoDetecting,
        suggestedCompetitors,
        showSuggestions,
        setShowSuggestions,
        fetchWeakness,
        handleCreate,
        handleDelete,
        handleAutoDetect,
        handleAddSuggested,
    };
}
