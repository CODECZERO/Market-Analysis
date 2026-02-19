/**
 * Executive Summary Card Component
 */

import { motion } from "framer-motion";
import { FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WebAnalysis } from "@/hooks/insights/useWebInsights";

interface ExecutiveSummaryCardProps {
    analysis: WebAnalysis;
}

const sentimentColors = {
    positive: "text-green-400 bg-green-500/10 border-green-500/20",
    neutral: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
    negative: "text-red-400 bg-red-500/10 border-red-500/20",
    mixed: "text-orange-400 bg-orange-500/10 border-orange-500/20",
};

export function ExecutiveSummaryCard({ analysis }: ExecutiveSummaryCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
        >
            <Card className="bg-zinc-900/50 border-zinc-800 overflow-hidden relative">
                <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-lg flex items-center gap-2">
                            <FileText className="w-5 h-5 text-zinc-400" />
                            Executive Summary
                        </CardTitle>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${sentimentColors[analysis.sentiment]}`}>
                            {analysis.sentiment.toUpperCase()}
                        </span>
                    </div>
                </CardHeader>
                <CardContent>
                    <p className="text-zinc-300 leading-relaxed text-lg">{analysis.summary}</p>

                    <div className="mt-6 flex flex-wrap gap-2">
                        {analysis.key_themes.map((theme, idx) => (
                            <span
                                key={idx}
                                className="px-3 py-1 bg-zinc-800 text-zinc-300 rounded-md text-sm border border-zinc-700"
                            >
                                #{theme}
                            </span>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
