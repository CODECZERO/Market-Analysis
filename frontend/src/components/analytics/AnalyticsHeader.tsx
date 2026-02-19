/**
 * Analytics Header Component
 */

import { motion } from "framer-motion";
import { BarChart3 } from "lucide-react";

export function AnalyticsHeader() {
    return (
        <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-indigo-500" />
            </div>
            <div>
                <h1 className="text-2xl font-semibold text-white">
                    Analytics Dashboard
                </h1>
                <p className="text-sm text-zinc-400">
                    Deep insights into your brand's online presence
                </p>
            </div>
        </div>
    );
}
