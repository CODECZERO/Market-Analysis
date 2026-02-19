/**
 * Base Card Component
 * 
 * Consistent card styling for dashboard components.
 * Wraps content with standard zinc styling and optional header.
 */

import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface BaseCardProps {
    children: React.ReactNode;
    className?: string;
    /** Optional title with icon */
    title?: string;
    icon?: LucideIcon;
    /** Optional action button/element */
    action?: React.ReactNode;
    /** Remove default padding */
    noPadding?: boolean;
}

export function BaseCard({
    children,
    className,
    title,
    icon: Icon,
    action,
    noPadding = false,
}: BaseCardProps) {
    return (
        <div
            className={cn(
                "bg-zinc-900/50 border border-zinc-800 rounded-xl",
                !noPadding && "p-5",
                className
            )}
        >
            {(title || action) && (
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        {Icon && <Icon className="w-4 h-4 text-zinc-400" />}
                        {title && <h3 className="text-sm font-semibold text-white">{title}</h3>}
                    </div>
                    {action}
                </div>
            )}
            {children}
        </div>
    );
}

/**
 * Glowing variant for highlighted content
 */
interface GlowCardProps extends Omit<BaseCardProps, 'className'> {
    glowColor?: 'purple' | 'blue' | 'emerald' | 'amber' | 'red';
    className?: string;
}

export function GlowCard({
    glowColor = 'purple',
    className,
    ...props
}: GlowCardProps) {
    const glowColors = {
        purple: 'border-purple-500/30 bg-purple-500/5',
        blue: 'border-blue-500/30 bg-blue-500/5',
        emerald: 'border-emerald-500/30 bg-emerald-500/5',
        amber: 'border-amber-500/30 bg-amber-500/5',
        red: 'border-red-500/30 bg-red-500/5',
    };

    return (
        <BaseCard
            className={cn(glowColors[glowColor], className)}
            {...props}
        />
    );
}
