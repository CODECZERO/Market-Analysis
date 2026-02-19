/**
 * AI Suggested Competitors Panel
 * 
 * Shows AI-detected competitor suggestions with add functionality
 */

import { Search, X, Plus, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface SuggestedCompetitor {
    name: string;
    reason: string;
    keywords?: string[];
    confidence?: number;
}

interface SuggestedCompetitorsProps {
    suggestions: SuggestedCompetitor[];
    onClose: () => void;
    onAdd: (suggestion: SuggestedCompetitor) => void;
    isAdding: boolean;
}

export function SuggestedCompetitors({ suggestions, onClose, onAdd, isAdding }: SuggestedCompetitorsProps) {
    if (!suggestions || suggestions.length === 0) return null;

    return (
        <Card className="border-blue-500/30 bg-blue-500/5">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
                <CardTitle className="text-base font-semibold text-blue-400 flex items-center gap-2">
                    <Search className="w-5 h-5" />
                    AI-Detected Competitors
                </CardTitle>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onClose}
                    className="text-zinc-500 hover:text-white"
                >
                    <X className="w-4 h-4" />
                </Button>
            </CardHeader>
            <CardContent className="space-y-3">
                {suggestions.map((suggested, index) => (
                    <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-zinc-900/50 rounded-lg border border-zinc-800"
                    >
                        <div>
                            <h4 className="font-medium text-white">{suggested.name}</h4>
                            <p className="text-xs text-zinc-500 mt-1">{suggested.reason}</p>
                            <div className="flex gap-1 mt-2">
                                {suggested.keywords?.slice(0, 3).map((kw, i) => (
                                    <Badge key={i} variant="secondary" className="bg-zinc-800 text-zinc-400 text-xs">
                                        {kw}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-zinc-500">
                                {Math.round((suggested.confidence || 0.8) * 100)}% match
                            </span>
                            <Button
                                size="sm"
                                onClick={() => onAdd(suggested)}
                                disabled={isAdding}
                                className="bg-blue-600 hover:bg-blue-500 text-white"
                            >
                                {isAdding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                            </Button>
                        </div>
                    </div>
                ))}
            </CardContent>
        </Card>
    );
}
