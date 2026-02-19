/**
 * Crisis Thermometer Page - Real-time Risk Monitoring
 * 
 * Connected to backend API for real crisis data.
 * Refactored to use extracted SRP-compliant components.
 */

import { motion } from "framer-motion";
import { TrendingUp, Activity } from "lucide-react";

import { useCrisisMonitor } from "@/hooks/crisis";
import {
    ThermometerGauge,
    VelocityGraph,
    AlertTimeline,
    MetricCard,
    CrisisHeader,
    CrisisHowItWorks,
    CrisisLoading,
    CrisisError,
} from "@/components/crisis";

const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.08 } }
};

const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } }
};

// Helper to safely format dates
const formatAlertDate = (dateStr: string): string => {
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
            return 'Recently';
        }
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
        return 'Recently';
    }
};

export default function CrisisThermometerPage() {
    const {
        metrics,
        alerts,
        velocityData,
        isLive,
        setIsLive,
        loading,
        error,
        resolveAlert,
        refetch
    } = useCrisisMonitor();

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-6 p-4 md:p-6 pb-24 bg-[#0a0a0b] min-h-screen text-white"
        >
            <CrisisHeader isLive={isLive} onToggleLive={() => setIsLive(!isLive)} />

            {loading ? (
                <CrisisLoading />
            ) : error ? (
                <CrisisError message={error} onRetry={refetch} />
            ) : (
                <>
                    {/* Main Grid - unified gap-6 for consistent spacing */}
                    <div className="grid lg:grid-cols-12 gap-6">
                        {/* Left Column: Thermometer + Metric Cards */}
                        <motion.div variants={itemVariants} className="lg:col-span-4 space-y-4">
                            <ThermometerGauge metrics={metrics} />

                            <div className="grid grid-cols-2 gap-3">
                                <MetricCard
                                    icon={<TrendingUp className="w-4 h-4" />}
                                    label="Viral Velocity"
                                    value={`${metrics.velocityMultiplier.toFixed(1)}x`}
                                    description="growth rate"
                                    color="blue"
                                />
                                <MetricCard
                                    icon={<Activity className="w-4 h-4" />}
                                    label="Sentiment Risk"
                                    value={`${Math.round(metrics.sentimentIntensity * 100)}%`}
                                    description="negative intensity"
                                    color="amber"
                                />
                            </div>
                        </motion.div>

                        {/* Right Column: Velocity Graph + Alerts */}
                        <div className="lg:col-span-8 space-y-4">
                            <motion.div variants={itemVariants}>
                                <VelocityGraph data={velocityData} />
                            </motion.div>
                            <motion.div variants={itemVariants}>
                                <AlertTimeline
                                    alerts={alerts}
                                    onResolve={resolveAlert}
                                    formatDate={formatAlertDate}
                                />
                            </motion.div>
                        </div>
                    </div>
                </>
            )}

            <CrisisHowItWorks />
        </motion.div>
    );
}
