/**
 * Enhanced Summary Cards with Glass Morphism and Animations
 * V4.0 Premium Dashboard Component
 */

import { motion } from "framer-motion";
import { Flame, MessageSquare, TrendingUp, DollarSign, Target, Thermometer } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";

import {
    type BrandSummaryResponse,
    type BrandSpikesResponse,
    type LiveMentionsResponse,
    type SentimentTrendPoint,
    type SpikeSample,
} from "@/types/api";

interface EnhancedSummaryCardsProps {
    summary?: BrandSummaryResponse;
    spikes?: BrandSpikesResponse;
    mentions?: LiveMentionsResponse;
    sentimentTrend?: SentimentTrendPoint[];
    spikeTimeline?: SpikeSample[];
    onViewAnalytics?: () => void;
    onViewLiveMentions?: () => void;
    onViewSpikes?: () => void;
}

const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: {
            delay: i * 0.1,
            duration: 0.5,
            ease: "easeOut",
        },
    }),
};

export function EnhancedSummaryCards({
    summary,
    spikes,
    mentions,
    sentimentTrend,
    spikeTimeline,
    onViewAnalytics,
    onViewLiveMentions,
    onViewSpikes,
}: EnhancedSummaryCardsProps) {
    // Fix: Use || instead of ?? to catch 0 as invalid (worker not running)
    const healthScore = summary?.healthScore || 50;
    const spikeScore = summary?.sentiment?.score ?? 0;
    const spikeDetected = summary?.spikeDetected ?? false;
    const mentionCount = mentions?.length ?? 0;
    const last24Count = spikes?.last24hCount ?? 0;
    const sentiment = summary?.sentiment;
    const totalSentiment = (sentiment?.positive ?? 0) + (sentiment?.neutral ?? 0) + (sentiment?.negative ?? 0);
    const positivePct = totalSentiment > 0 ? ((sentiment?.positive ?? 0) / totalSentiment) * 100 : 0;

    // Check if data is stale (>1 hour old)
    const dataAge = summary?.generatedAt ? Date.now() - new Date(summary.generatedAt).getTime() : Infinity;
    const isStale = dataAge > 60 * 60 * 1000; // 1 hour

    const lastUpdated = summary?.generatedAt
        ? formatDistanceToNow(new Date(summary.generatedAt), { addSuffix: true })
        : null;

    return (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Brand Health Card */}
            <GlassCard
                index={0}
                gradient="from-blue-500/20 via-blue-500/10 to-transparent"
                glowColor="blue"
            >
                <div className="flex items-start justify-between mb-3">
                    <h3 className="text-sm font-medium text-zinc-300">Brand Health</h3>
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                        <Thermometer className="h-4 w-4 text-blue-400" />
                    </div>
                </div>
                <AnimatedCounter value={healthScore} decimals={1} className="text-3xl font-bold text-white" />
                <div className="mt-3 space-y-1">
                    <ProgressBar label="Positive" value={positivePct} color="bg-emerald-500" />
                </div>
                <div className="mt-3 flex items-center justify-between">
                    <p className="text-xs text-zinc-500">
                        {lastUpdated ? `Updated ${lastUpdated}` : "Awaiting data"}
                    </p>
                    {isStale && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                            Stale
                        </span>
                    )}
                </div>
            </GlassCard>

            {/* Mentions Card */}
            <GlassCard
                index={1}
                gradient="from-purple-500/20 via-purple-500/10 to-transparent"
                glowColor="purple"
            >
                <div className="flex items-start justify-between mb-3">
                    <h3 className="text-sm font-medium text-zinc-300">Live Mentions</h3>
                    <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                        <MessageSquare className="h-4 w-4 text-purple-400" />
                    </div>
                </div>
                <AnimatedCounter value={mentionCount} className="text-3xl font-bold text-white" />
                <p className="mt-2 text-xs text-zinc-500">New mentions in last 60 minutes</p>
                <div className="mt-3 flex items-center gap-2">
                    <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-green-500" />
                    <span className="text-xs text-zinc-400">Real-time tracking</span>
                </div>
            </GlassCard>

            {/* Spike Detection Card */}
            <GlassCard
                index={2}
                gradient={spikeDetected ? "from-red-500/20 via-red-500/10 to-transparent" : "from-emerald-500/20 via-emerald-500/10 to-transparent"}
                glowColor={spikeDetected ? "red" : "emerald"}
            >
                <div className="flex items-start justify-between mb-3">
                    <h3 className="text-sm font-medium text-zinc-300">Spike Detection</h3>
                    <div className={`w-8 h-8 rounded-lg ${spikeDetected ? "bg-red-500/10 border-red-500/20" : "bg-emerald-500/10 border-emerald-500/20"} border flex items-center justify-center`}>
                        <motion.div
                            animate={spikeDetected ? { scale: [1, 1.2, 1] } : {}}
                            transition={{ duration: 1, repeat: spikeDetected ? Infinity : 0 }}
                        >
                            <Flame className={spikeDetected ? "h-4 w-4 text-red-400" : "h-4 w-4 text-emerald-400"} />
                        </motion.div>
                    </div>
                </div>
                <p className={`text-3xl font-bold ${spikeDetected ? "text-red-400" : "text-emerald-400"}`}>
                    {spikeDetected ? "Active" : "Stable"}
                </p>
                <p className="mt-2 text-xs text-zinc-500">
                    {spikeDetected ? "Unusual activity detected" : "Normal activity levels"}
                </p>
            </GlassCard>

            {/* 24h Spikes Card */}
            <GlassCard
                index={3}
                gradient="from-orange-500/20 via-orange-500/10 to-transparent"
                glowColor="orange"
            >
                <div className="flex items-start justify-between mb-3">
                    <h3 className="text-sm font-medium text-zinc-300">Spikes (24h)</h3>
                    <div className="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
                        <Flame className="h-4 w-4 text-orange-400" />
                    </div>
                </div>
                <AnimatedCounter value={last24Count} className="text-3xl font-bold text-white" />
                <p className="mt-2 text-xs text-zinc-500">Detected spikes in last 24 hours</p>
            </GlassCard>
        </div>
    );
}

