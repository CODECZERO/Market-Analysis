import { SuggestionsResponse } from "@/types/api";
import { Lightbulb, Info, Check } from "lucide-react";
import { motion } from "framer-motion";

interface SuggestionsFeedProps {
    data: SuggestionsResponse | null | undefined;
    isLoading: boolean;
}

export function SuggestionsFeed({ data, isLoading }: SuggestionsFeedProps) {
    if (isLoading) {
        return (
            <div className="h-full bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex items-center justify-center">
                <div className="flex flex-col items-center gap-2">
                    <div className="w-5 h-5 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin" />
                    <p className="text-xs text-zinc-500">Generating suggestions...</p>
                </div>
            </div>
        );
    }

    const suggestions = data?.suggestions || [];

    if (suggestions.length === 0) {
        return (
            <div className="h-full bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col items-center justify-center text-center">
                <div className="w-10 h-10 rounded-full bg-zinc-800/50 flex items-center justify-center mb-3">
                    <Info className="w-5 h-5 text-zinc-500" />
                </div>
                <p className="text-sm text-zinc-400 font-medium">No suggestions yet</p>
                <p className="text-xs text-zinc-600 mt-1 max-w-[200px]">
                    Actionable insights will appear here as we analyze more data.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden h-full flex flex-col">
            <div className="p-4 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-10 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
                    <Lightbulb className="w-4 h-4 text-amber-500" />
                    Smart Suggestions
                </h3>
                <span className="text-[10px] bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded-full font-medium">
                    {suggestions.length} available
                </span>
            </div>

            <div className="overflow-y-auto custom-scrollbar p-4 flex-1">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 items-start">
                    {suggestions.map((item, i) => {
                        // Safely extract suggestion text
                        const suggestionText = typeof item.suggestion === 'string'
                            ? item.suggestion
                            : (item.suggestion as any)?.text || (item.suggestion as any)?.name || JSON.stringify(item.suggestion);

                        return (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.03 }}
                                className="group p-4 rounded-xl bg-zinc-800/40 hover:bg-zinc-800/70 border border-zinc-800/50 hover:border-blue-500/30 transition-all cursor-default min-h-[90px] flex flex-col"
                            >
                                <div className="flex items-start gap-4 flex-1">
                                    <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center group-hover:from-blue-500/30 group-hover:to-purple-500/30 transition-colors">
                                        <Check className="w-4 h-4 text-blue-400" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm text-zinc-300 group-hover:text-zinc-100 leading-relaxed transition-colors" title={suggestionText}>
                                            {suggestionText}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 mt-3 pt-3 border-t border-zinc-700/30">
                                    <span className="text-xs text-zinc-500 font-medium bg-zinc-800/50 px-2 py-1 rounded">
                                        Mentioned {item.count}×
                                    </span>
                                    {item.count > 2 && (
                                        <span className="text-xs bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 px-2 py-1 rounded font-medium">
                                            🔥 Trending
                                        </span>
                                    )}
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
