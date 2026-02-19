/**
 * Opportunities and Risk Grid Component
 */

import { motion } from "framer-motion";
import { Sparkles, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface OpportunitiesRiskGridProps {
    opportunities: string[];
    risks: string[];
}

export function OpportunitiesRiskGrid({ opportunities, risks }: OpportunitiesRiskGridProps) {
    return (
        <div className="grid lg:grid-cols-2 gap-6">
            {/* Opportunities */}
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
            >
                <Card className="bg-zinc-900/50 border-zinc-800 h-full">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2 text-emerald-400">
                            <Sparkles className="w-5 h-5" />
                            Growth Opportunities
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-4">
                            {opportunities.map((opp, idx) => (
                                <li key={idx} className="flex gap-3">
                                    <div className="w-6 h-6 rounded bg-emerald-500/10 flex items-center justify-center shrink-0 border border-emerald-500/20 text-emerald-500 font-mono text-xs">
                                        {idx + 1}
                                    </div>
                                    <span className="text-zinc-300 leading-snug">{opp}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </motion.div>

            {/* Risks */}
            <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
            >
                <Card className="bg-zinc-900/50 border-zinc-800 h-full">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2 text-red-400">
                            <ShieldAlert className="w-5 h-5" />
                            Detected Risks
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-4">
                            {risks.map((risk, idx) => (
                                <li key={idx} className="flex gap-3">
                                    <div className="w-6 h-6 rounded bg-red-500/10 flex items-center justify-center shrink-0 border border-red-500/20 text-red-500 font-mono text-xs">
                                        !
                                    </div>
                                    <span className="text-zinc-300 leading-snug">{risk}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </motion.div>
        </div>
    );
}
