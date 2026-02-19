/**
 * Reports Page Hook
 */

import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { api } from "@/lib/api";
import type { Report } from "@/components/reports/ReportsList";

export function useReportsPage() {
    const { brandId } = useParams<{ brandId: string }>();
    const [reports, setReports] = useState<Report[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [showGenerateModal, setShowGenerateModal] = useState(false);

    // Form state
    const [reportName, setReportName] = useState("");
    const [reportType, setReportType] = useState<"weekly" | "monthly" | "custom">("weekly");
    const [reportFormat, setReportFormat] = useState<"pdf" | "csv">("pdf");
    const [startDate, setStartDate] = useState(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]);
    const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);

    // White-label branding options
    const [useWhiteLabel, setUseWhiteLabel] = useState(false);
    const [companyName, setCompanyName] = useState("");
    const [primaryColor, setPrimaryColor] = useState("#3b82f6");
    const [logoUrl, setLogoUrl] = useState("");
    const [email, setEmail] = useState("");

    // Expose apiUrl for components that might need it (though they should really use api client)
    // Deprecated: components should use api client or hook data
    const apiUrl = api.defaults.baseURL || "";

    useEffect(() => {
        if (brandId) fetchReports();
    }, [brandId]);

    const fetchReports = async () => {
        try {
            const res = await api.get(`/api/brands/${brandId}/reports`);
            setReports(res.data.data?.reports || []);
        } catch (error) {
            console.error("Failed to fetch reports:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        setGenerating(true);

        try {
            await api.post(`/api/brands/${brandId}/reports`, {
                name: reportName,
                type: reportType,
                format: reportFormat,
                startDate,
                endDate,
                includeCompetitors: true,
                branding: useWhiteLabel ? {
                    companyName,
                    primaryColor,
                    logoUrl: logoUrl || undefined
                } : undefined,
                email: email || undefined
            });

            setShowGenerateModal(false);
            setReportName("");
            fetchReports();
        } catch (error) {
            console.error("Failed to generate report:", error);
        } finally {
            setGenerating(false);
        }
    };

    const handleExportData = async (format: "json" | "csv") => {
        try {
            const res = await api.post(`/api/brands/${brandId}/reports/export`, {
                format,
                startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                endDate: new Date().toISOString()
            }, {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(res.data);
            const a = document.createElement("a");
            a.href = url;
            a.download = `brand-export-${format}-${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (error) {
            console.error("Export failed:", error);
        }
    };

    return {
        brandId,
        reports,
        loading,
        apiUrl,
        showGenerateModal,
        setShowGenerateModal,
        generating,
        handleGenerate,
        handleExportData,
        form: {
            reportName, setReportName,
            reportType, setReportType,
            reportFormat, setReportFormat,
            startDate, setStartDate,
            endDate, setEndDate,
            email, setEmail,
            useWhiteLabel, setUseWhiteLabel,
            companyName, setCompanyName,
            primaryColor, setPrimaryColor,
            logoUrl, setLogoUrl,
        }
    };
}
