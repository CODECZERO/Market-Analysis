/**
 * Competitors Page - Manage and Analyze Competitors
 * 
 * Full CRUD for competitors + Share of Voice and Sentiment comparison charts.
 * Refactored to use extracted SRP-compliant components.
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Swords, Target, Search, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

import {
    ShareOfVoiceChart,
    SentimentComparisonChart,
    SuggestedCompetitors,
    CompetitorsList,
    AddCompetitorModal,
    WeaknessAnalysisModal,
} from "@/components/competitors";

import { useCompetitors } from "@/hooks/competitors";

export default function CompetitorsPage() {
    const {
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
    } = useCompetitors();

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-6 pb-24"
        >
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20">
                            <Swords className="w-6 h-6 text-purple-400" />
                        </div>
                        Competitor Intelligence
                    </h1>
                    <p className="text-zinc-400 mt-2 ml-1">Track, analyze, and benchmark against competitors</p>
                </div>
                <div className="flex gap-3">
                    <Link to="/market-gap">
                        <Button variant="outline" className="gap-2 bg-zinc-900 border-zinc-700 text-zinc-300 hover:bg-zinc-800">
                            <Target className="w-4 h-4" />
                            Market Gap
                        </Button>
                    </Link>
                    <Button
                        onClick={handleAutoDetect}
                        disabled={autoDetecting}
                        variant="outline"
                        className="gap-2 bg-zinc-900 border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
                    >
                        {autoDetecting ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="hidden sm:inline">Detecting...</span>
                            </>
                        ) : (
                            <>
                                <Search className="w-4 h-4" />
                                <span className="hidden sm:inline">Auto-Detect AI</span>
                            </>
                        )}
                    </Button>
                    <Button onClick={() => setShowAddModal(true)} className="gap-2 bg-purple-600 hover:bg-purple-500 text-white">
                        <Plus className="w-4 h-4" />
                        <span className="hidden sm:inline">Add Competitor</span>
                    </Button>
                </div>
            </div>

            {/* Charts Section */}
            {comparison && (comparison.shareOfVoice?.length > 0 || comparison.sentimentComparison?.length > 0) && (
                <div className="grid lg:grid-cols-2 gap-6">
                    <ShareOfVoiceChart data={comparison.shareOfVoice || []} />
                    <SentimentComparisonChart data={comparison.sentimentComparison || []} />
                </div>
            )}

            {/* AI Suggested Competitors */}
            {showSuggestions && suggestedCompetitors.length > 0 && (
                <SuggestedCompetitors
                    suggestions={suggestedCompetitors}
                    onClose={() => setShowSuggestions(false)}
                    onAdd={handleAddSuggested}
                    isAdding={creating}
                />
            )}

            {/* Competitors List */}
            <CompetitorsList
                competitors={competitors}
                loading={loading}
                deletingId={deleting}
                onAnalyze={fetchWeakness}
                onDelete={handleDelete}
                onAddFirst={() => setShowAddModal(true)}
            />

            {/* Add Competitor Modal */}
            <AddCompetitorModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                onSubmit={handleCreate}
                isCreating={creating}
                name={newName}
                setName={setNewName}
                keywords={newKeywords}
                setKeywords={setNewKeywords}
            />

            {/* Weakness Analysis Modal */}
            <WeaknessAnalysisModal
                isOpen={showWeaknessModal}
                onClose={() => setShowWeaknessModal(false)}
                analysis={selectedWeakness}
            />
        </motion.div>
    );
}
