/**
 * Pitch Generator Component
 */

import { motion } from "framer-motion";
import { Sparkles, MessageSquare, Copy, Check, Zap } from "lucide-react";
import { useState } from "react";
import { TypewriterText } from "@/components/shared/TypewriterText";
import type { Lead } from "@/types/api";

interface PitchGeneratorProps {
    selectedLead: Lead | null;
    generatingPitch: boolean;
    generatedPitch: string | null;
    onGenerate: (lead: Lead) => void;
}

export function PitchGenerator({
    selectedLead,
    generatingPitch,
    generatedPitch,
    onGenerate,
}: PitchGeneratorProps) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        if (generatedPitch) {
            navigator.clipboard.writeText(generatedPitch);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="lg:col-span-1">
            <div className="sticky top-6">
                <div className="bg-zinc-900/30 backdrop-blur-xl rounded-2xl border border-zinc-800/50 p-1 max-h-[calc(100vh-2rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                    <div className="p-5">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                                <Sparkles className="w-4 h-4 text-indigo-400" />
                            </div>
                            Sales Assistant
                            <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse ml-auto" />
                        </h2>

                        {selectedLead ? (
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="space-y-4"
                            >
                                {/* Selected Lead Info */}
                                <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-6 h-6 rounded-md bg-emerald-500/20 flex items-center justify-center">
                                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                                        </div>
                                        <span className="text-xs font-medium text-emerald-400">Lead Selected</span>
                                    </div>
                                    <p className="text-xs text-zinc-400 line-clamp-2">
                                        {selectedLead.sourceText?.slice(0, 100)}...
                                    </p>
                                </div>

                                {/* Pain Point */}
                                <div className="p-3 rounded-xl bg-zinc-900/50 border border-zinc-800">
                                    <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-medium">Identified Pain Point</span>
                                    <p className="text-sm text-zinc-300 mt-1.5 leading-relaxed">
                                        {selectedLead.painPoint || "No specific pain point identified"}
                                    </p>
                                </div>

                                {/* Generate Button */}
                                <div className="relative">
                                    <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl opacity-20 blur" />
                                    <button
                                        onClick={() => onGenerate(selectedLead)}
                                        disabled={generatingPitch}
                                        className="relative w-full py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-medium text-white transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2"
                                    >
                                        {generatingPitch ? (
                                            <>
                                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                <span>Generating Pitch...</span>
                                            </>
                                        ) : (
                                            <>
                                                <Zap className="w-4 h-4" />
                                                <span>Generate Strategy & Pitch</span>
                                            </>
                                        )}
                                    </button>
                                </div>

                                {/* Generated Pitch */}
                                {generatedPitch && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="bg-zinc-800/30 rounded-xl border border-zinc-700/30 overflow-hidden"
                                    >
                                        <div className="px-3 py-2 bg-zinc-900/50 border-b border-zinc-700/30 flex justify-between items-center">
                                            <span className="text-xs font-medium text-zinc-400 flex items-center gap-1.5">
                                                <MessageSquare className="w-3 h-3" />
                                                AI Draft
                                            </span>
                                            <button
                                                onClick={handleCopy}
                                                className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
                                            >
                                                {copied ? (
                                                    <>
                                                        <Check className="w-3 h-3" />
                                                        Copied!
                                                    </>
                                                ) : (
                                                    <>
                                                        <Copy className="w-3 h-3" />
                                                        Copy
                                                    </>
                                                )}
                                            </button>
                                        </div>
                                        <div className="p-3">
                                            <TypewriterText text={generatedPitch} />
                                        </div>
                                    </motion.div>
                                )}
                            </motion.div>
                        ) : (
                            <div className="py-10 text-center">
                                <div className="w-14 h-14 rounded-2xl bg-zinc-800/50 border-2 border-dashed border-zinc-700 flex items-center justify-center mx-auto mb-4">
                                    <Sparkles className="w-6 h-6 text-zinc-600" />
                                </div>
                                <h3 className="text-zinc-300 font-medium mb-1">Select a Lead</h3>
                                <p className="text-xs text-zinc-500 max-w-[200px] mx-auto">
                                    Click on any lead card to activate the AI Sales Assistant
                                </p>
                                <div className="mt-4 flex items-center justify-center gap-1.5 text-[10px] text-zinc-600">
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-500/50 animate-pulse" />
                                    <span>AI ready and waiting</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

