/**
 * Status Badge Component
 * 
 * Reusable status indicator with pulse animation option.
 */

import { cn } from "@/lib/utils";

interface StatusBadgeProps {
    status: 'online' | 'offline' | 'warning' | 'loading';
    label?: string;
    pulse?: boolean;
    className?: string;
}

export function StatusBadge({
    status,
    label,
    pulse = false,
    className,
}: StatusBadgeProps) {
    const statusConfig = {
        online: {
            bg: 'bg-green-500',
            text: 'text-green-400',
            glow: 'shadow-[0_0_6px_rgba(34,197,94,0.6)]',
        },
        offline: {
            bg: 'bg-zinc-500',
            text: 'text-zinc-400',
            glow: '',
        },
        warning: {
            bg: 'bg-amber-500',
            text: 'text-amber-400',
            glow: 'shadow-[0_0_6px_rgba(245,158,11,0.6)]',
        },
        loading: {
            bg: 'bg-blue-500',
            text: 'text-blue-400',
            glow: 'shadow-[0_0_6px_rgba(59,130,246,0.6)]',
        },
    };

    const config = statusConfig[status];

    return (
        <div className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-700/50",
            className
        )}>
            <div
                className={cn(
                    "w-2 h-2 rounded-full",
                    config.bg,
                    pulse && config.glow,
                    pulse && "animate-pulse"
                )}
            />
            {label && (
                <span className={cn("text-xs font-medium", config.text)}>
                    {label}
                </span>
            )}
        </div>
    );
}
