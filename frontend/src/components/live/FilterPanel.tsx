/**
 * Filter Panel Component
 */

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

interface FilterPanelProps {
    filters: {
        fromDate: string; setFromDate: (v: string) => void;
        fromTime: string; setFromTime: (v: string) => void;
        toDate: string; setToDate: (v: string) => void;
        toTime: string; setToTime: (v: string) => void;
        clear: () => void;
    };
    onApply: () => void;
}

export function FilterPanel({ filters, onApply }: FilterPanelProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="flex flex-wrap items-center gap-2 px-3 py-2 bg-zinc-900/60 border border-zinc-800/80 rounded-md backdrop-blur-sm"
        >
            <span className="text-xs text-zinc-500 font-medium">From:</span>
            <input
                type="date"
                value={filters.fromDate}
                onChange={(e) => filters.setFromDate(e.target.value)}
                className="h-7 px-2 text-xs bg-zinc-800/80 border border-zinc-700/50 rounded text-zinc-300 focus:outline-none focus:border-blue-500/50"
            />
            <input
                type="time"
                value={filters.fromTime}
                onChange={(e) => filters.setFromTime(e.target.value)}
                className="h-7 w-20 px-2 text-xs bg-zinc-800/80 border border-zinc-700/50 rounded text-zinc-300 focus:outline-none focus:border-blue-500/50"
            />
            <span className="text-zinc-600">→</span>
            <span className="text-xs text-zinc-500 font-medium">To:</span>
            <input
                type="date"
                value={filters.toDate}
                onChange={(e) => filters.setToDate(e.target.value)}
                className="h-7 px-2 text-xs bg-zinc-800/80 border border-zinc-700/50 rounded text-zinc-300 focus:outline-none focus:border-blue-500/50"
            />
            <input
                type="time"
                value={filters.toTime}
                onChange={(e) => filters.setToTime(e.target.value)}
                className="h-7 w-20 px-2 text-xs bg-zinc-800/80 border border-zinc-700/50 rounded text-zinc-300 focus:outline-none focus:border-blue-500/50"
            />
            <Button
                variant="ghost"
                size="sm"
                onClick={filters.clear}
                className="h-7 px-2 text-xs text-zinc-500 hover:text-zinc-300"
            >
                Clear
            </Button>
            <Button
                size="sm"
                onClick={onApply}
                className="h-7 px-3 text-xs bg-blue-600/80 hover:bg-blue-500"
            >
                Apply
            </Button>
        </motion.div>
    );
}
