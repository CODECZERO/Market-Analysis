/**
 * Toggle Switch Component
 * 
 * Reusable toggle switch for settings
 */

import { cn } from "@/lib/utils";

interface ToggleSwitchProps {
    checked: boolean;
    onChange: (checked: boolean) => void;
    color?: "blue" | "emerald" | "purple";
    className?: string;
}

export function ToggleSwitch({
    checked,
    onChange,
    color = "blue",
    className,
}: ToggleSwitchProps) {
    const colors = {
        blue: "peer-checked:bg-blue-600",
        emerald: "peer-checked:bg-emerald-500",
        purple: "peer-checked:bg-purple-500",
    };

    return (
        <label className={cn("relative inline-flex items-center cursor-pointer", className)}>
            <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onChange(e.target.checked)}
                className="sr-only peer"
            />
            <div className={`w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all ${colors[color]}`} />
        </label>
    );
}
