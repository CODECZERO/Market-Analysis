import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, BarChart3 } from "lucide-react";
import type { TrendPrediction } from "@/types/api";

interface TrendChartProps {
    trend: TrendPrediction | null;
    isLoading?: boolean;
}

export function TrendChart({ trend, isLoading }: TrendChartProps) {
    if (isLoading) {
        return (
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 animate-pulse">
                <div className="h-5 bg-zinc-800 rounded w-1/3 mb-3" />
                <div className="h-20 bg-zinc-800 rounded" />
            </div>
        );
    }

    if (!trend) {
        return (
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                    <BarChart3 className="w-4 h-4 text-purple-400" />
                    <h3 className="text-sm font-semibold text-white">Trend Prediction</h3>
                </div>
                <p className="text-zinc-400 text-sm">Insufficient data to predict trends.</p>
            </div>
        );
    }

    const getTrendIcon = () => {
        switch (trend.trend) {
            case "improving":
                return <TrendingUp className="w-8 h-8 text-emerald-400" />;
            case "declining":
                return <TrendingDown className="w-8 h-8 text-red-400" />;
            default:
                return <Minus className="w-8 h-8 text-yellow-400" />;
        }
    };

    const getTrendColor = () => {
        switch (trend.trend) {
            case "improving":
                return "from-emerald-500/20 to-emerald-500/5 border-emerald-500/30";
            case "declining":
                return "from-red-500/20 to-red-500/5 border-red-500/30";
            default:
                return "from-yellow-500/20 to-yellow-500/5 border-yellow-500/30";
        }
    };

    const getTrendLabel = () => {
        switch (trend.trend) {
            case "improving":
                return "Improving";
            case "declining":
                return "Declining";
            default:
                return "Stable";
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 bg-gradient-to-br ${getTrendColor()}`}
        >
            <div className="flex items-center gap-2 mb-3">
                <BarChart3 className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-semibold text-white">Trend Prediction</h3>
            </div>

            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                    {getTrendIcon()}
                    <div>
                        <p className="text-xl font-bold text-white">{getTrendLabel()}</p>
                        <p className="text-xs text-zinc-400">
                            {trend.percentChange > 0 ? "+" : ""}
                            {trend.percentChange}% change
                        </p>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-xs text-zinc-400">Confidence</p>
                    <p className="text-base font-semibold text-white">
                        {Math.round(trend.confidence * 100)}%
                    </p>
                </div>
            </div>

            <div className="bg-black/20 rounded-lg p-3 max-h-[80px] overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                <p className="text-xs text-zinc-300 whitespace-pre-wrap">{trend.prediction}</p>
            </div>

            {/* Confidence bar */}
            <div className="mt-3">
                <div className="flex justify-between text-[10px] text-zinc-500 mb-1">
                    <span>Low</span>
                    <span>High</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${trend.confidence * 100}%` }}
                        transition={{ delay: 0.3, duration: 0.5 }}
                        className={`h-full rounded-full ${trend.trend === "improving"
                            ? "bg-emerald-400"
                            : trend.trend === "declining"
                                ? "bg-red-400"
                                : "bg-yellow-400"
                            }`}
                    />
                </div>
            </div>
        </motion.div>
    );
}
