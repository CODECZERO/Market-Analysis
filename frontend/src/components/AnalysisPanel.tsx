/**
 * Analysis Panel Component
 * Displays comprehensive stock analysis results
 */

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Target, AlertTriangle, Info, BarChart3, Brain, Zap } from 'lucide-react';

interface Stock {
    id: string;
    symbol: string;
    exchange: string;
}

interface AnalysisData {
    current_price: number;
    technical_indicators: any;
    quant_signals: any;
    ml_predictions: any;
    phase1_what_why: any;
    phase2_when_where: any;
    phase3_recommendation: any;
    decision: any;
}

interface AnalysisPanelProps {
    stock: Stock;
}

export default function AnalysisPanel({ stock }: AnalysisPanelProps) {
    const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'llm' | 'ml'>('overview');

    useEffect(() => {
        fetchAnalysis();
    }, [stock]);

    const fetchAnalysis = async () => {
        try {
            setLoading(true);
            // In production, this would fetch from /api/stocks/analyze/:analysisId
            // For now, simulate with mock data
            setTimeout(() => {
                setAnalysis({
                    current_price: 2456.75,
                    technical_indicators: {
                        rsi_14: 38.2,
                        macd_bullish: true,
                        price_vs_sma50: 2.34,
                        adx_14: 28.5
                    },
                    quant_signals: {
                        momentum: { signal: 'LONG', percentile_rank: 72.5 },
                        mean_reversion: { signal: 'BUY', zscore: -1.8 },
                        regime: { regime: 'BULL', probability: 0.82 }
                    },
                    ml_predictions: {
                        lstm: { '30d': 2620, '90d': 2780, confidence: 0.78 },
                        xgboost: { signal: 'BUY', probability: 0.78 }
                    },
                    phase1_what_why: {
                        what: 'Stock consolidating after earnings with price stabilizing',
                        primary_cause: 'FUNDAMENTALS_SHIFT',
                        confidence: 78
                    },
                    phase2_when_where: {
                        entry_window: 'Next 5-7 trading days',
                        entry_trigger: 'Price dips to ₹2440-2470 with RSI below 40',
                        horizon: 'MEDIUM_TERM'
                    },
                    phase3_recommendation: {
                        rating: 'BUY',
                        entry_price_range: { min: 2440, max: 2470 },
                        stop_loss: 2380,
                        targets: { t1_1week: 2550, t2_30day: 2650, t3_90day: 2800 },
                        position_size_pct: 3.5,
                        risk_reward_ratio: 3.2
                    },
                    decision: {
                        recommendation: 'BUY',
                        composite_score: 62.5,
                        confidence: 78.2
                    }
                });
                setLoading(false);
            }, 1000);
        } catch (error) {
            console.error('Failed to fetch analysis:', error);
            setLoading(false);
        }
    };

    const getRatingColor = (rating: string) => {
        switch (rating) {
            case 'STRONG_BUY':
            case 'BUY':
                return 'text-emerald-400 bg-emerald-500/20';
            case 'HOLD':
                return 'text-amber-400 bg-amber-500/20';
            case 'SELL':
            case 'STRONG_SELL':
                return 'text-red-400 bg-red-500/20';
            default:
                return 'text-slate-400 bg-slate-500/20';
        }
    };

    if (loading) {
        return (
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700/50 p-12">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400 mb-4"></div>
                    <p className="text-slate-400">Analyzing {stock.symbol}...</p>
                </div>
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700/50 p-12 text-center">
                <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto mb-4" />
                <p className="text-slate-400">No analysis available</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header Card */}
            <div className="bg-gradient-to-r from-slate-800/80 to-purple-900/40 backdrop-blur-lg rounded-xl border border-slate-700/50 p-6">
                <div className="flex items-start justify-between">
                    <div>
                        <h2 className="text-3xl font-bold text-white mb-2">
                            {stock.symbol}
                            <span className="text-lg text-slate-400 ml-3">{stock.exchange}</span>
                        </h2>
                        <div className="text-4xl font-bold text-white mb-2">
                            ₹{analysis.current_price.toLocaleString()}
                        </div>
                    </div>

                    <div className="text-right">
                        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-lg ${getRatingColor(analysis.phase3_recommendation.rating)}`}>
                            {analysis.phase3_recommendation.rating === 'BUY' && <TrendingUp className="w-5 h-5" />}
                            {analysis.phase3_recommendation.rating === 'SELL' && <TrendingDown className="w-5 h-5" />}
                            {analysis.phase3_recommendation.rating}
                        </div>
                        <div className="text-sm text-slate-400 mt-2">
                            Confidence: {analysis.decision.confidence.toFixed(1)}%
                        </div>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-4 gap-4 mt-6">
                    <div className="bg-slate-700/30 rounded-lg p-3">
                        <div className="text-xs text-slate-400 mb-1">Entry Range</div>
                        <div className="text-sm font-semibold text-white">
                            ₹{analysis.phase3_recommendation.entry_price_range.min} - ₹{analysis.phase3_recommendation.entry_price_range.max}
                        </div>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                        <div className="text-xs text-slate-400 mb-1">Stop Loss</div>
                        <div className="text-sm font-semibold text-red-400">
                            ₹{analysis.phase3_recommendation.stop_loss}
                        </div>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                        <div className="text-xs text-slate-400 mb-1">Target (30d)</div>
                        <div className="text-sm font-semibold text-emerald-400">
                            ₹{analysis.phase3_recommendation.targets.t2_30day}
                        </div>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                        <div className="text-xs text-slate-400 mb-1">Risk/Reward</div>
                        <div className="text-sm font-semibold text-white">
                            1:{analysis.phase3_recommendation.risk_reward_ratio}
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-700">
                {[
                    { id: 'overview', label: 'Overview', icon: Info },
                    { id: 'technical', label: 'Technical', icon: BarChart3 },
                    { id: 'llm', label: 'AI Analysis', icon: Brain },
                    { id: 'ml', label: 'ML Predictions', icon: Zap }
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${activeTab === tab.id
                                ? 'text-emerald-400 border-b-2 border-emerald-400'
                                : 'text-slate-400 hover:text-slate-300'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700/50 p-6">
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-3">Investment Thesis</h3>
                            <p className="text-slate-300">{analysis.phase1_what_why.what}</p>
                            <div className="mt-3 flex items-center gap-2">
                                <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm">
                                    {analysis.phase1_what_why.primary_cause}
                                </span>
                                <span className="text-slate-400 text-sm">
                                    {analysis.phase1_what_why.confidence}% confidence
                                </span>
                            </div>
                        </div>

                        <div className="border-t border-slate-700 pt-6">
                            <h3 className="text-lg font-semibold text-white mb-3">Entry Strategy</h3>
                            <div className="space-y-2 text-slate-300">
                                <div><span className="text-slate-400">Window:</span> {analysis.phase2_when_where.entry_window}</div>
                                <div><span className="text-slate-400">Trigger:</span> {analysis.phase2_when_where.entry_trigger}</div>
                                <div><span className="text-slate-400">Horizon:</span> {analysis.phase2_when_where.horizon}</div>
                            </div>
                        </div>

                        <div className="border-t border-slate-700 pt-6">
                            <h3 className="text-lg font-semibold text-white mb-3">Price Targets</h3>
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-slate-700/30 rounded-lg p-4">
                                    <div className="text-xs text-slate-400 mb-1">1 Week</div>
                                    <div className="text-2xl font-bold text-emerald-400">
                                        ₹{analysis.phase3_recommendation.targets.t1_1week}
                                    </div>
                                </div>
                                <div className="bg-slate-700/30 rounded-lg p-4">
                                    <div className="text-xs text-slate-400 mb-1">30 Days</div>
                                    <div className="text-2xl font-bold text-emerald-400">
                                        ₹{analysis.phase3_recommendation.targets.t2_30day}
                                    </div>
                                </div>
                                <div className="bg-slate-700/30 rounded-lg p-4">
                                    <div className="text-xs text-slate-400 mb-1">90 Days</div>
                                    <div className="text-2xl font-bold text-emerald-400">
                                        ₹{analysis.phase3_recommendation.targets.t3_90day}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'technical' && (
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-white mb-4">Technical Indicators</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-700/30 rounded-lg p-4">
                                <div className="text-sm text-slate-400 mb-1">RSI (14)</div>
                                <div className="text-2xl font-bold text-white">{analysis.technical_indicators.rsi_14}</div>
                                <div className="text-xs text-amber-400 mt-1">Oversold</div>
                            </div>
                            <div className="bg-slate-700/30 rounded-lg p-4">
                                <div className="text-sm text-slate-400 mb-1">MACD</div>
                                <div className="text-2xl font-bold text-emerald-400">
                                    {analysis.technical_indicators.macd_bullish ? 'Bullish' : 'Bearish'}
                                </div>
                            </div>
                            <div className="bg-slate-700/30 rounded-lg p-4">
                                <div className="text-sm text-slate-400 mb-1">vs SMA50</div>
                                <div className="text-2xl font-bold text-white">
                                    {analysis.technical_indicators.price_vs_sma50 > 0 ? '+' : ''}{analysis.technical_indicators.price_vs_sma50}%
                                </div>
                            </div>
                            <div className="bg-slate-700/30 rounded-lg p-4">
                                <div className="text-sm text-slate-400 mb-1">ADX (14)</div>
                                <div className="text-2xl font-bold text-white">{analysis.technical_indicators.adx_14}</div>
                                <div className="text-xs text-emerald-400 mt-1">Strong Trend</div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'llm' && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                                <Brain className="w-5 h-5 text-purple-400" />
                                Phase 1: What & Why
                            </h3>
                            <p className="text-slate-300">{analysis.phase1_what_why.what}</p>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                                <Target className="w-5 h-5 text-blue-400" />
                                Phase 2: When & Where
                            </h3>
                            <p className="text-slate-300">{analysis.phase2_when_where.entry_trigger}</p>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-emerald-400" />
                                Phase 3: How to Execute
                            </h3>
                            <div className="text-slate-300">
                                Position Size: <span className="font-semibold text-white">{analysis.phase3_recommendation.position_size_pct}%</span> of portfolio
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'ml' && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4">LSTM Price Forecasts</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-slate-700/30 rounded-lg p-4">
                                    <div className="text-sm text-slate-400 mb-1">30-Day Forecast</div>
                                    <div className="text-2xl font-bold text-emerald-400">
                                        ₹{analysis.ml_predictions.lstm['30d']}
                                    </div>
                                    <div className="text-xs text-slate-400 mt-1">
                                        +{((analysis.ml_predictions.lstm['30d'] - analysis.current_price) / analysis.current_price * 100).toFixed(1)}%
                                    </div>
                                </div>
                                <div className="bg-slate-700/30 rounded-lg p-4">
                                    <div className="text-sm text-slate-400 mb-1">90-Day Forecast</div>
                                    <div className="text-2xl font-bold text-emerald-400">
                                        ₹{analysis.ml_predictions.lstm['90d']}
                                    </div>
                                    <div className="text-xs text-slate-400 mt-1">
                                        +{((analysis.ml_predictions.lstm['90d'] - analysis.current_price) / analysis.current_price * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4">XGBoost Classification</h3>
                            <div className="bg-slate-700/30 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-slate-300">Signal</span>
                                    <span className={`font-bold ${analysis.ml_predictions.xgboost.signal === 'BUY' ? 'text-emerald-400' : 'text-red-400'}`}>
                                        {analysis.ml_predictions.xgboost.signal}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-slate-300">Probability</span>
                                    <span className="font-bold text-white">
                                        {(analysis.ml_predictions.xgboost.probability * 100).toFixed(0)}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
