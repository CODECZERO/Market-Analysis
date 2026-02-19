import { motion } from "framer-motion";
import { BarChart3 } from "lucide-react";

interface ComparisonData {
    name: string;
    value: number;
    color: string;
}

interface ComparisonChartProps {
    title: string;
    data: ComparisonData[];
    maxValue?: number;
    isLoading?: boolean;
}

export function ComparisonChart({ title, data, maxValue, isLoading }: ComparisonChartProps) {
    if (isLoading) {
        return (
            <div className="glass-card p-6 rounded-xl animate-pulse">
                <div className="h-5 bg-white/10 rounded w-1/3 mb-6" />
                <div className="space-y-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="space-y-2">
                            <div className="h-4 bg-white/10 rounded w-1/4" />
                            <div className="h-6 bg-white/10 rounded" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (!data?.length) {
        return (
            <div className="glass-card p-6 rounded-xl border border-white/10 text-center">
                <BarChart3 className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400">No comparison data available.</p>
            </div>
        );
    }

    const max = maxValue || Math.max(...data.map(d => d.value), 1);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 rounded-xl border border-white/10"
        >
            <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">{title}</h3>
            </div>

            <div className="space-y-4">
                {data.map((item, index) => (
                    <motion.div
                        key={item.name}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-gray-300">{item.name}</span>
                            <span className="text-sm font-semibold text-white">{item.value.toLocaleString()}</span>
                        </div>
                        <div className="h-4 bg-white/10 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${(item.value / max) * 100}%` }}
                                transition={{ delay: 0.3 + index * 0.1, duration: 0.5 }}
                                className="h-full rounded-full"
                                style={{ backgroundColor: item.color }}
                            />
                        </div>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
}

// Market share variant with percentages
interface MarketShareChartProps {
    data: ComparisonData[];
    isLoading?: boolean;
}

export function MarketShareChart({ data, isLoading }: MarketShareChartProps) {
    if (isLoading) {
        return (
            <div className="glass-card p-6 rounded-xl animate-pulse">
                <div className="h-5 bg-white/10 rounded w-1/3 mb-6" />
                <div className="flex gap-2 h-8 mb-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="flex-1 bg-white/10 rounded" />
                    ))}
                </div>
            </div>
        );
    }

    if (!data?.length) {
        return (
            <div className="glass-card p-6 rounded-xl border border-white/10 text-center">
                <BarChart3 className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400">No market share data available.</p>
            </div>
        );
    }

    const total = data.reduce((sum, item) => sum + item.value, 0) || 1;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 rounded-xl border border-white/10"
        >
            <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Market Share</h3>
            </div>

            {/* Stacked bar */}
            <div className="flex h-8 rounded-full overflow-hidden mb-6">
                {data.map((item, index) => (
                    <motion.div
                        key={item.name}
                        initial={{ width: 0 }}
                        animate={{ width: `${(item.value / total) * 100}%` }}
                        transition={{ delay: 0.2 + index * 0.1, duration: 0.5 }}
                        className="h-full"
                        style={{ backgroundColor: item.color }}
                        title={`${item.name}: ${((item.value / total) * 100).toFixed(1)}%`}
                    />
                ))}
            </div>

            {/* Legend */}
            <div className="grid grid-cols-2 gap-3">
                {data.map((item) => (
                    <div key={item.name} className="flex items-center gap-2">
                        <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sm text-gray-300 truncate">{item.name}</span>
                        <span className="text-sm font-semibold text-white ml-auto">
                            {((item.value / total) * 100).toFixed(0)}%
                        </span>
                    </div>
                ))}
            </div>
        </motion.div>
    );
}
