/**
 * Analytics Section
 */

import { TrendingUp } from "lucide-react";
import { SectionHeader } from "@/components/shared";
import { SentimentTrendChart } from "@/components/charts/SentimentTrendChart";
import { SpikeTimelineChart } from "@/components/charts/SpikeTimelineChart";

interface AnalyticsSectionProps {
    sentimentTrend: any[];
    spikeTimeline: any[];
}

export function AnalyticsSection({ sentimentTrend, spikeTimeline }: AnalyticsSectionProps) {
    return (
        <section>
            <SectionHeader
                icon={TrendingUp}
                title="Analytics"
                subtitle="Sentiment trends and activity spikes"
            />
            <div className="grid gap-4 lg:grid-cols-2">
                <SentimentTrendChart data={sentimentTrend} />
                <SpikeTimelineChart data={spikeTimeline} />
            </div>
        </section>
    );
}
