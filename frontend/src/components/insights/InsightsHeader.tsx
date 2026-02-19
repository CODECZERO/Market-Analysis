/**
 * Insights Header Component
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Globe } from "lucide-react";

interface InsightsHeaderProps {
    brandName: string;
    brandId: string;
}

export function InsightsHeader({ brandName, brandId }: InsightsHeaderProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between"
        >
            <div>
                <h1 className="text-2xl font-semibold text-white flex items-center gap-2">
                    <Globe className="w-6 h-6 text-blue-500" />
                    Web Intelligence Report
                </h1>
                <p className="text-zinc-400 text-sm mt-1">
                    Deep dive analysis for <span className="text-blue-400 font-medium">{brandName}</span>
                </p>
            </div>
            <Link
                to={`/brands/${brandId}/dashboard`}
                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm transition border border-zinc-700"
            >
                Esc
            </Link>
        </motion.div>
    );
}
