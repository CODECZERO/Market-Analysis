/**
 * Section Header Component
 * 
 * Consistent section header with icon, title, subtitle, and optional badge.
 * Used across dashboard sections for visual consistency.
 */

import type { LucideIcon } from "lucide-react";

interface SectionHeaderProps {
    icon: LucideIcon;
    title: string;
    subtitle?: string;
    badge?: React.ReactNode;
    className?: string;
}

export function SectionHeader({
    icon: Icon,
    title,
    subtitle,
    badge,
    className = "",
}: SectionHeaderProps) {
    return (
        <div className={`flex items-center justify-between mb-4 ${className}`}>
            <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-zinc-800/80 border border-zinc-700/50 flex items-center justify-center">
                    <Icon className="text-zinc-400 w-4 h-4" />
                </div>
                <div>
                    <h2 className="text-base font-semibold text-white">{title}</h2>
                    {subtitle && <p className="text-xs text-zinc-500">{subtitle}</p>}
                </div>
            </div>
            {badge}
        </div>
    );
}
