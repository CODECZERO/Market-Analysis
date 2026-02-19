/**
 * Analytics Charts Component
 */

import { TrendingUp, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SentimentTrendChart } from "@/components/charts/SentimentTrendChart";
import { SpikeTimelineChart } from "@/components/charts/SpikeTimelineChart";

interface AnalyticsChartsProps {
    sentimentTrend: any[];
    spikeTimeline: any[];
}

export function AnalyticsCharts({ sentimentTrend, spikeTimeline }: AnalyticsChartsProps) {
    return (
        <div className="grid gap-6 lg:grid-cols-2">
            <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
                <CardHeader className="border-b border-zinc-800/50">
                    <CardTitle className="text-base font-semibold flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                            <TrendingUp className="h-4 w-4 text-blue-400" />
                        </div>
                        Sentiment Trend (7 Days)
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                    <SentimentTrendChart data={sentimentTrend} />
                </CardContent>
            </Card>

            <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
                <CardHeader className="border-b border-zinc-800/50">
                    <CardTitle className="text-base font-semibold flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                            <Zap className="h-4 w-4 text-amber-400" />
                        </div>
                        Spike Timeline
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                    <SpikeTimelineChart data={spikeTimeline} />
                </CardContent>
            </Card>
        </div>
    );
}
