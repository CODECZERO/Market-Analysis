/**
 * Empty State Component
 * 
 * Consistent empty/placeholder state for when no data is available.
 * Shows icon, message, and optional action button.
 */

import { Button } from "@/components/ui/button";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
    icon: LucideIcon;
    title: string;
    description?: string;
    actionLabel?: string;
    onAction?: () => void;
    className?: string;
}

export function EmptyState({
    icon: Icon,
    title,
    description,
    actionLabel,
    onAction,
    className = "",
}: EmptyStateProps) {
    return (
        <div className={`p-12 text-center ${className}`}>
            <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center mx-auto mb-4 border border-zinc-700">
                <Icon className="w-6 h-6 text-zinc-500" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
            {description && (
                <p className="text-sm text-zinc-400 mb-6 max-w-sm mx-auto">
                    {description}
                </p>
            )}
            {actionLabel && onAction && (
                <Button onClick={onAction} variant="outline">
                    {actionLabel}
                </Button>
            )}
        </div>
    );
}
