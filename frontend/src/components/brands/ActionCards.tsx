/**
 * Quick Action Cards
 * 
 * Navigation cards for main features
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { BarChart3, Shield, DollarSign } from "lucide-react";

export function ActionCards() {
    return (
        <div className="grid gap-4 sm:grid-cols-3">
            <ActionCard
                to="/analytics"
                icon={<BarChart3 className="h-4 w-4" />}
                title="Analytics"
                description="View detailed insights"
            />
            <ActionCard
                to="/crisis"
                icon={<Shield className="h-4 w-4" />}
                title="Crisis Monitor"
                description="Track brand health"
            />
            <ActionCard
                to="/money-mode"
                icon={<DollarSign className="h-4 w-4" />}
                title="Money Mode"
                description="Find hot leads"
            />
        </div>
    );
}

function ActionCard({
    to,
    icon,
    title,
    description
}: {
    to: string;
    icon: React.ReactNode;
    title: string;
    description: string;
}) {
    return (
        <motion.div
            whileHover={{ y: -4, scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300 }}
        >
            <Link
                to={to}
                className="group flex items-center gap-3 p-4 rounded-xl bg-zinc-900/50 border border-zinc-800 hover:border-blue-500/30 transition-colors"
            >
                <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-500 group-hover:scale-105 transition-transform">
                    {icon}
                </div>
                <div>
                    <p className="text-sm font-medium text-white">{title}</p>
                    <p className="text-xs text-zinc-500">{description}</p>
                </div>
            </Link>
        </motion.div>
    );
}
