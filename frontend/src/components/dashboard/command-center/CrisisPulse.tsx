import { useMemo } from "react";
import { AlertTriangle, Shield, Activity, TrendingDown, Bell } from "lucide-react";
import { motion } from "framer-motion";

// =============================================================================
// TYPES
// =============================================================================

interface Mention {
    id: string;
    text: string;
    intent: "HOT_LEAD" | "CHURN_RISK" | "BUG_REPORT" | "FEATURE_REQUEST" | "PRAISE" | "GENERAL";
    strategic_tag: "OPPORTUNITY_TO_STEAL" | "CRITICAL_ALERT" | "NONE";
    sentiment_score: number;
    created_at?: string;
}

interface CrisisPulseProps {
    mentions: Mention[];
    isLoading?: boolean;
}

type CrisisLevel = "stable" | "elevated" | "critical";

// =============================================================================
// CRISIS LEVEL CALCULATION
// =============================================================================

function calculateCrisisMetrics(mentions: Mention[]) {
    if (mentions.length === 0) {
        return {
            level: "stable" as CrisisLevel,
            avgSentiment: 0,
            churnCount: 0,
            criticalCount: 0,
            negativePercent: 0,
            score: 0,
        };
    }

    const avgSentiment = mentions.reduce((sum, m) => sum + m.sentiment_score, 0) / mentions.length;
    const churnCount = mentions.filter((m) => m.intent === "CHURN_RISK").length;
    const criticalCount = mentions.filter((m) => m.strategic_tag === "CRITICAL_ALERT").length;
    const negativeCount = mentions.filter((m) => m.sentiment_score < -0.3).length;
    const negativePercent = (negativeCount / mentions.length) * 100;

    const sentimentScore = Math.abs(Math.min(avgSentiment, 0)) * 40;
    const churnScore = Math.min(churnCount * 10, 30);
    const criticalScore = Math.min(criticalCount * 15, 30);
    const score = Math.min(sentimentScore + churnScore + criticalScore, 100);

    let level: CrisisLevel = "stable";
    if (score > 60 || criticalCount > 2) {
        level = "critical";
    } else if (score > 30 || churnCount > 3 || negativePercent > 40) {
        level = "elevated";
    }

    return { level, avgSentiment, churnCount, criticalCount, negativePercent, score };
}

// =============================================================================
// RISK GAUGE COMPONENT
// =============================================================================

