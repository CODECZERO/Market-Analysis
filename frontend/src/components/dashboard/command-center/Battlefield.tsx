import { useMemo } from "react";
import { TrendingUp, TrendingDown, Minus, Swords } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// =============================================================================
// TYPES
// =============================================================================

interface BrandData {
    name: string;
    mentionCount: number;
    avgSentiment: number;
    positiveCount: number;
    negativeCount: number;
    neutralCount: number;
    trend: "up" | "down" | "stable";
    isCompetitor: boolean;
}

interface BattlefieldProps {
    myBrand: BrandData;
    competitor: BrandData;
    isLoading?: boolean;
}

// =============================================================================
// BAR COMPARISON
// =============================================================================

function ComparisonBar({
    label,
    myValue,
    competitorValue,
    myLabel,
    competitorLabel,
    format = "number",
    inverted = false, // For sentiment, lower is worse
}: {
    label: string;
    myValue: number;
    competitorValue: number;
    myLabel: string;
    competitorLabel: string;
    format?: "number" | "percent" | "sentiment";
    inverted?: boolean;
}) {
    const total = Math.max(myValue + competitorValue, 1);
    const myPercent = (myValue / total) * 100;
    const competitorPercent = (competitorValue / total) * 100;

    // Determine winner
    const myWins = inverted ? myValue < competitorValue : myValue > competitorValue;
    const tie = myValue === competitorValue;

    const formatValue = (val: number) => {
        switch (format) {
            case "percent":
                return `${val.toFixed(0)}%`;
            case "sentiment":
                return `${(val * 100).toFixed(0)}%`;
            default:
                return val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val.toString();
        }
    };

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-zinc-400">
                <span>{label}</span>
                <span className={`font-medium ${myWins && !tie ? "text-emerald-400" : tie ? "text-zinc-400" : "text-red-400"}`}>
                    {myWins && !tie ? "You Win" : tie ? "Tied" : "They Win"}
                </span>
            </div>

            {/* Stacked Bar */}
            <div className="relative h-8 bg-zinc-800 rounded-lg overflow-hidden flex">
                {/* My Brand */}
                <div
                    className={`
            h-full flex items-center justify-center
            transition-all duration-500
            ${myWins && !tie ? "bg-emerald-600" : "bg-zinc-600"}
          `}
                    style={{ width: `${myPercent}%`, minWidth: myPercent > 5 ? "auto" : "20px" }}
                >
                    {myPercent > 15 && (
                        <span className="text-xs font-semibold text-white">
                            {formatValue(myValue)}
                        </span>
                    )}
                </div>

                {/* Competitor */}
                <div
                    className={`
            h-full flex items-center justify-center
            transition-all duration-500
            ${!myWins && !tie ? "bg-purple-600" : "bg-zinc-700"}
          `}
                    style={{ width: `${competitorPercent}%`, minWidth: competitorPercent > 5 ? "auto" : "20px" }}
                >
                    {competitorPercent > 15 && (
                        <span className="text-xs font-semibold text-white">
                            {formatValue(competitorValue)}
                        </span>
                    )}
                </div>
            </div>

            {/* Labels */}
            <div className="flex justify-between text-[10px]">
                <span className={`${myWins && !tie ? "text-emerald-400" : "text-zinc-500"}`}>
                    {myLabel}
                </span>
                <span className={`${!myWins && !tie ? "text-purple-400" : "text-zinc-500"}`}>
                    {competitorLabel}
                </span>
            </div>
        </div>
    );
}

// =============================================================================
// TREND INDICATOR
// =============================================================================

