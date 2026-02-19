/**
 * Live Header Component
 */

import { motion } from "framer-motion";
import { Filter, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LiveHeaderProps {
    showFilters: boolean;
    onToggleFilters: () => void;
    onRefresh: () => void;
    isFetching: boolean;
    hasActiveFilters: boolean;
}

export function LiveHeader({
    showFilters,
    onToggleFilters,
    onRefresh,
    isFetching,
    hasActiveFilters
}: LiveHeaderProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-wrap items-center justify-between gap-4"
        >
            <div className="flex items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        Live Mentions
                    </h1>
                    <p className="text-zinc-400 mt-1 flex items-center gap-2">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        {hasActiveFilters ? "Filtered by date" : "Real-time monitoring • Auto-refreshes every 10s"}
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <Button
                    variant="outline"
                    size="sm"
                    className={`border-zinc-700 bg-zinc-800/50 hover:bg-zinc-700 gap-2 ${showFilters ? 'bg-zinc-700' : ''}`}
                    onClick={onToggleFilters}
                >
                    <Filter className="h-4 w-4" />
                    Filter
                </Button>
                <Button
                    onClick={onRefresh}
                    disabled={isFetching}
                    size="sm"
                    className="bg-blue-600 hover:bg-blue-500 gap-2"
                >
                    <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
                    {isFetching ? 'Refreshing...' : 'Refresh Now'}
                </Button>
            </div>
        </motion.div>
    );
}
