import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Plus, Sparkles, Loader2, Check, AlertCircle } from "lucide-react";
import { addCompetitor, autoDetectCompetitors } from "@/lib/api";

interface CompetitorManagementModalProps {
    brandId: string;
    onClose: () => void;
    onCompetitorAdded: () => void;
}

interface SuggestedCompetitor {
    name: string;
    keywords: string[];
    confidence: number;
    reason: string;
}

export function CompetitorManagementModal({ brandId, onClose, onCompetitorAdded }: CompetitorManagementModalProps) {
    const [activeTab, setActiveTab] = useState<"manual" | "auto">("manual");

    // Manual form state
    const [name, setName] = useState("");
    const [keywords, setKeywords] = useState("");
    const [adding, setAdding] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Auto-detect state
    const [detecting, setDetecting] = useState(false);
    const [suggestions, setSuggestions] = useState<SuggestedCompetitor[]>([]);
    const [addedSuggestions, setAddedSuggestions] = useState<Set<string>>(new Set());

    const handleManualAdd = async () => {
        if (!name.trim()) {
            setError("Competitor name is required");
            return;
        }

        setAdding(true);
        setError(null);

        try {
            const keywordArray = keywords.split(",").map(k => k.trim()).filter(Boolean);
            await addCompetitor(brandId, {
                name: name.trim(),
                keywords: keywordArray.length > 0 ? keywordArray : [name.toLowerCase()],
                sources: ["reddit", "x", "news"],
                enabled: true
            });

            setName("");
            setKeywords("");
            onCompetitorAdded();
        } catch (err: any) {
            setError(err.response?.data?.message || "Failed to add competitor");
        } finally {
            setAdding(false);
        }
    };

    const handleAutoDetect = async () => {
        setDetecting(true);
        setError(null);
        setSuggestions([]);

        try {
            const result = await autoDetectCompetitors(brandId);
            setSuggestions(result.suggestedCompetitors || []);
        } catch (err: any) {
            setError(err.response?.data?.message || "Failed to detect competitors");
        } finally {
            setDetecting(false);
        }
    };

    const handleAddSuggestion = async (suggestion: SuggestedCompetitor) => {
        try {
            await addCompetitor(brandId, {
                name: suggestion.name,
                keywords: suggestion.keywords,
                sources: ["reddit", "x", "news"],
                enabled: true
            });

            setAddedSuggestions(prev => new Set(prev).add(suggestion.name));
            onCompetitorAdded();
        } catch (err) {
            console.error("Failed to add suggestion:", err);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-zinc-900 rounded-2xl border border-zinc-800 w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl"
            >
                {/* Header */}
                <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-white">Manage Competitors</h2>
                        <p className="text-sm text-zinc-400 mt-1">Add competitors manually or let AI find them</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-zinc-400" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-zinc-800 px-6">
                    <button
                        onClick={() => setActiveTab("manual")}
                        className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === "manual"
                            ? "text-blue-400 border-blue-400"
                            : "text-zinc-500 border-transparent hover:text-zinc-300"
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <Plus className="w-4 h-4" />
                            Manual Entry
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab("auto")}
                        className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === "auto"
                            ? "text-blue-400 border-blue-400"
                            : "text-zinc-500 border-transparent hover:text-zinc-300"
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4" />
                            AI Auto-Detect
                        </div>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    <AnimatePresence mode="wait">
                        {activeTab === "manual" ? (
                            <motion.div
                                key="manual"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                className="space-y-4"
                            >
                                <div>
                                    <label className="block text-sm font-medium text-zinc-300 mb-2">
                                        Competitor Name *
                                    </label>
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="e.g., Microsoft"
                                        className="w-full px-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-zinc-300 mb-2">
                                        Keywords (comma-separated)
                                    </label>
                                    <input
                                        type="text"
                                        value={keywords}
                                        onChange={(e) => setKeywords(e.target.value)}
                                        placeholder="e.g., microsoft, windows, azure"
                                        className="w-full px-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                    <p className="text-xs text-zinc-500 mt-1.5">
                                        If left empty, will use competitor name as keyword
                                    </p>
                                </div>

                                {error && (
                                    <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                                        <AlertCircle className="w-4 h-4 shrink-0" />
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handleManualAdd}
                                    disabled={adding || !name.trim()}
                                    className="w-full px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium text-white transition-all flex items-center justify-center gap-2"
                                >
                                    {adding ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Adding...
                                        </>
                                    ) : (
                                        <>
                                            <Plus className="w-4 h-4" />
                                            Add Competitor
                                        </>
                                    )}
                                </button>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="auto"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-4"
                            >
                                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                                    <p className="text-sm text-blue-200">
                                        Our AI will analyze your brand and suggest relevant competitors based on industry, keywords, and market presence.
                                    </p>
                                </div>

                                <button
                                    onClick={handleAutoDetect}
                                    disabled={detecting}
                                    className="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium text-white transition-all flex items-center justify-center gap-2"
                                >
                                    {detecting ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Detecting Competitors...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-4 h-4" />
                                            Detect Competitors with AI
                                        </>
                                    )}
                                </button>

                                {error && (
                                    <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                                        <AlertCircle className="w-4 h-4 shrink-0" />
                                        {error}
                                    </div>
                                )}

                                {suggestions.length > 0 && (
                                    <div className="space-y-3 mt-6">
                                        <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">
                                            Suggested Competitors ({suggestions.length})
                                        </h3>
                                        {suggestions.map((suggestion, idx) => (
                                            <motion.div
                                                key={suggestion.name}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: idx * 0.05 }}
                                                className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-4"
                                            >
                                                <div className="flex items-start justify-between gap-4">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <h4 className="font-semibold text-white">{suggestion.name}</h4>
                                                            <span className="px-2 py-0.5 bg-blue-500/20 border border-blue-500/30 rounded text-xs font-medium text-blue-300">
                                                                {Math.round(suggestion.confidence * 100)}% match
                                                            </span>
                                                        </div>
                                                        <p className="text-sm text-zinc-400 mb-2">{suggestion.reason}</p>
                                                        <div className="flex flex-wrap gap-1.5">
                                                            {suggestion.keywords.slice(0, 5).map((kw) => (
                                                                <span
                                                                    key={kw}
                                                                    className="px-2 py-0.5 bg-zinc-700 rounded text-xs text-zinc-300"
                                                                >
                                                                    {kw}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => handleAddSuggestion(suggestion)}
                                                        disabled={addedSuggestions.has(suggestion.name)}
                                                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-green-600 disabled:cursor-not-allowed rounded-lg text-sm font-medium text-white transition-all flex items-center gap-1.5"
                                                    >
                                                        {addedSuggestions.has(suggestion.name) ? (
                                                            <>
                                                                <Check className="w-3.5 h-3.5" />
                                                                Added
                                                            </>
                                                        ) : (
                                                            <>
                                                                <Plus className="w-3.5 h-3.5" />
                                                                Add
                                                            </>
                                                        )}
                                                    </button>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </div>
    );
}