/**
 * Quick Access Cards for V4.0 Features - Minimalist Professional Style
 */
export function QuickAccessCards() {
    const features = [
        {
            title: "Money Mode",
            description: "Identify leads with commercial intent and convert conversations to revenue",
            icon: DollarSign,
            link: "/money-mode",
            iconColor: "text-emerald-400",
            borderColor: "border-zinc-800 hover:border-emerald-500/30",
            accentColor: "emerald",
        },
        {
            title: "Crisis Monitor",
            description: "Real-time risk scoring and instant alerts for reputation management",
            icon: Thermometer,
            link: "/crisis",
            iconColor: "text-rose-400",
            borderColor: "border-zinc-800 hover:border-rose-500/30",
            accentColor: "rose",
        },
        {
            title: "Market Gap",
            description: "Discover competitor weaknesses and untapped market opportunities",
            icon: Target,
            link: "/market-gap",
            iconColor: "text-blue-400",
            borderColor: "border-zinc-800 hover:border-blue-500/30",
            accentColor: "blue",
        },
    ];

    const accentMap: Record<string, { bg: string; hover: string }> = {
        emerald: { bg: "bg-emerald-500/10", hover: "group-hover:bg-emerald-500/15" },
        rose: { bg: "bg-rose-500/10", hover: "group-hover:bg-rose-500/15" },
        blue: { bg: "bg-blue-500/10", hover: "group-hover:bg-blue-500/15" },
    };

    return (
        <div className="grid gap-4 md:grid-cols-3">
            {features.map((feature, i) => (
                <Link to={feature.link} key={feature.title} className="group block">
                    <motion.div
                        custom={i}
                        initial="hidden"
                        animate="visible"
                        variants={cardVariants}
                        whileHover={{ y: -4 }}
                        transition={{ type: "spring", stiffness: 300, damping: 25 }}
                        className={`
                            relative h-full rounded-xl border ${feature.borderColor}
                            bg-zinc-900/50 backdrop-blur-sm p-4
                            transition-all duration-300
                        `}
                    >
                        {/* Icon */}
                        <div className={`
                            w-10 h-10 rounded-lg ${accentMap[feature.accentColor].bg} ${accentMap[feature.accentColor].hover}
                            flex items-center justify-center mb-4 transition-colors duration-300
                        `}>
                            <feature.icon className={`h-5 w-5 ${feature.iconColor}`} strokeWidth={1.5} />
                        </div>

                        {/* Title */}
                        <h3 className="text-base font-semibold text-white mb-2 tracking-tight">
                            {feature.title}
                        </h3>

                        {/* Description */}
                        <p className="text-sm text-zinc-500 leading-relaxed mb-4">
                            {feature.description}
                        </p>

                        {/* CTA */}
                        <div className="flex items-center gap-2 text-xs font-medium text-zinc-500 group-hover:text-zinc-300 transition-colors">
                            <span>Open</span>
                            <svg
                                className="h-3.5 w-3.5 transform transition-transform duration-200 group-hover:translate-x-1"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                strokeWidth={2}
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </svg>
                        </div>
                    </motion.div>
                </Link>
            ))}
        </div>
    );
}

