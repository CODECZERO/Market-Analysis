/**
 * Analysis Panel - Shows detailed AI analysis results
 * Features real-time updates and interactive visualizations
 */

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Brain, Target, Shield, Zap, Activity, BarChart3 } from 'lucide-react';
import { API_CONFIG } from '../config';

interface AnalysisData {
    technical?: {
        rsi: number;
        macd: number;
        signal: string;
    };
    sentiment?: {
        news: { score: number; label: string };
        social: { score: number; label: string };
    };
    decision?: {
        rating: string;
        confidence: number;
        entry_price: number;
        stop_loss: number;
        target_1: number;
    };
}

interface Props {
    symbol: string;
}

export default function ModernAnalysisPanel({ symbol }: Props) {
    const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (symbol) {
            fetchAnalysis();
        }
    }, [symbol]);

    const fetchAnalysis = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/stocks/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol })
            });
            const data = await response.json();
            if (data.success) {
                setAnalysis(data.analysis);
            }
        } catch (error) {
            // Use mock data for demo
            setAnalysis({
                technical: { rsi: 68, macd: 12.5, signal: 'BUY' },
                sentiment: {
                    news: { score: 0.75, label: 'POSITIVE' },
                    social: { score: 0.62, label: 'POSITIVE' }
                },
                decision: {
                    rating: 'STRONG_BUY',
                    confidence: 0.87,
                    entry_price: 2420,
                    stop_loss: 2310,
                    target_1: 2850
                }
            });
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-12 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-white font-semibold">Analyzing {symbol}...</p>
                    <p className="text-sm text-slate-400 mt-1">Running AI models</p>
                </div>
            </div>
        );
    }

    if (!analysis) return null;

    const getRatingColor = (rating: string) => {
        if (rating.includes('BUY')) return 'from-emerald-500 to-teal-500';
        if (rating.includes('SELL')) return 'from-rose-500 to-pink-500';
        return 'from-slate-500 to-gray-500';
    };

    return (
        <div className="space-y-6">
            {/* Rating Card */}
            <div className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 backdrop-blur-xl rounded-2xl border border-emerald-500/20 p-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                            <Brain className="w-6 h-6 text-emerald-400" />
                            AI Recommendation
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">Confidence: {(analysis.decision?.confidence! * 100).toFixed(0)}%</p>
                    </div>
                    <div className={`px-6 py-3 rounded-xl bg-gradient-to-r ${getRatingColor(analysis.decision?.rating!)} text-white font-bold text-lg shadow-lg`}>
                        {analysis.decision?.rating.replace('_', ' ')}
                    </div>
                </div>

                {/* Price Targets */}
                <div className="grid grid-cols-3 gap-4 mt-6">
                    <div className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-blue-500/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Target className="w-4 h-4 text-blue-400" />
                            <span className="text-xs text-slate-400">Entry Price</span>
                        </div>
                        <div className="text-2xl font-bold text-blue-400">₹{analysis.decision?.entry_price}</div>
                    </div>

                    <div className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-emerald-500/20">
                        <div className="flex items-center gap-2 mb-2">
                            <TrendingUp className="w-4 h-4 text-emerald-400" />
                            <span className="text-xs text-slate-400">Target</span>
                        </div>
                        <div className="text-2xl font-bold text-emerald-400">₹{analysis.decision?.target_1}</div>
                    </div>

                    <div className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-rose-500/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Shield className="w-4 h-4 text-rose-400" />
                            <span className="text-xs text-slate-400">Stop Loss</span>
                        </div>
                        <div className="text-2xl font-bold text-rose-400">₹{analysis.decision?.stop_loss}</div>
                    </div>
                </div>
            </div>

            {/* Technical Indicators */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <BarChart3 className="w-5 h-5 text-purple-400" />
                    Technical Indicators
                </h3>

                <div className="space-y-4">
                    <div className="bg-white/5 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-slate-400">RSI (14)</span>
                            <span className="text-white font-semibold">{analysis.technical?.rsi}</span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all"
                                style={{ width: `${analysis.technical?.rsi}%` }}
                            />
                        </div>
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                            <span>Oversold</span>
                            <span>Overbought</span>
                        </div>
                    </div>

                    <div className="bg-white/5 rounded-xl p-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-400">MACD</span>
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${(analysis.technical?.macd ?? 0) > 0
                                ? 'bg-emerald-500/20 text-emerald-400'
                                : 'bg-rose-500/20 text-rose-400'
                                }`}>
                                {(analysis.technical?.macd ?? 0) > 0 ? 'BULLISH' : 'BEARISH'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Sentiment Analysis */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <Activity className="w-5 h-5 text-yellow-400" />
                    Sentiment Analysis
                </h3>

                <div className="space-y-3">
                    {[
                        { label: 'News Sentiment', data: analysis.sentiment?.news, icon: '📰' },
                        { label: 'Social Media', data: analysis.sentiment?.social, icon: '💬' }
                    ].map((item, i) => (
                        <div key={i} className="bg-white/5 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-slate-400 flex items-center gap-2">
                                    <span>{item.icon}</span>
                                    {item.label}
                                </span>
                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${item.data?.label === 'POSITIVE'
                                    ? 'bg-emerald-500/20 text-emerald-400'
                                    : item.data?.label === 'NEGATIVE'
                                        ? 'bg-rose-500/20 text-rose-400'
                                        : 'bg-slate-500/20 text-slate-400'
                                    }`}>
                                    {item.data?.label}
                                </span>
                            </div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all ${item.data?.score! > 0
                                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500'
                                        : 'bg-gradient-to-r from-rose-500 to-pink-500'
                                        }`}
                                    style={{ width: `${Math.abs(item.data?.score! * 100)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Action Button */}
            <button className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl font-semibold text-white hover:shadow-lg hover:shadow-emerald-500/50 transition-all hover:scale-[1.02] flex items-center justify-center gap-2">
                <Zap className="w-5 h-5" />
                Execute Trade
            </button>
        </div>
    );
}
