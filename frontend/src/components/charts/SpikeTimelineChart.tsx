import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type SpikeSample } from "@/types/api";

interface SpikeTimelineChartProps {
  data: SpikeSample[];
}

export function SpikeTimelineChart({ data }: SpikeTimelineChartProps) {
  const hasData = data.length > 0;

  return (
    <Card className="border-zinc-800 bg-zinc-900/50">
      <CardHeader>
        <CardTitle className="text-base font-semibold text-white">Spike timeline (24h)</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        {hasData ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ left: 0, right: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.5} />
              <XAxis
                dataKey="timestamp"
                tick={{ fontSize: 12, fill: '#71717a' }}
                minTickGap={24}
                axisLine={{ stroke: '#27272a' }}
                tickLine={{ stroke: '#27272a' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#71717a' }}
                allowDecimals={false}
                axisLine={{ stroke: '#27272a' }}
                tickLine={{ stroke: '#27272a' }}
              />
              <Tooltip
                formatter={(value: number) => value.toFixed(0)}
                cursor={{ stroke: '#3f3f46' }}
                contentStyle={{
                  backgroundColor: '#18181b',
                  border: '1px solid #27272a',
                  borderRadius: '8px',
                  color: '#fafafa',
                }}
              />
              <Line type="monotone" dataKey="spikeScore" stroke="#ef4444" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="threshold" stroke="#6366f1" dot={false} strokeDasharray="4 4" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-zinc-500">
            No spike data available.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
