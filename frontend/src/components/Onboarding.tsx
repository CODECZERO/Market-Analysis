/**
 * Onboarding Component
 * 
 * Interactive product tour that highlights key features of the dashboard.
 * Uses a spotlight effect to guide users through the interface.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowRight, ArrowLeft, X, CheckCircle,
    Sparkles, Target, ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface OnboardingStep {
    target: string; // CSS selector
    title: string;
    description: string;
    position: 'top' | 'bottom' | 'left' | 'right';
}

interface OnboardingProps {
    steps?: OnboardingStep[];
    onComplete?: () => void;
    onSkip?: () => void;
}

const TOUR_STORAGE_KEY = 'brand_pulse_tour_complete';

const defaultSteps: OnboardingStep[] = [
    {
        target: '[data-tour="sidebar"]',
        title: 'Navigation',
        description: 'Access all your brand monitoring tools from the sidebar. Switch between brands and features quickly.',
        position: 'right'
    },
    {
        target: '[data-tour="dashboard"]',
        title: 'Dashboard Overview',
        description: 'Your command center. See sentiment scores, mention counts, and key metrics at a glance.',
        position: 'bottom'
    },
    {
        target: '[data-tour="mentions"]',
        title: 'Live Mentions',
        description: 'Real-time stream of brand mentions from across the web. Filter by sentiment, source, and date.',
        position: 'bottom'
    },
    {
        target: '[data-tour="analytics"]',
        title: 'Analytics',
        description: 'Deep dive into your brand\'s performance with charts, trends, and AI-powered insights.',
        position: 'left'
    },
    {
        target: '[data-tour="alerts"]',
        title: 'Alert Settings',
        description: 'Configure notifications for crisis alerts, sentiment drops, and mention spikes.',
        position: 'bottom'
    }
];

export default function Onboarding({
    steps = defaultSteps,
    onComplete,
    onSkip
}: OnboardingProps) {
    const [isActive, setIsActive] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

    // Check if tour should show
    useEffect(() => {
        const hasCompleted = localStorage.getItem(TOUR_STORAGE_KEY);
        if (!hasCompleted) {
            // Delay to let the page render
            const timer = setTimeout(() => setIsActive(true), 1000);
            return () => clearTimeout(timer);
        }
    }, []);

    // Find and highlight target element
    useEffect(() => {
        if (!isActive || currentStep >= steps.length) return;

        const step = steps[currentStep];
        const element = document.querySelector(step.target);

        if (element) {
            const rect = element.getBoundingClientRect();
            setTargetRect(rect);

            // Scroll element into view if needed
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            setTargetRect(null);
        }
    }, [isActive, currentStep, steps]);

    const handleNext = useCallback(() => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(s => s + 1);
        } else {
            handleComplete();
        }
    }, [currentStep, steps.length]);

    const handlePrev = useCallback(() => {
        if (currentStep > 0) {
            setCurrentStep(s => s - 1);
        }
    }, [currentStep]);

    const handleComplete = useCallback(() => {
        localStorage.setItem(TOUR_STORAGE_KEY, 'true');
        setIsActive(false);
        onComplete?.();
    }, [onComplete]);

    const handleSkip = useCallback(() => {
        localStorage.setItem(TOUR_STORAGE_KEY, 'true');
        setIsActive(false);
        onSkip?.();
    }, [onSkip]);

    if (!isActive) return null;

    const step = steps[currentStep];
    const isLastStep = currentStep === steps.length - 1;

    // Calculate tooltip position
    const getTooltipStyle = () => {
        if (!targetRect) {
            return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
        }

        const padding = 16;
        const tooltipWidth = 320;
        const tooltipHeight = 200;

        switch (step.position) {
            case 'top':
                return {
                    bottom: window.innerHeight - targetRect.top + padding,
                    left: targetRect.left + targetRect.width / 2,
                    transform: 'translateX(-50%)'
                };
            case 'bottom':
                return {
                    top: targetRect.bottom + padding,
                    left: targetRect.left + targetRect.width / 2,
                    transform: 'translateX(-50%)'
                };
            case 'left':
                return {
                    top: targetRect.top + targetRect.height / 2,
                    right: window.innerWidth - targetRect.left + padding,
                    transform: 'translateY(-50%)'
                };
            case 'right':
                return {
                    top: targetRect.top + targetRect.height / 2,
                    left: targetRect.right + padding,
                    transform: 'translateY(-50%)'
                };
            default:
                return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[9999]">
                {/* Overlay with cutout */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-black/60"
                    onClick={handleSkip}
                />

                {/* Spotlight effect */}
                {targetRect && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="absolute pointer-events-none"
                        style={{
                            top: targetRect.top - 8,
                            left: targetRect.left - 8,
                            width: targetRect.width + 16,
                            height: targetRect.height + 16,
                            boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.6)',
                            borderRadius: '12px',
                            border: '2px solid rgba(59, 130, 246, 0.5)'
                        }}
                    />
                )}

                {/* Tooltip */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="absolute w-80 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl p-5"
                    style={getTooltipStyle()}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                                <Target className="w-4 h-4 text-blue-400" />
                            </div>
                            <span className="text-xs text-zinc-500">
                                Step {currentStep + 1} of {steps.length}
                            </span>
                        </div>
                        <button
                            onClick={handleSkip}
                            className="text-zinc-500 hover:text-white transition-colors"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Content */}
                    <h3 className="text-lg font-semibold text-white mb-2">
                        {step.title}
                    </h3>
                    <p className="text-sm text-zinc-400 mb-4 leading-relaxed">
                        {step.description}
                    </p>

                    {/* Progress bar */}
                    <div className="h-1 bg-zinc-800 rounded-full mb-4 overflow-hidden">
                        <motion.div
                            className="h-full bg-blue-500"
                            initial={{ width: 0 }}
                            animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                            transition={{ duration: 0.3 }}
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                        {currentStep > 0 && (
                            <Button
                                onClick={handlePrev}
                                variant="ghost"
                                size="sm"
                                className="text-zinc-400 hover:text-white"
                            >
                                <ArrowLeft className="w-4 h-4 mr-1" />
                                Back
                            </Button>
                        )}
                        <div className="flex-1" />
                        <Button
                            onClick={handleNext}
                            size="sm"
                            className={`gap-1 ${isLastStep ? 'bg-green-600 hover:bg-green-500' : 'bg-blue-600 hover:bg-blue-500'}`}
                        >
                            {isLastStep ? (
                                <>
                                    <CheckCircle className="w-4 h-4" />
                                    Finish
                                </>
                            ) : (
                                <>
                                    Next
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </Button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}

// Hook to manually trigger tour
export function useStartTour() {
    return () => {
        localStorage.removeItem(TOUR_STORAGE_KEY);
        window.location.reload();
    };
}
