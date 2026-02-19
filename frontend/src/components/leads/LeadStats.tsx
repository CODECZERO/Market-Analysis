/**
 * Lead Stats Component
 */

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import type { LeadStats as LeadStatsType } from "@/types/api";

interface LeadStatsProps {
    stats: LeadStatsType | null;
    leadCount: number;
}

export function LeadStats({ stats, leadCount }: LeadStatsProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 md:grid-cols-5 gap-3"
        >
            <StatCard label="Total Leads" value={stats?.totalLeads ?? leadCount} delay={0.1} />
            <StatCard label="New Opportunities" value={stats?.newLeads ?? 0} color="text-blue-400" delay={0.15} />
            <StatCard label="Qualified" value={stats?.qualifiedLeads ?? 0} color="text-emerald-400" delay={0.2} />
            <StatCard label="Pipeline Value" value={stats?.convertedLeads ?? 0} prefix="$" color="text-green-400" delay={0.25} />
            <StatCard label="Avg Intent Score" value={stats?.avgLeadScore ? Math.round(stats.avgLeadScore) : 0} suffix="/100" delay={0.3} />
        </motion.div>
    );
}

function StatCard({ label, value, suffix = "", prefix = "", color = "text-white", delay = 0 }: { label: string; value: number; suffix?: string; prefix?: string; color?: string; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className="bg-zinc-900/40 rounded-xl p-3 border border-zinc-800/50 hover:border-zinc-700/50 transition-colors"
        >
            <p className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider mb-1">{label}</p>
            <p className={`text-xl font-bold ${color} tracking-tight`}>
                <span className="text-sm opacity-70 mr-0.5">{prefix}</span>
                <AnimatedCounter value={value} />
                <span className="text-xs opacity-50 ml-0.5">{suffix}</span>
            </p>
        </motion.div>
    );
}

function AnimatedCounter({ value }: { value: number }) {
    const [displayValue, setDisplayValue] = useState(0);

    useEffect(() => {
        const duration = 800;
        const steps = 40;
        const increment = value / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= value) {
                setDisplayValue(value);
                clearInterval(timer);
            } else {
                setDisplayValue(Math.floor(current));
            }
        }, duration / steps);

        return () => clearInterval(timer);
    }, [value]);

    return <>{displayValue}</>;
}
