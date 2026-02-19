/**
 * Reports Page - Generate and Manage Brand Reports
 */

import { FileSpreadsheet, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReportsList } from "@/components/reports/ReportsList";
import { GenerateReportModal } from "@/components/reports/GenerateReportModal";
import { useReportsPage } from "@/hooks/reports";

export default function ReportsPage() {
    const {
        reports,
        loading,
        apiUrl,
        showGenerateModal,
        setShowGenerateModal,
        generating,
        handleGenerate,
        handleExportData,
        form
    } = useReportsPage();

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-white">Reports & Exports</h1>
                    <p className="text-zinc-400">Generate executive reports and export raw data</p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" onClick={() => handleExportData("csv")} className="gap-2 bg-zinc-900 border-zinc-700 text-zinc-300">
                        <FileSpreadsheet className="w-4 h-4" />
                        Export CSV
                    </Button>
                    <Button onClick={() => setShowGenerateModal(true)} className="gap-2 bg-blue-600 hover:bg-blue-500 text-white">
                        <Plus className="w-4 h-4" />
                        Generate Report
                    </Button>
                </div>
            </div>

            {/* Reports List */}
            <div className="bg-zinc-900/50 rounded-xl border border-zinc-800 overflow-hidden">
                <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
                    <h3 className="font-medium text-white">Generated Reports</h3>
                    <span className="text-xs text-zinc-500">{reports.length} reports</span>
                </div>

                <ReportsList
                    reports={reports}
                    loading={loading}
                    apiUrl={apiUrl}
                    onCreateFirst={() => setShowGenerateModal(true)}
                />
            </div>

            {/* Generate Modal */}
            <GenerateReportModal
                isOpen={showGenerateModal}
                onClose={() => setShowGenerateModal(false)}
                onSubmit={handleGenerate}
                generating={generating}
                {...form} // Spread form state props
            />
        </div>
    );
}
