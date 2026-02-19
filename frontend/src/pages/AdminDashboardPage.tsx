/**
 * Admin Dashboard Page
 */

import { motion } from "framer-motion";
import {
    Users, BarChart3, Activity, Target,
    TrendingUp, UserPlus
} from "lucide-react";

import { useAdminDashboard } from "@/hooks/admin/useAdminDashboard";
import {
    KPICard,
    MetricBar,
    SignupSourcesChart,
    RecentUsersTable,
    RecentBrandsTable,
    DashboardHeader,
    DeleteConfirmModal
} from "@/components/admin";

export default function AdminDashboardPage() {
    const {
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
        handleLogout
    } = useAdminDashboard();

    // Loading state
    if (authLoading || loading) {
        return (
            <div className="min-h-screen bg-[#0a0a0b] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-2 border-zinc-700 border-t-purple-500 rounded-full animate-spin" />
                    <p className="text-zinc-500 text-sm">Loading admin dashboard...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="min-h-screen bg-[#0a0a0b] flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400 mb-4">{error}</p>
                    <button
                        onClick={fetchAllData}
                        className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg text-sm"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    // Dashboard
    return (
        <div className="min-h-screen bg-[#0a0a0b] text-white">
            <DashboardHeader
                user={user}
                lastUpdated={overview?.lastUpdated}
                onLogout={handleLogout}
            />

            <main className="p-8 max-w-7xl mx-auto space-y-8">
                {/* KPI Cards */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
                >
                    <KPICard
                        icon={<Users className="h-5 w-5 text-purple-400" />}
                        title="Total Users"
                        value={overview?.totals.users || 0}
                        growth={overview?.growth.signupsMoM}
                        color="purple"
                    />
                    <KPICard
                        icon={<UserPlus className="h-5 w-5 text-emerald-400" />}
                        title="Today's Signups"
                        value={overview?.today.newSignups || 0}
                        color="emerald"
                    />
                    <KPICard
                        icon={<Activity className="h-5 w-5 text-blue-400" />}
                        title="Active Users (DAU)"
                        value={userAnalytics?.dau || 0}
                        color="blue"
                    />
                    <KPICard
                        icon={<Target className="h-5 w-5 text-amber-400" />}
                        title="Total Monitors"
                        value={overview?.totals.monitors || 0}
                        color="amber"
                    />
                </motion.div>

                {/* User Metrics Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 lg:grid-cols-2 gap-6"
                >
                    {/* User Engagement */}
                    <div className="bg-gradient-to-br from-zinc-900 via-zinc-900 to-purple-950/10 rounded-xl p-6 border border-zinc-800">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-purple-400" />
                            User Engagement
                        </h2>
                        <div className="space-y-4">
                            <MetricBar label="Daily Active (DAU)" value={userAnalytics?.dau || 0} max={userAnalytics?.mau || 100} color="purple" />
                            <MetricBar label="Weekly Active (WAU)" value={userAnalytics?.wau || 0} max={userAnalytics?.mau || 100} color="blue" />
                            <MetricBar label="Monthly Active (MAU)" value={userAnalytics?.mau || 0} max={userAnalytics?.mau || 100} color="emerald" />
                        </div>
                    </div>

                    {/* Signup Sources */}
                    <div className="bg-gradient-to-br from-zinc-900 via-zinc-900 to-blue-950/10 rounded-xl p-6 border border-zinc-800">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-blue-400" />
                            Signup Sources (30d)
                        </h2>
                        <SignupSourcesChart sources={signupSources} />
                    </div>
                </motion.div>

                {/* Recent Users Table */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <RecentUsersTable
                        users={recentUsers}
                        onDelete={(id, name) => setShowDeleteModal({ type: 'user', id, name })}
                    />
                </motion.div>

                {/* Recent Brands Table */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <RecentBrandsTable
                        brands={recentBrands}
                        onDelete={(id, name) => setShowDeleteModal({ type: 'brand', id, name })}
                    />
                </motion.div>
            </main>

            {/* Delete Confirmation Modal */}
            {showDeleteModal && (
                <DeleteConfirmModal
                    data={showDeleteModal}
                    onConfirm={handleDelete}
                    onClose={() => setShowDeleteModal(null)}
                />
            )}
        </div>
    );
}
