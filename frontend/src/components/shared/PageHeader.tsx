/**
 * Page Header Component
 * 
 * Consistent page header with icon, title, description, and action buttons.
 * Used at the top of feature pages.
 */

import type { LucideIcon } from "lucide-react";

interface PageHeaderProps {
    icon: LucideIcon;
    title: string;
    description?: string;
    actions?: React.ReactNode;
    /** Gradient color for icon background */
    iconColor?: 'purple' | 'blue' | 'emerald' | 'amber' | 'red';
}

export function PageHeader({
    icon: Icon,
    title,
    description,
    actions,
    iconColor = 'purple',
}: PageHeaderProps) {
    const iconColors = {
        purple: 'bg-purple-500/10 border-purple-500/20 text-purple-400',
        blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
        emerald: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
        amber: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
        red: 'bg-red-500/10 border-red-500/20 text-red-400',
    };

    return (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
                <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                    <div className={`p-2 rounded-xl border ${iconColors[iconColor]}`}>
                        <Icon className="w-6 h-6" />
                    </div>
                    {title}
                </h1>
                {description && (
                    <p className="text-zinc-400 mt-2 ml-1">{description}</p>
                )}
            </div>
            {actions && <div className="flex gap-3">{actions}</div>}
        </div>
    );
}
