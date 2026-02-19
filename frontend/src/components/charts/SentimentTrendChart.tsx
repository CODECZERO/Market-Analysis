import { useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type SentimentTrendPoint } from "@/types/api";

interface SentimentTrendChartProps {
  data: SentimentTrendPoint[];
  onDaysChange?: (days: number) => void;
}

const DAY_OPTIONS = [1, 3, 5, 7] as const;

export function SentimentTrendChart({ data, onDaysChange }: SentimentTrendChartProps) {
  const [selectedDays, setSelectedDays] = useState<number>(7);

  // Filter data based on selected days
  const filteredData = data.slice(-selectedDays);
  const hasData = filteredData.length > 0;

  const handleDaysChange = (days: number) => {
    setSelectedDays(days);
    onDaysChange?.(days);
  };

  return (
    <Card className="border-zinc-800 bg-zinc-900/50">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-semibold text-white">
          Sentiment trend ({selectedDays} {selectedDays === 1 ? "day" : "days"})
        </CardTitle>
        <div className="flex items-center gap-1">
          {DAY_OPTIONS.map((days) => (
            <button
              key={days}
              onClick={() => handleDaysChange(days)}
              className={`px-2 py-1 text-xs rounded transition-colors ${selectedDays === days
                  ? "bg-blue-600 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-300"
                }`}
            >
              {days}d
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="h-72">
        {hasData ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredData} margin={{ left: 0, right: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.5} />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12, fill: '#71717a' }}
                axisLine={{ stroke: '#27272a' }}
                tickLine={{ stroke: '#27272a' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#71717a' }}
                axisLine={{ stroke: '#27272a' }}
                tickLine={{ stroke: '#27272a' }}
                allowDecimals={false}
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3", stroke: '#3f3f46' }}
                contentStyle={{
                  backgroundColor: '#18181b',
                  border: '1px solid #27272a',
                  borderRadius: '8px',
                  color: '#fafafa',
                }}
              />
              <Area type="monotone" dataKey="positive" stroke="#22c55e" fill="#22c55e22" name="Positive" />
              <Area type="monotone" dataKey="neutral" stroke="#71717a" fill="#71717a22" name="Neutral" />
              <Area type="monotone" dataKey="negative" stroke="#ef4444" fill="#ef444422" name="Negative" />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-zinc-500">
            No sentiment data available for the selected period.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
