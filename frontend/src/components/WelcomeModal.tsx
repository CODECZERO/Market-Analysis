/**
 * Welcome Modal Component
 * 
 * Appears for new users on first login. Provides a quick start guide.
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    Sparkles, ArrowRight, X, Zap, BarChart3,
    Users, Bell, Rocket
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WelcomeModalProps {
    onComplete?: () => void;
}

const STORAGE_KEY = 'brand_pulse_onboarding_complete';

export default function WelcomeModal({ onComplete }: WelcomeModalProps) {
    const [isVisible, setIsVisible] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        // Check if user has completed onboarding
        const hasCompleted = localStorage.getItem(STORAGE_KEY);
        if (!hasCompleted) {
            // Small delay for better UX
            const timer = setTimeout(() => setIsVisible(true), 500);
            return () => clearTimeout(timer);
        }
    }, []);

    const handleComplete = () => {
        localStorage.setItem(STORAGE_KEY, 'true');
        setIsVisible(false);
        onComplete?.();
    };

    const handleSkip = () => {
        handleComplete();
    };

    const handleCreateBrand = () => {
        handleComplete();
        navigate('/brands/create');
    };

    const steps = [
        {
            icon: <Rocket className="w-8 h-8" />,
            title: "Welcome to Brand Pulse",
            description: "Your AI-powered brand monitoring command center. Track mentions, analyze sentiment, and stay ahead of competitors.",
            color: "from-blue-500 to-cyan-400"
        },
        {
            icon: <BarChart3 className="w-8 h-8" />,
            title: "Real-time Analytics",
            description: "Get instant insights into your brand's online presence with sentiment analysis, mention tracking, and trend detection.",
            color: "from-purple-500 to-pink-400"
        },
        {
            icon: <Users className="w-8 h-8" />,
            title: "Competitor Intelligence",
            description: "Track your competitors' weaknesses and discover market gaps to gain a strategic advantage.",
            color: "from-orange-500 to-amber-400"
        },
        {
            icon: <Bell className="w-8 h-8" />,
            title: "Smart Alerts",
            description: "Get notified instantly about crisis situations, sentiment drops, and viral mentions via Slack, Discord, or email.",
            color: "from-emerald-500 to-teal-400"
        }
    ];

    if (!isVisible) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
            >
                <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                    className="relative w-full max-w-lg bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden"
                >
                    {/* Skip button */}
                    <button
                        onClick={handleSkip}
                        className="absolute top-4 right-4 text-zinc-500 hover:text-white transition-colors z-10"
                    >
                        <X className="w-5 h-5" />
                    </button>

                    {/* Content */}
                    <div className="p-8">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={currentStep}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                transition={{ duration: 0.3 }}
                                className="text-center"
                            >
                                {/* Icon */}
                                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${steps[currentStep].color} flex items-center justify-center mx-auto mb-6 text-white shadow-lg`}>
                                    {steps[currentStep].icon}
                                </div>

                                {/* Title */}
                                <h2 className="text-2xl font-bold text-white mb-3">
                                    {steps[currentStep].title}
                                </h2>

                                {/* Description */}
                                <p className="text-zinc-400 leading-relaxed mb-8">
                                    {steps[currentStep].description}
                                </p>
                            </motion.div>
                        </AnimatePresence>

                        {/* Step indicators */}
                        <div className="flex justify-center gap-2 mb-8">
                            {steps.map((_, index) => (
                                <button
                                    key={index}
                                    onClick={() => setCurrentStep(index)}
                                    className={`w-2 h-2 rounded-full transition-all ${index === currentStep
                                            ? 'w-6 bg-blue-500'
                                            : 'bg-zinc-700 hover:bg-zinc-600'
                                        }`}
                                />
                            ))}
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3">
                            {currentStep < steps.length - 1 ? (
                                <>
                                    <Button
                                        onClick={handleSkip}
                                        variant="ghost"
                                        className="flex-1 text-zinc-400 hover:text-white"
                                    >
                                        Skip
                                    </Button>
                                    <Button
                                        onClick={() => setCurrentStep(s => s + 1)}
                                        className="flex-1 bg-blue-600 hover:bg-blue-500 gap-2"
                                    >
                                        Next
                                        <ArrowRight className="w-4 h-4" />
                                    </Button>
                                </>
                            ) : (
                                <Button
                                    onClick={handleCreateBrand}
                                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 gap-2 h-12 text-base"
                                >
                                    <Sparkles className="w-5 h-5" />
                                    Create Your First Brand
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Decorative gradient */}
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}

// Hook to reset onboarding (for testing)
export function useResetOnboarding() {
    return () => localStorage.removeItem(STORAGE_KEY);
}
