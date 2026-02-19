import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import {
    Lightbulb,
    AlertTriangle,
    TrendingUp,
    CheckCircle2,
    ChevronDown,
    BrainCircuit
} from "lucide-react";
import { BrandSummaryResponse } from "../../types/api";

interface BusinessInsightsCardProps {
    summary?: BrandSummaryResponse | null;
}

export const BusinessInsightsCard: React.FC<BusinessInsightsCardProps> = ({ summary }) => {
    const [expandedSection, setExpandedSection] = useState<string | null>("actions");

    const hasData = summary && (
        (summary.feature_requests?.length || 0) > 0 ||
        (summary.pain_points?.length || 0) > 0 ||
        (summary.churn_risks?.length || 0) > 0 ||
        (summary.recommended_actions?.length || 0) > 0
    );

    // If no data, show a "Waiting for Intelligence" state instead of nothing
    if (!hasData) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative overflow-hidden rounded-2xl border border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl p-6 text-center"
            >
                <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-zinc-800/50 flex items-center justify-center animate-pulse">
                        <BrainCircuit className="w-8 h-8 text-zinc-600" />
                    </div>
                    <div>
                        <h3 className="text-lg font-medium text-white">Strategic Intelligence Initializing</h3>
                        <p className="text-sm text-zinc-500 mt-1 max-w-sm mx-auto">
                            Our AI is analyzing your brand mentions to extract leads, risks, and feature requests. This may take a few minutes.
                        </p>
                    </div>
                </div>
            </motion.div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="relative overflow-hidden rounded-2xl border border-zinc-800/50 bg-gradient-to-br from-indigo-900/10 via-zinc-900/50 to-zinc-900/80 backdrop-blur-xl p-0.5"
        >
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:20px_20px]" />
            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] -z-10" />

            <div className="bg-zinc-950/40 rounded-[15px] p-4 h-full">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shadow-lg shadow-indigo-500/5">
                            <BrainCircuit className="w-5 h-5 text-indigo-400" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white tracking-tight">Strategic Intelligence</h2>
                            <div className="flex items-center gap-2 mt-1">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                <p className="text-xs font-medium text-emerald-400 uppercase tracking-wider">AI Analysis Active</p>
                            </div>
                        </div>
                    </div>

                    {/* Lead Score Radial */}
                    {summary?.avgLeadScore && summary.avgLeadScore > 0 && (
                        <div className="flex items-center gap-4 bg-white/5 rounded-xl p-2 pr-4 border border-white/5">
                            <div className="relative w-12 h-12 flex items-center justify-center">
                                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                                    <path className="text-zinc-700" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                                    <path className="text-emerald-400" strokeDasharray={`${summary.avgLeadScore}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                                </svg>
                                <span className="absolute text-xs font-bold text-white">{summary.avgLeadScore}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-zinc-400 uppercase font-bold tracking-wider">Lead Score</span>
                                <span className="text-sm font-medium text-white">High Potential</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Grid Layout */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InsightCard
                        title="Recommended Actions"
                        icon={CheckCircle2}
                        color="emerald"
                        items={summary?.recommended_actions}
                        delay={0.1}
                    />

                    <InsightCard
                        title="Feature Requests"
                        icon={Lightbulb}
                        color="amber"
                        items={summary?.feature_requests}
                        delay={0.2}
                    />

                    <InsightCard
                        title="Pain Points"
                        icon={AlertTriangle}
                        color="rose"
                        items={summary?.pain_points}
                        delay={0.3}
                    />

                    <InsightCard
                        title="Churn Risks"
                        icon={TrendingUp}
                        color="orange"
                        items={summary?.churn_risks}
                        delay={0.4}
                    />
                </div>
            </div>
        </motion.div>
    );
};

const InsightCard: React.FC<{
    title: string;
    icon: any;
    color: string;
    items?: string[];
    delay: number;
}> = ({ title, icon: Icon, color, items, delay }) => {
    if (!items || items.length === 0) return null;

    const colors: Record<string, any> = {
        emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20", hover: "group-hover:border-emerald-500/30" },
        amber: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20", hover: "group-hover:border-amber-500/30" },
        rose: { bg: "bg-rose-500/10", text: "text-rose-400", border: "border-rose-500/20", hover: "group-hover:border-rose-500/30" },
        orange: { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/20", hover: "group-hover:border-orange-500/30" },
    };

    const theme = colors[color];

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.4 }}
            className={`group bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 hover:bg-zinc-900/80 transition-all duration-300 ${theme.hover}`}
        >
            <div className="flex items-center gap-2 mb-3">
                <div className={`w-8 h-8 rounded-lg ${theme.bg} ${theme.border} border flex items-center justify-center`}>
                    <Icon className={`w-4 h-4 ${theme.text}`} />
                </div>
                <h3 className="font-semibold text-zinc-200 text-sm">{title}</h3>
                <span className="ml-auto text-xs px-2 py-1 rounded-full bg-zinc-800 text-zinc-500 font-mono">
                    {items.length}
                </span>
            </div>

            <ul className="space-y-3">
                {items.slice(0, 4).map((item, idx) => (
                    <li key={idx} className="flex gap-3 text-sm group/item">
                        <div className={`mt-1.5 w-1.5 h-1.5 rounded-full ${theme.bg.replace('/10', '/40')} shrink-0 group-hover/item:bg-${color}-400 transition-colors`} />
                        <span className="text-zinc-400 leading-relaxed group-hover/item:text-zinc-200 transition-colors">
                            {item}
                        </span>
                    </li>
                ))}
            </ul>
        </motion.div>
    );
};
