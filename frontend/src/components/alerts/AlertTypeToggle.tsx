/**
 * Alert Type Toggle Component
 * 
 * Toggle button for enabling/disabling specific alert types
 */

import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";

interface AlertTypeToggleProps {
    icon: React.ReactNode;
    title: string;
    description: string;
    color: "red" | "amber" | "blue" | "purple";
    enabled: boolean;
    onChange: (value: boolean) => void;
}

const COLORS = {
    red: "bg-red-500/10 border-red-500/20 text-red-400",
    amber: "bg-amber-500/10 border-amber-500/20 text-amber-400",
    blue: "bg-blue-500/10 border-blue-500/20 text-blue-400",
    purple: "bg-purple-500/10 border-purple-500/20 text-purple-400",
};

export function AlertTypeToggle({
    icon,
    title,
    description,
    color,
    enabled,
    onChange,
}: AlertTypeToggleProps) {
    return (
        <motion.div
            whileHover={{ scale: 1.02 }}
            className={`p-4 rounded-xl border transition-colors cursor-pointer ${enabled
                    ? "bg-zinc-800/50 border-zinc-600/50"
                    : "bg-zinc-900/30 border-zinc-800/50 opacity-60"
                }`}
            onClick={() => onChange(!enabled)}
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg border ${COLORS[color]}`}>
                        {icon}
                    </div>
                    <div>
                        <p className="font-medium text-white">{title}</p>
                        <p className="text-xs text-zinc-500">{description}</p>
                    </div>
                </div>
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${enabled
                        ? "border-blue-500 bg-blue-500"
                        : "border-zinc-600"
                    }`}>
                    {enabled && <CheckCircle2 className="w-3 h-3 text-white" />}
                </div>
            </div>
        </motion.div>
    );
}
