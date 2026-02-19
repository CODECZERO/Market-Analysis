/**
 * Onboarding Step Progress Component
 * 
 * Displays the step-by-step progress indicator
 */

import { CheckCircle2, LucideIcon } from "lucide-react";

interface Step {
    id: string;
    icon: LucideIcon;
    title: string;
}

interface StepProgressProps {
    steps: Step[];
    currentStep: string;
}

export function StepProgress({ steps, currentStep }: StepProgressProps) {
    const currentStepIndex = steps.findIndex(s => s.id === currentStep);

    return (
        <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
                {steps.map((s, idx) => {
                    const Icon = s.icon;
                    const isActive = idx === currentStepIndex;
                    const isCompleted = idx < currentStepIndex;

                    return (
                        <div key={s.id} className="flex flex-col items-center gap-2 relative z-10">
                            <div className={`
                                w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300
                                ${isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25 scale-110' :
                                    isCompleted ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-500'}
                            `}>
                                {isCompleted ? <CheckCircle2 className="w-6 h-6" /> : <Icon className="w-5 h-5" />}
                            </div>
                            <span className={`text-xs font-medium ${isActive ? 'text-blue-400' : 'text-zinc-600'}`}>
                                {s.title}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
