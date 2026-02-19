/**
 * Spike Detection Card
 */

import { Zap, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SpikeDetectionCardProps {
    spikeDetected: boolean;
    last24hCount: number;
    sentimentScore: number;
}

export function SpikeDetectionCard({ spikeDetected, last24hCount, sentimentScore }: SpikeDetectionCardProps) {
    return (
        <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
            <CardHeader className="border-b border-zinc-800/50">
                <CardTitle className="text-base font-semibold flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                        <Zap className="h-4 w-4 text-amber-400" />
                    </div>
                    Spike Detection
                </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">Status</span>
                    <span className={`text-sm font-medium flex items-center gap-2 ${spikeDetected ? 'text-amber-400' : 'text-emerald-400'}`}>
                        {spikeDetected ? (
                            <>
                                <Zap className="h-3.5 w-3.5" />
                                Spike Active
                            </>
                        ) : (
                            <>
                                <Activity className="h-3.5 w-3.5" />
                                Normal
                            </>
                        )}
                    </span>
                </div>
                <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">Last 24h</span>
                    <span className="text-sm font-medium text-white">{last24hCount} spikes</span>
                </div>
                <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">Score</span>
                    <span className="text-sm font-medium text-white">{sentimentScore.toFixed(2)}</span>
                </div>
            </CardContent>
        </Card>
    );
}
