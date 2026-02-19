/**
 * Reports List Component
 * 
 * Displays list of generated reports with download actions
 */

import { FileText, FileSpreadsheet, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Report {
    id: string;
    name: string;
    type: "daily" | "weekly" | "monthly" | "custom";
    format: "pdf" | "csv" | "excel" | "json";
    status: "pending" | "processing" | "completed" | "failed";
    url?: string;
    createdAt: string;
    startDate: string;
    endDate: string;
}

interface ReportsListProps {
    reports: Report[];
    loading: boolean;
    apiUrl: string;
    onCreateFirst: () => void;
}

export function ReportsList({ reports, loading, apiUrl, onCreateFirst }: ReportsListProps) {
    if (loading) {
        return (
            <div className="p-8 text-center text-zinc-500">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                Loading reports...
            </div>
        );
    }

    if (reports.length === 0) {
        return (
            <div className="p-12 text-center">
                <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center mx-auto mb-4 border border-zinc-700">
                    <FileText className="w-6 h-6 text-zinc-500" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">No Reports Yet</h3>
                <p className="text-sm text-zinc-400 mb-6 max-w-sm mx-auto">
                    Generate your first PDF report to share insights with your team or clients.
                </p>
                <Button onClick={onCreateFirst} variant="outline">
                    Create First Report
                </Button>
            </div>
        );
    }

    return (
        <div className="divide-y divide-zinc-800">
            {reports.map((report) => (
                <div key={report.id} className="p-4 flex items-center justify-between hover:bg-zinc-800/30 transition-colors">
                    <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center border ${report.format === 'pdf'
                                ? 'bg-red-500/10 border-red-500/20 text-red-500'
                                : 'bg-green-500/10 border-green-500/20 text-green-500'
                            }`}>
                            {report.format === 'pdf' ? <FileText className="w-5 h-5" /> : <FileSpreadsheet className="w-5 h-5" />}
                        </div>
                        <div>
                            <h4 className="font-medium text-white">{report.name}</h4>
                            <div className="flex items-center gap-3 text-xs text-zinc-500 mt-1">
                                <span className="capitalize">{report.type} Report</span>
                                <span>•</span>
                                <span>{new Date(report.createdAt).toLocaleDateString()}</span>
                                <span>•</span>
                                <span className={`capitalize ${report.status === 'completed' ? 'text-green-500' :
                                        report.status === 'failed' ? 'text-red-500' : 'text-amber-500'
                                    }`}>
                                    {report.status}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        {report.status === 'completed' && report.url && (
                            <a
                                href={`${apiUrl}${report.url}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition-colors"
                                title="Download"
                            >
                                <Download className="w-5 h-5" />
                            </a>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

export type { Report };
