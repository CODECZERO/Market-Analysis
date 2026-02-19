/**
 * Lead Feed Component
 */

import { motion, AnimatePresence } from "framer-motion";
import { LeadCard } from "./LeadCard";
import type { Lead } from "@/types/api";

interface LeadFeedProps {
    leads: Lead[];
    loading: boolean;
    error: string | null;
    selectedLead: Lead | null;
    onSelectLead: (lead: Lead) => void;
    onUpdateStatus: (id: string, status: string) => void;
    onRetry: () => void;
}

export function LeadFeed({
    leads,
    loading,
    error,
    selectedLead,
    onSelectLead,
    onUpdateStatus,
    onRetry,
}: LeadFeedProps) {
    return (
        <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Live Opportunities</h2>
                <div className="flex gap-2">
                    <span className="px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs text-zinc-400">
                        Real-time
                    </span>
                </div>
            </div>

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-40 bg-zinc-900/30 rounded-xl border border-zinc-800/50 animate-pulse" />
                    ))}
                </div>
            ) : error ? (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
                    <div className="flex items-center gap-3">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <p>{error}</p>
                        <button
                            onClick={onRetry}
                            className="ml-auto text-sm underline hover:text-red-300"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            ) : leads.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 bg-zinc-900/20 rounded-2xl border border-zinc-800/50 border-dashed">
                    <div className="w-16 h-16 rounded-full bg-zinc-900/50 flex items-center justify-center mb-4 text-zinc-500">
                        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <h3 className="text-zinc-300 font-medium mb-1">No Leads Found</h3>
                    <p className="text-zinc-500 text-sm text-center max-w-sm">
                        AI is monitoring for commercial intent. New opportunities will appear here automatically.
                    </p>
                </div>
            ) : (
                <div className="space-y-4">
                    <AnimatePresence>
                        {leads.map((lead, index) => (
                            <LeadCard
                                key={lead.id}
                                lead={lead}
                                index={index}
                                isSelected={selectedLead?.id === lead.id}
                                onSelect={() => onSelectLead(lead)}
                                onStatusChange={onUpdateStatus}
                            />
                        ))}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
}
