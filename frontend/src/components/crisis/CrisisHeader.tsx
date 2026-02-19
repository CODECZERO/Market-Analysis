/**
 * Crisis Header Component
 * 
 * Displays the page title, description, and live status toggle.
 */

import { motion } from "framer-motion";
import { AlertTriangle, Zap } from "lucide-react";

interface CrisisHeaderProps {
    isLive: boolean;
    onToggleLive: () => void;
}

export function CrisisHeader({ isLive, onToggleLive }: CrisisHeaderProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="relative overflow-hidden rounded-xl bg-gradient-to-br from-red-950/40 via-zinc-900/60 to-orange-950/30 border border-red-500/20 p-4 md:p-6"
        >
            <div className="relative z-10">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-3 md:gap-4">
                        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shadow-lg shadow-red-500/25 shrink-0">
                            <AlertTriangle className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">Crisis Monitor</h1>
                            <p className="text-xs md:text-sm text-zinc-400 mt-0.5 max-w-md">
                                AI-powered early warning system that predicts and prevents viral PR disasters.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 self-start md:self-center">
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-900/60 border border-zinc-700/50">
                            <motion.div
                                animate={{ scale: isLive ? [1, 1.2, 1] : 1 }}
                                transition={{ duration: 2, repeat: isLive ? Infinity : 0 }}
                                className={`w-1.5 h-1.5 rounded-full ${isLive ? "bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.6)]" : "bg-zinc-500"}`}
                            />
                            <span className="text-[10px] font-medium text-zinc-300">{isLive ? "Live" : "Paused"}</span>
                        </div>
                        <button
                            onClick={onToggleLive}
                            className="px-2.5 py-1 bg-zinc-800/80 hover:bg-zinc-700 rounded-lg text-[10px] font-medium transition border border-zinc-700"
                        >
                            {isLive ? "Pause" : "Resume"}
                        </button>
                    </div>
                </div>

                <div className="flex items-center gap-1.5 mt-3 text-[10px] text-red-300/90 bg-red-500/10 px-2.5 py-1.5 rounded-lg w-fit border border-red-500/20">
                    <Zap className="w-3 h-3" />
                    <span>Detects velocity spikes 6 hours before generic tools</span>
                </div>
            </div>

            <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />
        </motion.div>
    );
}
