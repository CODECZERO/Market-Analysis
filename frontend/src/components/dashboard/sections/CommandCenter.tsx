/**
 * Command Center Section
 */

import { motion } from "framer-motion";
import { Sparkles, Wifi, WifiOff } from "lucide-react";
import { SectionHeader } from "@/components/shared";
import { MoneyFeed, CrisisPulse, Battlefield, LaunchPredictor } from "@/components/dashboard/command-center";

interface CommandCenterProps {
    isConnected: boolean;
    transformedMentions: any[];
    battlefieldData: any;
    launches: any;
    loading: {
        mentions: boolean;
        comparison: boolean;
        launches: boolean;
    };
    onDraftReply: (mention: any) => void;
}

export function CommandCenter({
    isConnected,
    transformedMentions,
    battlefieldData,
    launches,
    loading,
    onDraftReply
}: CommandCenterProps) {
    return (
        <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15, duration: 0.4 }}
        >
            <SectionHeader
                icon={Sparkles}
                title="Command Center"
                subtitle="Real-time strategic intelligence"
                badge={
                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium ${isConnected
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : "bg-zinc-800/80 text-zinc-500 border border-zinc-700"
                        }`}>
                        {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                        {isConnected ? "Live" : "Offline"}
                    </div>
                }
            />

            {/* Money & Crisis Grid */}
            <div className="grid gap-4 lg:grid-cols-2 mb-4">
                <MoneyFeed
                    mentions={transformedMentions}
                    onDraftReply={onDraftReply}
                    isLoading={loading.mentions}
                />
                <CrisisPulse
                    mentions={transformedMentions}
                    isLoading={loading.mentions}
                />
            </div>

            {/* Battlefield */}
            {battlefieldData && (
                <div className="mb-4">
                    <Battlefield
                        myBrand={battlefieldData.myBrand}
                        competitor={battlefieldData.competitor}
                        isLoading={loading.comparison}
                    />
                </div>
            )}

            {/* Launch Predictor */}
            <LaunchPredictor
                myLaunch={launches?.myLaunch ?? null}
                competitorLaunch={launches?.competitorLaunch ?? null}
                isLoading={loading.launches}
            />
        </motion.section>
    );
}
