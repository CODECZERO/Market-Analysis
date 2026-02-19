import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Circle, X, ArrowRight, Sparkles } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Props {
    brandId: string;
}

export function GettingStarted({ brandId }: Props) {
    const [searchParams] = useSearchParams();
    const [isVisible, setIsVisible] = useState(true);
    const [completedSteps, setCompletedSteps] = useState<string[]>([]);

    // Check if we just finished onboarding
    useEffect(() => {
        if (searchParams.get("onboarding") === "true") {
            setIsVisible(true);
            // Mark first step as done if coming from onboarding
            setCompletedSteps(prev => [...new Set([...prev, "create_brand"])]);
        }
    }, [searchParams]);

    // Mock progress checking (in real app, check API data)
    useEffect(() => {
        // Determine what's done based on assumption or Props
        // For now, we simulate "Create Brand" is always done if we are here
        setCompletedSteps(prev => [...new Set([...prev, "create_brand"])]);
    }, []);

    if (!isVisible) return null;

    const steps = [
        { id: "create_brand", label: "Create your brand", link: null },
        { id: "add_competitor", label: "Add a competitor", link: `/brands/${brandId}/competitors` },
        { id: "connect_source", label: "Connect a data source", link: `/brands/${brandId}/settings` },
        { id: "invite_team", label: "Invite your team", link: `/brands/${brandId}/team` },
    ];

    const progress = (completedSteps.length / steps.length) * 100;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: -20, height: 0 }}
                animate={{ opacity: 1, y: 0, height: "auto" }}
                exit={{ opacity: 0, y: -20, height: 0 }}
                className="mb-6"
            >
                <Card className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-blue-500/20 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
                    <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                            <div className="space-y-1">
                                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                    <Sparkles className="w-5 h-5 text-blue-400" />
                                    Getting Started
                                </h3>
                                <p className="text-zinc-400 text-sm">Complete these steps to get the most out of your dashboard.</p>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="text-zinc-500 hover:text-white -mt-2 -mr-2"
                                onClick={() => setIsVisible(false)}
                            >
                                <X className="w-4 h-4" />
                            </Button>
                        </div>

                        <div className="mt-4 grid gap-3 md:grid-cols-4">
                            {steps.map((step) => {
                                const isCompleted = completedSteps.includes(step.id);
                                return (
                                    <div key={step.id} className={`p-3 rounded-lg border ${isCompleted ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-zinc-800/50 border-zinc-700/50'}`}>
                                        <div className="flex items-center gap-3 mb-2">
                                            {isCompleted ? (
                                                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                            ) : (
                                                <Circle className="w-5 h-5 text-zinc-500" />
                                            )}
                                            <span className={`text-sm font-medium ${isCompleted ? 'text-emerald-200' : 'text-zinc-300'}`}>
                                                {step.label}
                                            </span>
                                        </div>
                                        {step.link && !isCompleted && (
                                            <Link to={step.link} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 mt-1 pl-8">
                                                Start <ArrowRight className="w-3 h-3" />
                                            </Link>
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        <div className="mt-3 h-1 bg-zinc-800 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-blue-500"
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                                transition={{ duration: 1 }}
                            />
                        </div>
                    </CardContent>
                </Card>
            </motion.div>
        </AnimatePresence>
    );
}
