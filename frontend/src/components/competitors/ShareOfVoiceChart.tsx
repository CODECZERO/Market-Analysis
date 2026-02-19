/**
 * Share of Voice Pie Chart
 * 
 * Displays market share/voice distribution between brand and competitors
 */

import { BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"];

interface ShareOfVoiceData {
    name: string;
    value: number;
    color?: string;
}

interface ShareOfVoiceChartProps {
    data: ShareOfVoiceData[];
}

export function ShareOfVoiceChart({ data }: ShareOfVoiceChartProps) {
    if (!data || data.length === 0) return null;

    return (
        <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader className="pb-2">
                <CardTitle className="text-base font-semibold text-white flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-blue-400" />
                    Share of Voice
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={90}
                            paddingAngle={5}
                            dataKey="value"
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            stroke="none"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#18181b',
                                border: '1px solid #27272a',
                                borderRadius: '8px',
                                color: '#fafafa'
                            }}
                            itemStyle={{ color: '#fafafa' }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
