/**
 * AI Matching Step Component
 * 
 * Third step of onboarding - AI tuning configuration
 */

import { motion } from "framer-motion";
import { Label } from "@/components/ui/label";
import { KeywordInput } from "@/components/shared/KeywordInput";
import type { BrandMatchConfig } from "@/types/api";

const INDUSTRIES = [
    { value: "tech", label: "Technology / SaaS" },
    { value: "ecommerce", label: "E-commerce / Retail" },
    { value: "finance", label: "Finance / Fintech" },
    { value: "healthcare", label: "Healthcare" },
    { value: "food", label: "Food & Beverage" },
    { value: "automotive", label: "Automotive" },
    { value: "gaming", label: "Gaming" },
    { value: "social", label: "Social Media" },
    { value: "", label: "Other / Not Listed" },
];

interface MatchingStepProps {
    matchConfig: BrandMatchConfig;
    setMatchConfig: React.Dispatch<React.SetStateAction<BrandMatchConfig>>;
}

export function MatchingStep({ matchConfig, setMatchConfig }: MatchingStepProps) {
    return (
        <motion.div
            key="matching"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">AI Tuning</h2>
                <p className="text-zinc-400">Help us find your brand more accurately.</p>
            </div>

            {/* Industry Selector */}
            <div className="space-y-2">
                <Label className="text-zinc-300">Industry (helps filter false positives)</Label>
                <select
                    value={matchConfig.industry || ""}
                    onChange={(e) => setMatchConfig(prev => ({ ...prev, industry: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-zinc-100"
                >
                    {INDUSTRIES.map(ind => (
                        <option key={ind.value} value={ind.value}>{ind.label}</option>
                    ))}
                </select>
            </div>

            {/* Misspellings / Aliases */}
            <div className="space-y-2">
                <Label className="text-zinc-300">Common Misspellings (optional)</Label>
                <p className="text-xs text-zinc-500">Add typos people often make, e.g. "Amazn", "Gogle"</p>
                <KeywordInput
                    value={matchConfig.misspellings || []}
                    onChange={(val) => setMatchConfig(prev => ({ ...prev, misspellings: val }))}
                    placeholder="Type and press Enter..."
                />
            </div>

            {/* Exclude Keywords */}
            <div className="space-y-2">
                <Label className="text-zinc-300">Exclude Keywords (optional)</Label>
                <p className="text-xs text-zinc-500">Words that indicate false positives, e.g. "recipe" for Apple</p>
                <KeywordInput
                    value={matchConfig.excludeKeywords || []}
                    onChange={(val) => setMatchConfig(prev => ({ ...prev, excludeKeywords: val }))}
                    placeholder="Type and press Enter..."
                />
            </div>

            {/* Fuzzy Threshold Slider */}
            <div className="space-y-2">
                <Label className="text-zinc-300">Typo Detection Sensitivity</Label>
                <div className="flex items-center gap-4">
                    <span className="text-xs text-zinc-500">Strict</span>
                    <input
                        type="range"
                        min="0.6"
                        max="0.95"
                        step="0.05"
                        value={matchConfig.fuzzyThreshold || 0.8}
                        onChange={(e) => setMatchConfig(prev => ({ ...prev, fuzzyThreshold: parseFloat(e.target.value) }))}
                        className="flex-1 accent-blue-500"
                    />
                    <span className="text-xs text-zinc-500">Flexible</span>
                    <span className="text-sm text-zinc-400 w-12 text-right">
                        {((matchConfig.fuzzyThreshold || 0.8) * 100).toFixed(0)}%
                    </span>
                </div>
            </div>
        </motion.div>
    );
}

export { INDUSTRIES };