function RiskGauge({ score, level }: { score: number; level: CrisisLevel }) {
    const config = {
        stable: { color: "bg-emerald-500", text: "text-emerald-400" },
        elevated: { color: "bg-amber-500", text: "text-amber-400" },
        critical: { color: "bg-rose-500", text: "text-rose-400" },
    };

    const { color, text } = config[level];

    return (
        <div className="flex flex-col items-center w-20">
            <div className={`w-14 h-14 rounded-xl ${color} flex flex-col items-center justify-center text-white mb-3`}>
                <span className="text-xl font-bold">{Math.round(score)}</span>
                <span className="text-[8px] uppercase font-medium opacity-80">Risk</span>
            </div>
            <div className="w-3 h-24 bg-zinc-800 rounded-full overflow-hidden">
                <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: `${score}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className={`${color} w-full rounded-full`}
                    style={{ marginTop: `${100 - score}%` }}
                />
            </div>
        </div>
    );
}

// =============================================================================
// METRIC WIDGET COMPONENT
// =============================================================================

function MetricWidget({
    icon: Icon,
    label,
    value,
    highlight
}: {
    icon: React.ElementType;
    label: string;
    value: string | number;
    highlight?: boolean;
}) {
    return (
        <div className="p-3 rounded-lg bg-zinc-800/30 border border-zinc-800 hover:border-zinc-700 transition-colors">
            <div className="flex items-center gap-1.5 text-zinc-500 mb-1">
                <Icon className="w-3 h-3" />
                <span className="text-[9px] font-medium uppercase tracking-wide">{label}</span>
            </div>
            <div className={`text-lg font-semibold ${highlight ? "text-amber-400" : "text-zinc-200"}`}>
                {value}
            </div>
        </div>
    );
}

// =============================================================================
// CRISIS PULSE COMPONENT
// =============================================================================

export function CrisisPulse({ mentions, isLoading }: CrisisPulseProps) {
    const metrics = useMemo(() => calculateCrisisMetrics(mentions), [mentions]);

    const levelConfig = {
        stable: {
            label: "Stable",
            description: "Sentiment within normal range",
            icon: Shield,
            color: "text-emerald-400",
            bg: "bg-emerald-500/10",
            border: "border-emerald-500/20",
        },
        elevated: {
            label: "Elevated",
            description: "Monitor for potential spikes",
            icon: Activity,
            color: "text-amber-400",
            bg: "bg-amber-500/10",
            border: "border-amber-500/20",
        },
        critical: {
            label: "Critical",
            description: "High risk activity detected",
            icon: AlertTriangle,
            color: "text-rose-400",
            bg: "bg-rose-500/10",
            border: "border-rose-500/20",
        },
    };

    const config = levelConfig[metrics.level];
    const StatusIcon = config.icon;

    if (isLoading) {
        return (
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 h-full flex items-center justify-center">
                <div className="flex flex-col items-center gap-3">
                    <Activity className="w-6 h-6 text-zinc-600 animate-pulse" />
                    <p className="text-xs text-zinc-500">Calibrating...</p>
                </div>
            </div>
        );
    }

    if (mentions.length === 0) {
        return (
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 h-full flex items-center justify-center">
                <div className="flex flex-col items-center gap-3 text-center p-6">
                    <Shield className="w-8 h-8 text-zinc-700" />
                    <div>
                        <p className="text-sm font-semibold text-zinc-400">No Crisis Data</p>
                        <p className="text-xs text-zinc-500 mt-1">Not enough mentions to assess risk.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`rounded-xl border ${config.border} bg-zinc-900/50 overflow-hidden`}>
            {/* Header */}
            <div className="p-4 border-b border-zinc-800">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg ${config.bg} flex items-center justify-center`}>
                            <StatusIcon className={`w-4 h-4 ${config.color}`} />
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-white">Crisis Monitor</h3>
                            <p className="text-[11px] text-zinc-500">Real-time risk assessment</p>
                        </div>
                    </div>
                    <div className={`px-2.5 py-1 rounded ${config.bg} border ${config.border}`}>
                        <span className={`text-[10px] font-semibold uppercase tracking-wide ${config.color}`}>
                            {config.label}
                        </span>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="p-4">
                <div className="flex gap-4">
                    {/* Gauge */}
                    <RiskGauge score={metrics.score} level={metrics.level} />

                    {/* Metrics */}
                    <div className="flex-1 space-y-3">
                        {/* Status */}
                        <div className="mb-4">
                            <p className="text-[10px] text-zinc-500 uppercase tracking-wide mb-1">Status</p>
                            <p className="text-sm text-white font-medium">{config.description}</p>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-2 gap-2">
                            <MetricWidget
                                icon={Activity}
                                label="Sentiment"
                                value={`${(metrics.avgSentiment * 100).toFixed(0)}%`}
                                highlight={metrics.avgSentiment < -0.3}
                            />
                            <MetricWidget
                                icon={TrendingDown}
                                label="Negativity"
                                value={`${metrics.negativePercent.toFixed(0)}%`}
                                highlight={metrics.negativePercent > 40}
                            />
                            <MetricWidget
                                icon={AlertTriangle}
                                label="Churn Risk"
                                value={metrics.churnCount}
                                highlight={metrics.churnCount > 0}
                            />
                            <MetricWidget
                                icon={Bell}
                                label="Critical"
                                value={metrics.criticalCount}
                                highlight={metrics.criticalCount > 0}
                            />
                        </div>
                    </div>
                </div>

                {/* Footer Insight */}
                <div className="mt-4 p-3 rounded-lg bg-zinc-800/30 border border-zinc-800">
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                        {metrics.level === "critical" && "Immediate intervention recommended. Negative sentiment is trending across multiple channels."}
                        {metrics.level === "elevated" && "Risk factors identified. Review negative mentions in the feed to prevent escalation."}
                        {metrics.level === "stable" && "Brand reputation is healthy. No significant threats detected in the last 24 hours."}
                    </p>
                </div>
            </div>
        </div>
    );
}

export default CrisisPulse;
