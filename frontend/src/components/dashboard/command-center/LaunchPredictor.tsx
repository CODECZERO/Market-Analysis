import { useMemo } from "react";
import { Sparkles, TrendingUp, TrendingDown, AlertTriangle, Rocket } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// =============================================================================
// TYPES
// =============================================================================

interface LaunchData {
    is_launch: boolean;
    product_name: string;
    success_score: number;
    reason: string;
    brand: string;
    is_competitor: boolean;
    reception: {
        hype_signals: string[];
        skepticism_signals: string[];
        overall: string;
    };
}

interface LaunchPredictorProps {
    myLaunch?: LaunchData | null;
    competitorLaunch?: LaunchData | null;
    isLoading?: boolean;
}

// =============================================================================
// SUCCESS METER (Circular Progress)
// =============================================================================

function SuccessMeter({
    score,
    label,
    productName,
    isCompetitor = false
}: {
    score: number;
    label: string;
    productName: string;
    isCompetitor?: boolean;
}) {
    const circumference = 2 * Math.PI * 45; // r = 45
    const strokeDashoffset = circumference - (score / 100) * circumference;

    const getColorClass = (score: number) => {
        if (score >= 71) return { stroke: "stroke-emerald-500", text: "text-emerald-400", glow: "drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]" };
        if (score >= 40) return { stroke: "stroke-amber-500", text: "text-amber-400", glow: "drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]" };
        return { stroke: "stroke-red-500", text: "text-red-400", glow: "drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]" };
    };

    const getPredictionLabel = (score: number) => {
        if (score >= 71) return "POTENTIAL HIT";
        if (score >= 40) return "MODERATE SUCCESS";
        return "FLOP RISK";
    };

    const colors = getColorClass(score);

    return (
        <div className="flex flex-col items-center">
            {/* Label */}
            <p className={`text-xs font-medium mb-2 ${isCompetitor ? "text-purple-400" : "text-emerald-400"}`}>
                {label}
            </p>

            {/* Circular Progress */}
            <div className="relative w-32 h-32">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    {/* Background circle */}
                    <circle
                        cx="50"
                        cy="50"
                        r="45"
                        strokeWidth="8"
                        fill="none"
                        className="stroke-zinc-800"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="50"
                        cy="50"
                        r="45"
                        strokeWidth="8"
                        fill="none"
                        strokeLinecap="round"
                        className={`${colors.stroke} ${colors.glow} transition-all duration-1000`}
                        style={{
                            strokeDasharray: circumference,
                            strokeDashoffset,
                        }}
                    />
                </svg>

                {/* Score in center */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-3xl font-bold ${colors.text}`}>{score}</span>
                    <span className="text-xs text-zinc-500">/100</span>
                </div>
            </div>

            {/* Product Name */}
            <p className="text-sm font-semibold text-white mt-2 text-center max-w-[120px] truncate">
                {productName || "Unknown Product"}
            </p>

            {/* Prediction Label */}
            <p className={`text-[10px] font-medium mt-1 ${colors.text}`}>
                {getPredictionLabel(score)}
            </p>
        </div>
    );
}

// =============================================================================
// RECEPTION SIGNALS
// =============================================================================

function ReceptionSignals({ hype, skepticism }: { hype: string[]; skepticism: string[] }) {
    if (hype.length === 0 && skepticism.length === 0) {
        return null;
    }

    return (
        <div className="grid grid-cols-2 gap-4 mt-4">
            {/* Hype Signals */}
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                <p className="text-[10px] uppercase tracking-wide text-emerald-500 mb-1">Hype Signals</p>
                <div className="flex flex-wrap gap-1">
                    {hype.slice(0, 3).map((signal, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                            {signal}
                        </span>
                    ))}
                    {hype.length === 0 && <span className="text-[10px] text-zinc-500">None detected</span>}
                </div>
            </div>

            {/* Skepticism Signals */}
            <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20">
                <p className="text-[10px] uppercase tracking-wide text-red-500 mb-1">Skepticism</p>
                <div className="flex flex-wrap gap-1">
                    {skepticism.slice(0, 3).map((signal, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300">
                            {signal}
                        </span>
                    ))}
                    {skepticism.length === 0 && <span className="text-[10px] text-zinc-500">None detected</span>}
                </div>
            </div>
        </div>
    );
}

// =============================================================================
// LAUNCH PREDICTOR COMPONENT
// =============================================================================

export function LaunchPredictor({ myLaunch, competitorLaunch, isLoading }: LaunchPredictorProps) {
    // Generate strategic insight
    const insight = useMemo(() => {
        if (!myLaunch?.is_launch && !competitorLaunch?.is_launch) {
            return null;
        }

        if (myLaunch?.is_launch && competitorLaunch?.is_launch) {
            const scoreDiff = myLaunch.success_score - competitorLaunch.success_score;
            if (scoreDiff > 20) {
                return {
                    text: "Market prefers your launch. Competitor facing resistance.",
                    type: "positive" as const,
                };
            } else if (scoreDiff < -20) {
                return {
                    text: "Competitor launch has stronger reception. Consider counter-strategy.",
                    type: "negative" as const,
                };
            }
            return {
                text: "Both launches receiving similar reception. Monitor closely.",
                type: "neutral" as const,
            };
        }

        if (myLaunch?.is_launch) {
            if (myLaunch.success_score >= 71) {
                return { text: "Your launch is gaining strong traction! Capitalize on momentum.", type: "positive" as const };
            }
            if (myLaunch.success_score >= 40) {
                return { text: "Your launch has moderate reception. Consider additional marketing.", type: "neutral" as const };
            }
            return { text: "Your launch is receiving mixed signals. Address concerns quickly.", type: "negative" as const };
        }

        if (competitorLaunch?.is_launch) {
            if (competitorLaunch.success_score >= 71) {
                return { text: "Competitor launch is trending. Prepare competitive response.", type: "warning" as const };
            }
            return { text: "Competitor launched but reception is weak. Opportunity to differentiate.", type: "positive" as const };
        }

        return null;
    }, [myLaunch, competitorLaunch]);

    const insightConfig = {
        positive: { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-400" },
        negative: { bg: "bg-red-500/10", border: "border-red-500/30", text: "text-red-400" },
        neutral: { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-400" },
        warning: { bg: "bg-purple-500/10", border: "border-purple-500/30", text: "text-purple-400" },
    };

    // Only show loading if we have NO data yet
    if (isLoading && !myLaunch && !competitorLaunch) {
        return (
            <Card className="border-zinc-800 bg-zinc-900/50">
                <CardContent className="flex items-center justify-center h-48">
                    <div className="animate-pulse text-zinc-500 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 animate-spin" />
                        The Oracle is analyzing launches...
                    </div>
                </CardContent>
            </Card>
        );
    }

    // No launches detected
    if (!myLaunch?.is_launch && !competitorLaunch?.is_launch) {
        return (
            <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-indigo-950/20">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-bold flex items-center gap-2">
                        <Sparkles className="w-6 h-6 text-indigo-400" />
                        The Oracle
                        <span className="text-xs font-normal text-zinc-500">Launch Predictor</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col items-center justify-center py-8 text-center">
                        <Rocket className="w-12 h-12 text-zinc-700 mb-3" />
                        <p className="text-sm text-zinc-500">No launches detected</p>
                        <p className="text-xs text-zinc-600 mt-1">The Oracle will predict success when launches are announced</p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-indigo-950/20">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-bold flex items-center gap-2">
                        <Sparkles className="w-6 h-6 text-indigo-400" />
                        The Oracle
                        <span className="text-xs font-normal text-zinc-500">Launch Predictor</span>
                    </CardTitle>
                    <Sparkles className="w-5 h-5 text-indigo-400 animate-pulse" />
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Strategic Insight */}
                {insight && (
                    <div className={`p-3 rounded-lg border ${insightConfig[insight.type].bg} ${insightConfig[insight.type].border}`}>
                        <p className={`text-sm font-medium ${insightConfig[insight.type].text}`}>
                            {insight.text}
                        </p>
                    </div>
                )}

                {/* Side-by-Side Meters */}
                <div className="flex items-center justify-around py-4">
                    {/* My Launch */}
                    {myLaunch?.is_launch ? (
                        <SuccessMeter
                            score={myLaunch.success_score}
                            label="My Launch"
                            productName={myLaunch.product_name}
                            isCompetitor={false}
                        />
                    ) : (
                        <div className="flex flex-col items-center opacity-50">
                            <div className="w-32 h-32 rounded-full bg-zinc-800 flex items-center justify-center">
                                <span className="text-zinc-600 text-sm">No Launch</span>
                            </div>
                            <p className="text-xs text-zinc-600 mt-2">My Brand</p>
                        </div>
                    )}

                    {/* VS Divider */}
                    <div className="flex flex-col items-center">
                        <span className="text-lg font-bold text-zinc-600">VS</span>
                    </div>

                    {/* Competitor Launch */}
                    {competitorLaunch?.is_launch ? (
                        <SuccessMeter
                            score={competitorLaunch.success_score}
                            label="Competitor Launch"
                            productName={competitorLaunch.product_name}
                            isCompetitor={true}
                        />
                    ) : (
                        <div className="flex flex-col items-center opacity-50">
                            <div className="w-32 h-32 rounded-full bg-zinc-800 flex items-center justify-center">
                                <span className="text-zinc-600 text-sm">No Launch</span>
                            </div>
                            <p className="text-xs text-zinc-600 mt-2">Competitor</p>
                        </div>
                    )}
                </div>

                {/* Reception Signals (for active launch) */}
                {myLaunch?.is_launch && (
                    <ReceptionSignals
                        hype={myLaunch.reception.hype_signals}
                        skepticism={myLaunch.reception.skepticism_signals}
                    />
                )}

                {/* Reason */}
                {(myLaunch?.is_launch || competitorLaunch?.is_launch) && (
                    <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700">
                        <p className="text-xs text-zinc-400">
                            <span className="font-semibold text-indigo-400">Oracle Insight:</span>{" "}
                            {myLaunch?.is_launch ? myLaunch.reason : competitorLaunch?.reason}
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

export default LaunchPredictor;
