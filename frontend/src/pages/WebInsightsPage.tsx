/**
 * Web Insights Page
 * 
 * Deep dive analysis for brands using AI.
 */

import { AnimatePresence } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BrainCircuit, Crosshair } from "lucide-react";

import { useWebInsights } from "@/hooks/insights/useWebInsights";
import {
    InsightsHeader,
    DeepScanView,
    ExecutiveSummaryCard,
    OpportunitiesRiskGrid,
    RecommendedActionsList
} from "@/components/insights";

export default function WebInsightsPage() {
    const {
        brandId,
        data,
        loading,
        error,
        minTimeElapsed,
        selectedAction,
        setSelectedAction,
        handleTerminalComplete
    } = useWebInsights();

    // Show DeepScan terminal if loading or not completed animation
    if (loading || !minTimeElapsed || !data) {
        return (
            <DeepScanView
                loading={loading}
                error={error}
                minTimeElapsed={minTimeElapsed}
                onComplete={handleTerminalComplete}
                brandId={brandId || ''}
            />
        );
    }

    return (
        <div className="space-y-8 p-6 max-w-7xl mx-auto">
            {/* Header */}
            <InsightsHeader
                brandName={data.brand}
                brandId={brandId || ''}
            />

            <Tabs defaultValue="plan" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-zinc-900/50 border border-zinc-800 p-1">
                    <TabsTrigger value="plan" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white">
                        <BrainCircuit className="w-4 h-4 mr-2" />
                        Strategic Plan
                    </TabsTrigger>
                    <TabsTrigger value="action" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                        <Crosshair className="w-4 h-4 mr-2" />
                        Take Action
                    </TabsTrigger>
                </TabsList>

                <div className="mt-8">
                    <AnimatePresence mode="wait">
                        <TabsContent value="plan" className="space-y-6 focus-visible:outline-none">
                            {/* Summary Section */}
                            <ExecutiveSummaryCard analysis={data.analysis} />

                            {/* Opportunities & Risks */}
                            <OpportunitiesRiskGrid
                                opportunities={data.analysis.opportunities}
                                risks={data.analysis.risks}
                            />
                        </TabsContent>

                        <TabsContent value="action" className="focus-visible:outline-none">
                            <RecommendedActionsList
                                actions={data.analysis.recommended_actions}
                                sourceCount={data.sources.length}
                                selectedAction={selectedAction}
                                onSelectAction={setSelectedAction}
                            />
                        </TabsContent>
                    </AnimatePresence>
                </div>
            </Tabs>
        </div>
    );
}
