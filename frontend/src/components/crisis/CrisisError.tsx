/**
 * Crisis Error State
 */

import { AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

interface CrisisErrorProps {
    message: string;
    onRetry: () => void;
}

export function CrisisError({ message, onRetry }: CrisisErrorProps) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-12 rounded-2xl bg-zinc-900/30 border border-zinc-800/50 text-center"
        >
            <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4 opacity-80" />
            <p className="text-zinc-300 text-lg font-medium mb-2">{message}</p>
            <p className="text-zinc-500 mb-6">Start monitoring a brand to see real-time risk analysis.</p>
            <button
                onClick={onRetry}
                className="px-6 py-2.5 bg-zinc-100 text-zinc-900 hover:bg-white rounded-lg font-medium transition shadow-lg shadow-white/5"
            >
                Retry Connection
            </button>
        </motion.div>
    );
}