/**
 * Glass morphism card component with 3D tilt effect
 */
function GlassCard({
    children,
    index,
    gradient,
    glowColor,
}: {
    children: React.ReactNode;
    index: number;
    gradient: string;
    glowColor: string;
}) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [transform, setTransform] = useState({ rotateX: 0, rotateY: 0 });

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        setTransform({ rotateX, rotateY });
    };

    const handleMouseLeave = () => {
        setTransform({ rotateX: 0, rotateY: 0 });
    };

    const glowColors: Record<string, string> = {
        blue: "hover:shadow-blue-500/10",
        purple: "hover:shadow-purple-500/10",
        red: "hover:shadow-red-500/10",
        emerald: "hover:shadow-emerald-500/10",
        orange: "hover:shadow-orange-500/10",
    };

    return (
        <motion.div
            ref={cardRef}
            custom={index}
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{
                transform: `perspective(1000px) rotateX(${transform.rotateX}deg) rotateY(${transform.rotateY}deg)`,
                transformStyle: "preserve-3d",
            }}
            className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${gradient} border border-zinc-800/50 p-4 backdrop-blur-sm transition-all duration-200 hover:shadow-xl ${glowColors[glowColor] || ""}`}
        >
            {children}
        </motion.div>
    );
}

/**
 * Animated counter component
 */
function AnimatedCounter({
    value,
    decimals = 0,
    className = ""
}: {
    value: number;
    decimals?: number;
    className?: string;
}) {
    const [displayValue, setDisplayValue] = useState(0);

    useEffect(() => {
        const duration = 1000;
        const steps = 30;
        const increment = value / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= value) {
                setDisplayValue(value);
                clearInterval(timer);
            } else {
                setDisplayValue(current);
            }
        }, duration / steps);

        return () => clearInterval(timer);
    }, [value]);

    return <span className={className}>{displayValue.toFixed(decimals)}</span>;
}

/**
 * Progress bar component
 */
function ProgressBar({
    label,
    value,
    color
}: {
    label: string;
    value: number;
    color: string;
}) {
    return (
        <div className="flex items-center gap-2 text-xs">
            <span className="w-16 text-zinc-500">{label}</span>
            <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className={`h-full rounded-full ${color}`}
                />
            </div>
            <span className="w-10 text-right text-zinc-400">{value.toFixed(0)}%</span>
        </div>
    );
}

export { EnhancedSummaryCards as default };
