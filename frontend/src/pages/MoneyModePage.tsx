/**
 * Money Mode Page - Lead Detection and Sales Intelligence
 * 
 * Displays commercial intent leads with animated cards and AI pitch generation.
 * Refactored to use extracted SRP-compliant components.
 */

import { useMoneyMode } from "@/hooks/leads";
import {
    MoneyHeader,
    LeadStats,
    LeadFeed,
    PitchGenerator,
} from "@/components/leads";

export default function MoneyModePage() {
    const {
        leads,
        stats,
        loading,
        error,
        selectedLead,
        generatingPitch,
        generatedPitch,
        fetchData,
        generatePitch,
        updateStatus,
        handleSelectLead,
    } = useMoneyMode();

    return (
        <div className="min-h-screen bg-[#0a0a0b] text-white p-4 md:p-6 pb-24">
            <div className="max-w-7xl mx-auto space-y-6">
                <MoneyHeader />
                <LeadStats stats={stats} leadCount={leads.length} />

                <div className="grid lg:grid-cols-3 gap-6">
                    <LeadFeed
                        leads={leads}
                        loading={loading}
                        error={error}
                        selectedLead={selectedLead}
                        onSelectLead={handleSelectLead}
                        onUpdateStatus={updateStatus}
                        onRetry={fetchData}
                    />

                    <PitchGenerator
                        selectedLead={selectedLead}
                        generatingPitch={generatingPitch}
                        generatedPitch={generatedPitch}
                        onGenerate={generatePitch}
                    />
                </div>
            </div>
        </div>
    );
}
