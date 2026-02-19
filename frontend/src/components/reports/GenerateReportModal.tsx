/**
 * Generate Report Modal Component
 * 
 * Modal form for generating new reports with white-label options
 */

import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Building2, Palette, Image } from "lucide-react";
import { Button } from "@/components/ui/button";

interface GenerateReportModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    generating: boolean;
    // Form state
    reportName: string;
    setReportName: (v: string) => void;
    reportType: "weekly" | "monthly" | "custom";
    setReportType: (v: "weekly" | "monthly" | "custom") => void;
    reportFormat: "pdf" | "csv";
    setReportFormat: (v: "pdf" | "csv") => void;
    startDate: string;
    setStartDate: (v: string) => void;
    endDate: string;
    setEndDate: (v: string) => void;
    email: string;
    setEmail: (v: string) => void;
    // White-label
    useWhiteLabel: boolean;
    setUseWhiteLabel: (v: boolean) => void;
    companyName: string;
    setCompanyName: (v: string) => void;
    primaryColor: string;
    setPrimaryColor: (v: string) => void;
    logoUrl: string;
    setLogoUrl: (v: string) => void;
}

export function GenerateReportModal({
    isOpen,
    onClose,
    onSubmit,
    generating,
    reportName,
    setReportName,
    reportType,
    setReportType,
    reportFormat,
    setReportFormat,
    startDate,
    setStartDate,
    endDate,
    setEndDate,
    email,
    setEmail,
    useWhiteLabel,
    setUseWhiteLabel,
    companyName,
    setCompanyName,
    primaryColor,
    setPrimaryColor,
    logoUrl,
    setLogoUrl,
}: GenerateReportModalProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-md shadow-2xl relative max-h-[90vh] overflow-y-auto"
                    >
                        <h2 className="text-xl font-semibold text-white mb-6">Generate New Report</h2>

                        <form onSubmit={onSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Report Name</label>
                                <input
                                    type="text"
                                    required
                                    value={reportName}
                                    onChange={(e) => setReportName(e.target.value)}
                                    placeholder="e.g., Weekly Summary - Oct 2024"
                                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-400 mb-1">Type</label>
                                    <select
                                        value={reportType}
                                        onChange={(e) => setReportType(e.target.value as "weekly" | "monthly" | "custom")}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                    >
                                        <option value="weekly">Weekly</option>
                                        <option value="monthly">Monthly</option>
                                        <option value="custom">Custom</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-zinc-400 mb-1">Format</label>
                                    <select
                                        value={reportFormat}
                                        onChange={(e) => setReportFormat(e.target.value as "pdf" | "csv")}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                    >
                                        <option value="pdf">PDF Document</option>
                                        <option value="csv">CSV Spreadsheet</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-400 mb-1">Start Date</label>
                                    <input
                                        type="date"
                                        required
                                        value={startDate}
                                        onChange={(e) => setStartDate(e.target.value)}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-zinc-400 mb-1">End Date</label>
                                    <input
                                        type="date"
                                        required
                                        value={endDate}
                                        onChange={(e) => setEndDate(e.target.value)}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Email Notification (Optional)</label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="Send report to..."
                                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                />
                            </div>

                            {/* White-Label Branding Section */}
                            <div className="border-t border-zinc-800 pt-4 mt-4">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <Building2 className="w-4 h-4 text-purple-400" />
                                        <span className="text-sm font-medium text-white">White-Label Branding</span>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={useWhiteLabel}
                                            onChange={(e) => setUseWhiteLabel(e.target.checked)}
                                            className="sr-only peer"
                                        />
                                        <div className="w-9 h-5 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-500" />
                                    </label>
                                </div>

                                {useWhiteLabel && (
                                    <div className="space-y-3 animate-in fade-in slide-in-from-top-2">
                                        <div>
                                            <label className="block text-xs font-medium text-zinc-400 mb-1">Company Name</label>
                                            <input
                                                type="text"
                                                value={companyName}
                                                onChange={(e) => setCompanyName(e.target.value)}
                                                placeholder="Your Company Inc."
                                                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                                            />
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            <div>
                                                <label className="block text-xs font-medium text-zinc-400 mb-1">
                                                    <Palette className="w-3 h-3 inline mr-1" />
                                                    Brand Color
                                                </label>
                                                <div className="flex gap-2">
                                                    <input
                                                        type="color"
                                                        value={primaryColor}
                                                        onChange={(e) => setPrimaryColor(e.target.value)}
                                                        className="w-10 h-8 rounded border border-zinc-700 cursor-pointer"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={primaryColor}
                                                        onChange={(e) => setPrimaryColor(e.target.value)}
                                                        className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-2 py-1 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-zinc-400 mb-1">
                                                    <Image className="w-3 h-3 inline mr-1" />
                                                    Logo URL
                                                </label>
                                                <input
                                                    type="url"
                                                    value={logoUrl}
                                                    onChange={(e) => setLogoUrl(e.target.value)}
                                                    placeholder="https://..."
                                                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-2 py-1 text-xs text-white focus:outline-none focus:border-purple-500"
                                                />
                                            </div>
                                        </div>
                                        <p className="text-xs text-zinc-500">
                                            Your branding will appear on the report header and footer.
                                        </p>
                                    </div>
                                )}
                            </div>

                            <div className="flex justify-end gap-3 mt-8">
                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={onClose}
                                    className="text-zinc-400 hover:text-white"
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    disabled={generating}
                                    className="bg-blue-600 hover:bg-blue-500 text-white min-w-[100px]"
                                >
                                    {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Generate"}
                                </Button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
