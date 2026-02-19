"""
Interactive Stock Chart Component with TradingView - like UI
Uses Recharts for visualization
"""

import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, TrendingDown, Activity, Calendar } from 'lucide-react';

interface ChartData {
    date: string;
    price: number;
    volume: number;
    ma20?: number;
    ma50?: number;
}

interface Props {
    symbol: string;
    interval?: '1d' | '1w' | '1m';
}

export default function StockChart({ symbol, interval = '1d' }: Props) {
    const [data, setData] = useState<ChartData[]>([]);
    const [chartType, setChartType] = useState<'line' | 'area' | 'candle'>('area');
    const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('1M');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchChartData();
    }, [symbol, timeframe]);

    const fetchChartData = async () => {
        setLoading(true);
        // Mock data for demo
        const mockData: ChartData[] = [];
        const basePrice = 2400;
        const days = timeframe === '1M' ? 30 : timeframe === '3M' ? 90 : timeframe === '6M' ? 180 : 365;

        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));

            const randomChange = (Math.random() - 0.5) * 50;
            const price = basePrice + randomChange + (i * 2);

            mockData.push({
                date: date.toISOString().split('T')[0],
                price: Math.round(price * 100) / 100,
                volume: Math.floor(Math.random() * 1000000) + 500000,
                ma20: i >= 20 ? price * 0.98 : undefined,
                ma50: i >= 50 ? price * 0.97 : undefined
            });
        }

        setData(mockData);
        setLoading(false);
    };

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-slate-900 border border-white/20 rounded-lg p-3 shadow-xl">
                    <p className="text-xs text-slate-400 mb-2">{data.date}</p>
                    <p className="text-white font-semibold">₹{data.price.toLocaleString()}</p>
                    <p className="text-xs text-slate-400 mt-1">Vol: {(data.volume / 1000000).toFixed(2)}M</p>
                    {data.ma20 && <p className="text-xs text-blue-400">MA20: ₹{data.ma20.toFixed(2)}</p>}
                    {data.ma50 && <p className="text-xs text-purple-400">MA50: ₹{data.ma50.toFixed(2)}</p>}
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-12 flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-white">Loading chart...</p>
                </div>
            </div>
        );
    }

    const currentPrice = data[data.length - 1]?.price || 0;
    const prevPrice = data[0]?.price || 0;
    const priceChange = currentPrice - prevPrice;
    const priceChangePercent = (priceChange / prevPrice) * 100;

    return (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-2xl font-bold text-white">{symbol}</h3>
                    <div className="flex items-center gap-4 mt-2">
                        <span className="text-3xl font-bold text-white">₹{currentPrice.toLocaleString()}</span>
                        <span className={`flex items-center gap-1 text-lg font-semibold ${priceChange >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {priceChange >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                            {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
                        </span>
                    </div>
                </div>

                {/* Controls */}
                <div className="flex gap-2">
                    {/* Timeframe */}
                    {(['1M', '3M', '6M', '1Y', 'ALL'] as const).map((tf) => (
                        <button
                            key={tf}
                            onClick={() => setTimeframe(tf)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${timeframe === tf
                                    ? 'bg-emerald-500 text-white'
                                    : 'bg-white/5 text-slate-400 hover:bg-white/10'
                                }`}
                        >
                            {tf}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chart Type Toggle */}
            <div className="flex gap-2 mb-4">
                {[
                    { type: 'area' as const, label: 'Area', icon: Activity },
                    { type: 'line' as const, label: 'Line', icon: TrendingUp }
                ].map(({ type, label, icon: Icon }) => (
                    <button
                        key={type}
                        onClick={() => setChartType(type)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-all ${chartType === type
                                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                                : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-transparent'
                            }`}
                    >
                        <Icon className="w-3 h-3" />
                        {label}
                    </button>
                ))}
            </div>

            {/* Main Chart */}
            <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                    {chartType === 'area' ? (
                        <AreaChart data={data}>
                            <defs>
                                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                                domain={['dataMin - 50', 'dataMax + 50']}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="price"
                                stroke="#10b981"
                                strokeWidth={2}
                                fill="url(#colorPrice)"
                            />
                            {data[0]?.ma20 && (
                                <Line type="monotone" dataKey="ma20" stroke="#3b82f6" strokeWidth={1.5} dot={false} />
                            )}
                            {data[0]?.ma50 && (
                                <Line type="monotone" dataKey="ma50" stroke="#a855f7" strokeWidth={1.5} dot={false} />
                            )}
                        </AreaChart>
                    ) : (
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                                domain={['dataMin - 50', 'dataMax + 50']}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Line
                                type="monotone"
                                dataKey="price"
                                stroke="#10b981"
                                strokeWidth={2}
                                dot={false}
                            />
                            {data[0]?.ma20 && (
                                <Line type="monotone" dataKey="ma20" stroke="#3b82f6" strokeWidth={1.5} dot={false} />
                            )}
                            {data[0]?.ma50 && (
                                <Line type="monotone" dataKey="ma50" stroke="#a855f7" strokeWidth={1.5} dot={false} />
                            )}
                        </LineChart>
                    )}
                </ResponsiveContainer>
            </div>

            {/* Volume Chart */}
            <div className="h-24 mt-4">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data}>
                        <XAxis dataKey="date" hide />
                        <YAxis hide />
                        <Tooltip
                            content={({ active, payload }: any) => {
                                if (active && payload && payload.length) {
                                    return (
                                        <div className="bg-slate-900 border border-white/20 rounded-lg p-2 text-xs text-white">
                                            Vol: {(payload[0].value / 1000000).toFixed(2)}M
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <Bar dataKey="volume" fill="#64748b" opacity={0.3} />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Legend */}
            <div className="flex items-center gap-6 mt-4 text-xs">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-0.5 bg-emerald-500" />
                    <span className="text-slate-400">Price</span>
                </div>
                {data[0]?.ma20 && (
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-0.5 bg-blue-500" />
                        <span className="text-slate-400">MA20</span>
                    </div>
                )}
                {data[0]?.ma50 && (
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-0.5 bg-purple-500" />
                        <span className="text-slate-400">MA50</span>
                    </div>
                )}
            </div>
        </div>
    );
}
