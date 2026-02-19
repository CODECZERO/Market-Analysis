/**
 * Onboarding Page - Brand Setup Wizard
 * 
 * Refactored to use extracted step components
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { ArrowRight, Target, Globe, Search, Building2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useCreateBrand } from "@/hooks/useBrands";
import { LoadingState } from "@/components/shared/LoadingState";
import {
    StepProgress,
    BrandStep,
    KeywordsStep,
    MatchingStep,
    CompetitorsStep,
    ConnectStep,
} from "@/components/onboarding";
import type { BrandMatchConfig } from "@/types/api";

type Step = "brand" | "keywords" | "matching" | "competitors" | "connect";

const STEPS = [
    { id: "brand", icon: Building2, title: "Brand" },
    { id: "keywords", icon: Search, title: "Keywords" },
    { id: "matching", icon: Sparkles, title: "AI Tuning" },
    { id: "competitors", icon: Target, title: "Competitors" },
    { id: "connect", icon: Globe, title: "Sources" },
];

export default function OnboardingPage() {
    const navigate = useNavigate();
    const createBrand = useCreateBrand();

    const [step, setStep] = useState<Step>("brand");
    const [brandName, setBrandName] = useState("");
    const [keywords, setKeywords] = useState<string[]>([]);
    const [competitors, setCompetitors] = useState<string[]>([]);
    const [newCompetitor, setNewCompetitor] = useState("");

    // Smart Matching Config
    const [matchConfig, setMatchConfig] = useState<BrandMatchConfig>({
        fuzzyThreshold: 0.8,
        industry: "",
        misspellings: [],
        excludeKeywords: [],
        products: [],
    });

    // Connect sources state
    const [sources, setSources] = useState({
        reddit: true,
        hackernews: true,
        google: true,
    });

    const handleNext = () => {
        if (step === "brand" && brandName) setStep("keywords");
        else if (step === "keywords" && keywords.length > 0) setStep("matching");
        else if (step === "matching") setStep("competitors");
        else if (step === "competitors") setStep("connect");
    };

    const handleBack = () => {
        if (step === "keywords") setStep("brand");
        else if (step === "matching") setStep("keywords");
        else if (step === "competitors") setStep("matching");
        else if (step === "connect") setStep("competitors");
    };

    const handleAddCompetitor = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (newCompetitor.trim() && !competitors.includes(newCompetitor.trim())) {
            setCompetitors([...competitors, newCompetitor.trim()]);
            setNewCompetitor("");
        }
    };

    const handleSubmit = () => {
        createBrand.mutate(
            {
                brandName,
                keywords,
                matchConfig: {
                    ...matchConfig,
                    misspellings: matchConfig.misspellings?.filter(Boolean),
                    excludeKeywords: matchConfig.excludeKeywords?.filter(Boolean),
                    products: matchConfig.products?.filter(Boolean),
                },
            },
            {
                onSuccess: (data) => {
                    navigate(`/brands/${data.slug}/dashboard?onboarding=true`);
                },
            }
        );
    };

    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center p-4">
            <div className="w-full max-w-2xl">
                {/* Progress Header */}
                <StepProgress steps={STEPS} currentStep={step} />

                <Card className="bg-zinc-900 border-zinc-800 shadow-2xl overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500" />

                    <CardContent className="p-8">
                        <AnimatePresence mode="wait">
                            {step === "brand" && (
                                <BrandStep
                                    brandName={brandName}
                                    setBrandName={setBrandName}
                                />
                            )}

                            {step === "keywords" && (
                                <KeywordsStep
                                    keywords={keywords}
                                    setKeywords={setKeywords}
                                />
                            )}

                            {step === "matching" && (
                                <MatchingStep
                                    matchConfig={matchConfig}
                                    setMatchConfig={setMatchConfig}
                                />
                            )}

                            {step === "competitors" && (
                                <CompetitorsStep
                                    competitors={competitors}
                                    setCompetitors={setCompetitors}
                                    newCompetitor={newCompetitor}
                                    setNewCompetitor={setNewCompetitor}
                                    onAddCompetitor={handleAddCompetitor}
                                />
                            )}

                            {step === "connect" && (
                                <ConnectStep sources={sources} setSources={setSources} />
                            )}
                        </AnimatePresence>

                        <div className="flex justify-between mt-8 pt-6 border-t border-zinc-800">
                            <Button
                                variant="ghost"
                                onClick={handleBack}
                                disabled={step === "brand"}
                                className="text-zinc-400 hover:text-white"
                            >
                                Back
                            </Button>

                            {step !== "connect" ? (
                                <Button
                                    onClick={handleNext}
                                    className="bg-blue-600 hover:bg-blue-500 min-w-[120px]"
                                    disabled={
                                        (step === "brand" && !brandName) ||
                                        (step === "keywords" && keywords.length === 0)
                                    }
                                >
                                    Next <ArrowRight className="w-4 h-4 ml-2" />
                                </Button>
                            ) : (
                                <div className="flex flex-col items-end gap-2">
                                    {createBrand.isError && (
                                        <p className="text-sm text-red-400">
                                            {(createBrand.error as any)?.response?.data?.message ?? "Failed to create brand"}
                                        </p>
                                    )}
                                    <Button
                                        onClick={handleSubmit}
                                        className="bg-emerald-600 hover:bg-emerald-500 min-w-[120px]"
                                        disabled={createBrand.isPending}
                                    >
                                        {createBrand.isPending ? "Creating..." : "Launch"}
                                    </Button>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {createBrand.isPending && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
                    <LoadingState message="Initializing your command center..." />
                </div>
            )}
        </div>
    );
}
