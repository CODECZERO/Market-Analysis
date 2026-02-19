/**
 * Admin Dashboard Hook
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import { BrandRecord } from "@/types/api";

export interface DashboardOverview {
    lastUpdated: string;
    totals: {
        users: number;
        monitors: number;
        mentionsToday: number;
        mentionsTotal: number;
    };
    today: {
        newSignups: number;
        activeUsers: number;
        mentionsScanned: number;
        avgSentiment: number | null;
    };
    growth: {
        signupsWoW: string;
        signupsMoM: string;
        activeUsersWoW: string;
    };
}

export interface UserAnalytics {
    totalUsers: number;
    signups24h: number;
    signups7d: number;
    signups30d: number;
    dau: number;
    wau: number;
    mau: number;
}

export interface SignupSource {
    source: string;
    count: number;
    percentage: number;
}

export interface RecentUser {
    id: string;
    email: string;
    name: string;
    signupDate: string;
    lastLogin: string | null;
    monitorsCount: number;
}

export function useAdminDashboard() {
    const navigate = useNavigate();
    const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();

    const [overview, setOverview] = useState<DashboardOverview | null>(null);
    const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null);
    const [signupSources, setSignupSources] = useState<SignupSource[]>([]);
    const [recentUsers, setRecentUsers] = useState<RecentUser[]>([]);
    const [recentBrands, setRecentBrands] = useState<BrandRecord[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showDeleteModal, setShowDeleteModal] = useState<{ type: 'user' | 'brand', id: string, name: string } | null>(null);

    // Check authentication and admin role
    useEffect(() => {
        if (!authLoading) {
            if (!isAuthenticated) {
                navigate("/login", { replace: true });
                return;
            }
            if (user?.role !== "admin") {
                navigate("/brands", { replace: true });
                return;
            }
            // User is authenticated admin, fetch data
            fetchAllData();
        }
    }, [authLoading, isAuthenticated, user, navigate]);

    const fetchAllData = async () => {
        setLoading(true);
        setError(null);

        try {
            const [overviewRes, analyticsRes, sourcesRes, usersRes, brandsRes] = await Promise.all([
                api.get("/api/v1/admin/dashboard/overview").catch(() => null),
                api.get("/api/v1/admin/analytics/users").catch(() => null),
                api.get("/api/v1/admin/analytics/signup-sources").catch(() => null),
                api.get("/api/v1/admin/users/recent").catch(() => null),
                api.get("/api/v1/admin/brands/recent").catch(() => null),
            ]);

            if (overviewRes?.data) setOverview(overviewRes.data);
            if (analyticsRes?.data) setUserAnalytics(analyticsRes.data);
            if (sourcesRes?.data) setSignupSources(sourcesRes.data.sources || []);
            if (usersRes?.data) setRecentUsers(usersRes.data.users || []);

            if (brandsRes?.data) {
                // Ensure we handle both array and object response wrappers
                const brandsData = Array.isArray(brandsRes.data)
                    ? brandsRes.data
                    : (brandsRes.data as any).brands || [];
                setRecentBrands(brandsData);
            }
        } catch (err: any) {
            console.error("Failed to fetch admin data:", err);
            setError("Failed to load admin data");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!showDeleteModal) return;

        try {
            const endpoint = showDeleteModal.type === 'user'
                ? `/api/v1/admin/users/${showDeleteModal.id}`
                : `/api/v1/admin/brands/${showDeleteModal.id}`;

            await api.delete(endpoint);

            // Refresh data
            fetchAllData();
            setShowDeleteModal(null);
        } catch (err) {
            console.error("Delete failed:", err);
            alert("Failed to delete item");
        }
    };

    return {
        user,
        authLoading,
        loading,
        error,
        overview,
        userAnalytics,
        signupSources,
        recentUsers,
        recentBrands,
        showDeleteModal,
        setShowDeleteModal,
        fetchAllData,
        handleDelete,
        handleLogout: logout
    };
}
