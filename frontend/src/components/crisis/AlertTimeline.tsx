/**
 * Alert Timeline Component
 * 
 * List of active crisis alerts with resolve functionality
 */

import { motion, AnimatePresence } from "framer-motion";
import { Bell, AlertTriangle, CheckCircle2, Shield } from "lucide-react";
import type { AlertEvent } from "./CrisisTypes";

interface AlertTimelineProps {
    alerts: AlertEvent[];
    onResolve: (id: string) => void;
    formatDate: (dateStr: string) => string;
}

export function AlertTimeline({ alerts, onResolve, formatDate }: AlertTimelineProps) {
    return (
        <div className="rounded-xl bg-zinc-900/30 backdrop-blur-sm border border-zinc-800/50 p-4">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                    <Bell className="w-3.5 h-3.5 text-amber-500" />
                </div>
                <div>
                    <h3 className="text-sm font-semibold text-white">Live Alerts</h3>
                    <p className="text-[10px] text-zinc-500">Active threats needing attention</p>
                </div>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                <AnimatePresence mode="popLayout">
                    {alerts.map((alert, i) => (
                        <motion.div
                            key={alert.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ delay: i * 0.05 }}
                            className={`relative overflow-hidden rounded-xl p-4 border transition-all ${alert.severity === "critical"
                                ? "bg-red-900/10 border-red-500/20"
                                : "bg-amber-900/10 border-amber-500/20"
                                }`}
                        >
                            <div className="flex items-start gap-4">
                                <div
                                    className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${alert.severity === "critical" ? "bg-red-500/10 text-red-500" : "bg-amber-500/10 text-amber-500"
                                        }`}
                                >
                                    {alert.isResolved ? <CheckCircle2 className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="flex items-center gap-2">
                                            <span
                                                className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded ${alert.severity === "critical" ? "bg-red-500/20 text-red-400" : "bg-amber-500/20 text-amber-400"
                                                    }`}
                                            >
                                                {alert.severity}
                                            </span>
                                            <span className="text-xs text-zinc-500 font-mono">
                                                {formatDate(alert.createdAt)}
                                            </span>
                                        </div>
                                        {alert.isResolved ? (
                                            <span className="text-xs font-medium text-green-500 flex items-center gap-1">
                                                <CheckCircle2 className="w-3 h-3" /> Resolved
                                            </span>
                                        ) : (
                                            <button
                                                onClick={() => onResolve(alert.id)}
                                                className="text-xs font-medium text-blue-400 hover:text-blue-300 hover:underline"
                                            >
                                                Mark Resolved
                                            </button>
                                        )}
                                    </div>

                                    <p className="text-white font-medium mb-1 line-clamp-1">
                                        {alert.triggeredReasons.join(", ") || "Anomaly detected"}
                                    </p>

                                    <div className="flex items-center gap-2 text-xs text-zinc-400 bg-black/20 p-2 rounded-lg mt-2">
                                        <Shield className="w-3 h-3 text-zinc-500" />
                                        <span>AI Rec: {alert.recommendedAction}</span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {alerts.length === 0 && (
                    <div className="text-center py-12 bg-zinc-900/20 rounded-xl border border-dashed border-zinc-800">
                        <div className="w-12 h-12 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mx-auto mb-3">
                            <Shield className="w-6 h-6" />
                        </div>
                        <p className="text-white font-medium">All Clear</p>
                        <p className="text-xs text-zinc-500 mt-1">No active threats detected at this time.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