function TrendIndicator({ trend, label }: { trend: "up" | "down" | "stable"; label: string }) {
    const config = {
        up: { icon: TrendingUp, color: "text-emerald-400", bg: "bg-emerald-500/20" },
        down: { icon: TrendingDown, color: "text-red-400", bg: "bg-red-500/20" },
        stable: { icon: Minus, color: "text-zinc-400", bg: "bg-zinc-500/20" },
    };

    const { icon: Icon, color, bg } = config[trend];

    return (
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${bg}`}>
            <Icon className={`w-3 h-3 ${color}`} />
            <span className={`text-[10px] font-medium ${color}`}>{label}</span>
        </div>
    );
}

// =============================================================================
// BATTLEFIELD COMPONENT
// =============================================================================

export function Battlefield({ myBrand, competitor, isLoading }: BattlefieldProps) {
    const insight = useMemo(() => {
        const volumeWinner = myBrand.mentionCount > competitor.mentionCount ? "you" : "competitor";
        const sentimentWinner = myBrand.avgSentiment > competitor.avgSentiment ? "you" : "competitor";

        if (volumeWinner === "competitor" && sentimentWinner === "you") {
            return {
                text: "They're winning on Volume, but You're winning on Sentiment.",
                type: "mixed-positive" as const,
            };
        }
        if (volumeWinner === "you" && sentimentWinner === "competitor") {
            return {
                text: "You're winning on Volume, but they have better Sentiment.",
                type: "mixed-negative" as const,
            };
        }
        if (volumeWinner === "you" && sentimentWinner === "you") {
            return {
                text: "You're dominating on both Volume AND Sentiment!",
                type: "winning" as const,
            };
        }
        return {
            text: "They're ahead on both metrics. Time to step up!",
            type: "losing" as const,
        };
    }, [myBrand, competitor]);

    const insightConfig = {
        "mixed-positive": { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-400" },
        "mixed-negative": { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-400" },
        "winning": { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-400" },
        "losing": { bg: "bg-red-500/10", border: "border-red-500/30", text: "text-red-400" },
    };

    // Only show loading if we really have no data to show
    const isInitialLoading = isLoading && (!myBrand || !competitor);

    if (isInitialLoading) {
        return (
            <Card className="border-zinc-800 bg-zinc-900/50">
                <CardContent className="flex items-center justify-center h-48">
                    <div className="animate-pulse text-zinc-500">Analyzing battlefield...</div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-purple-950/20">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-bold flex items-center gap-2">
                        <Swords className="w-6 h-6 text-purple-400" />
                        Battlefield
                    </CardTitle>
                    <div className="flex items-center gap-2">
                        <TrendIndicator trend={myBrand.trend} label={myBrand.name} />
                        <span className="text-zinc-600">vs</span>
                        <TrendIndicator trend={competitor.trend} label={competitor.name} />
                    </div>
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                    Head-to-head competitive intelligence
                </p>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Strategic Insight */}
                <div className={`p-3 rounded-lg border ${insightConfig[insight.type].bg} ${insightConfig[insight.type].border}`}>
                    <p className={`text-sm font-medium ${insightConfig[insight.type].text}`}>
                        {insight.text}
                    </p>
                </div>

                {/* Brand Headers */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-emerald-500" />
                        <span className="text-sm font-semibold text-emerald-400">{myBrand.name}</span>
                    </div>
                    <Swords className="w-5 h-5 text-zinc-600" />
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-purple-400">{competitor.name}</span>
                        <div className="w-3 h-3 rounded-full bg-purple-500" />
                    </div>
                </div>

                {/* Comparison Bars */}
                <div className="space-y-5">
                    <ComparisonBar
                        label="Total Mentions (Volume)"
                        myValue={myBrand.mentionCount}
                        competitorValue={competitor.mentionCount}
                        myLabel={myBrand.name}
                        competitorLabel={competitor.name}
                    />

                    <ComparisonBar
                        label="Average Sentiment"
                        myValue={myBrand.avgSentiment}
                        competitorValue={competitor.avgSentiment}
                        myLabel={myBrand.name}
                        competitorLabel={competitor.name}
                        format="sentiment"
                    />

                    <ComparisonBar
                        label="Positive Mentions"
                        myValue={myBrand.positiveCount}
                        competitorValue={competitor.positiveCount}
                        myLabel={myBrand.name}
                        competitorLabel={competitor.name}
                    />

                    <ComparisonBar
                        label="Negative Mentions"
                        myValue={myBrand.negativeCount}
                        competitorValue={competitor.negativeCount}
                        myLabel={myBrand.name}
                        competitorLabel={competitor.name}
                        inverted={true}
                    />
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 gap-3 pt-4 border-t border-zinc-800">
                    <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                        <p className="text-[10px] uppercase tracking-wide text-emerald-500/80">Your Score</p>
                        <p className="text-2xl font-bold text-emerald-400">
                            {(((myBrand.avgSentiment + 1) / 2) * 100).toFixed(0)}
                        </p>
                    </div>
                    <div className="p-3 rounded-lg bg-purple-500/5 border border-purple-500/20">
                        <p className="text-[10px] uppercase tracking-wide text-purple-500/80">Their Score</p>
                        <p className="text-2xl font-bold text-purple-400">
                            {(((competitor.avgSentiment + 1) / 2) * 100).toFixed(0)}
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export default Battlefield;
