/**
 * Sentiment Comparison Bar Chart
 * 
 * Stacked bar chart comparing sentiment across brand and competitors
 */

import { TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, Tooltip } from "recharts";

interface SentimentData {
    name: string;
    positive: number;
    neutral: number;
    negative: number;
}

interface SentimentComparisonChartProps {
    data: SentimentData[];
}

export function SentimentComparisonChart({ data }: SentimentComparisonChartProps) {
    if (!data || data.length === 0) return null;

    return (
        <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader className="pb-2">
                <CardTitle className="text-base font-semibold text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                    Sentiment Comparison
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.5} vertical={false} />
                        <XAxis
                            dataKey="name"
                            tick={{ fill: '#71717a', fontSize: 12 }}
                            axisLine={{ stroke: '#27272a' }}
                            tickLine={false}
                        />
                        <YAxis
                            tick={{ fill: '#71717a', fontSize: 12 }}
                            axisLine={{ stroke: '#27272a' }}
                            tickLine={false}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#18181b',
                                border: '1px solid #27272a',
                                borderRadius: '8px',
                                color: '#fafafa'
                            }}
                            cursor={{ fill: '#27272a', opacity: 0.4 }}
                        />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        <Bar dataKey="positive" stackId="a" fill="#22c55e" radius={[0, 0, 4, 4]} name="Positive" />
                        <Bar dataKey="neutral" stackId="a" fill="#71717a" name="Neutral" />
                        <Bar dataKey="negative" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} name="Negative" />
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
