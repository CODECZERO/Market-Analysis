/**
 * Modern Stock Dashboard - Premium Design
 * Features: Glassmorphism, Smooth Animations, Interactive Charts
 */

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, BarChart3, Plus, RefreshCw, Search, Sparkles, Zap } from 'lucide-react';
import { API_CONFIG } from '../config';

interface Stock {
    symbol: string;
    name?: string;
    price?: number;
    change?: number;
    changePercent?: number;
    sentiment?: 'bullish' | 'bearish' | 'neutral';
    analysisStatus?: 'idle' | 'analyzing' | 'complete';
}

export default function ModernStockDashboard() {
    const [stocks, setStocks] = useState<Stock[]>([
        { symbol: 'RELIANCE.NS', name: 'Reliance Industries', price: 2456.80, change: 45.20, changePercent: 1.87, sentiment: 'bullish', analysisStatus: 'idle' },
        { symbol: 'TCS.NS', name: 'Tata Consultancy', price: 3678.50, change: -23.40, changePercent: -0.63, sentiment: 'neutral', analysisStatus: 'idle' },
        { symbol: 'INFY.NS', name: 'Infosys', price: 1542.30, change: 12.80, changePercent: 0.84, sentiment: 'bullish', analysisStatus: 'idle' }
    ]);
    const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
    const [searchQuery, setSearchQuery] = useState('');

    const getSentimentColor = (sentiment?: string) => {
        switch (sentiment) {
            case 'bullish': return 'from-emerald-500 to-teal-500';
            case 'bearish': return 'from-rose-500 to-pink-500';
            default: return 'from-slate-500 to-gray-500';
        }
    };

    const getSentimentBg = (sentiment?: string) => {
        switch (sentiment) {
            case 'bullish': return 'bg-emerald-500/10 border-emerald-500/30';
            case 'bearish': return 'bg-rose-500/10 border-rose-500/30';
            default: return 'bg-slate-500/10 border-slate-500/30';
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
            {/* Animated Background Grid */}
            <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center opacity-10" />

            {/* Floating Orbs */}
            <div className="fixed top-20 left-20 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" />
            <div className="fixed bottom-20 right-20 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse delay-1000" />

            {/* Header */}
            <div className="relative z-10">
                <div className="bg-slate-900/40 backdrop-blur-xl border-b border-white/10">
                    <div className="max-w-7xl mx-auto px-6 py-6">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl blur-lg opacity-50" />
                                    <div className="relative w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center">
                                        <BarChart3 className="w-8 h-8 text-white" />
                                    </div>
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                                        Market Intelligence
                                        <Sparkles className="w-5 h-5 text-yellow-400" />
                                    </h1>
                                    <p className="text-sm text-slate-400">AI-Powered Stock Analysis Platform</p>
                                </div>
                            </div>

                            <button className="group relative px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl font-semibold text-white overflow-hidden transition-all hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/50">
                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform" />
                                <span className="relative flex items-center gap-2">
                                    <Plus className="w-5 h-5" />
                                    Add Stock
                                </span>
                            </button>
                        </div>

                        {/* Stats Cards */}
                        <div className="grid grid-cols-4 gap-4 mt-6">
                            {[
                                { label: 'Portfolio Value', value: '₹12.4L', change: '+2.4%', icon: TrendingUp, color: 'emerald' },
                                { label: 'Total Stocks', value: '12', change: '+3', icon: Activity, color: 'blue' },
                                { label: 'AI Signals', value: '8', change: 'Active', icon: Zap, color: 'yellow' },
                                { label: 'Accuracy', value: '87%', change: '+5%', icon: Sparkles, color: 'purple' }
                            ].map((stat, i) => (
                                <div key={i} className="group relative bg-white/5 backdrop-blur-xl rounded-2xl p-4 border border-white/10 hover:border-white/20 transition-all hover:scale-105">
                                    <div className={`absolute top-2 right-2 w-10 h-10 bg-${stat.color}-500/10 rounded-lg flex items-center justify-center`}>
                                        <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                                    </div>
                                    <div className="text-sm text-slate-400">{stat.label}</div>
                                    <div className="text-2xl font-bold text-white mt-1">{stat.value}</div>
                                    <div className={`text-xs mt-1 text-${stat.color}-400`}>{stat.change}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-12 gap-6">
                    {/* Stocks List */}
                    <div className="col-span-5">
                        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-emerald-400" />
                                    Watchlist
                                </h2>
                                <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                                    <RefreshCw className="w-4 h-4 text-slate-400" />
                                </button>
                            </div>

                            {/* Search */}
                            <div className="relative mb-4">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="Search stocks..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all"
                                />
                            </div>

                            {/* Stock Cards */}
                            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                                {stocks.map((stock, idx) => (
                                    <div
                                        key={idx}
                                        onClick={() => setSelectedStock(stock)}
                                        className={`group relative bg-white/5 backdrop-blur-lg rounded-xl p-4 border cursor-pointer transition-all hover:scale-[1.02] ${selectedStock?.symbol === stock.symbol
                                                ? 'border-emerald-500/50 bg-emerald-500/10'
                                                : 'border-white/10 hover:border-white/20'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-semibold text-white">{stock.symbol}</h3>
                                                    <span className={`px-2 py-0.5 text-xs rounded-full border ${getSentimentBg(stock.sentiment)}`}>
                                                        {stock.sentiment?.toUpperCase()}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-slate-400 mt-1">{stock.name}</p>
                                            </div>

                                            <div className="text-right">
                                                <div className="font-semibold text-white">₹{stock.price?.toLocaleString()}</div>
                                                <div className={`text-sm flex items-center gap-1 justify-end ${stock.change! >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    {stock.change! >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                                    {stock.changePercent?.toFixed(2)}%
                                                </div>
                                            </div>
                                        </div>

                                        {/* Analyze Button on Hover */}
                                        <div className="mt-3 pt-3 border-t border-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button className={`w-full py-2 rounded-lg font-medium text-sm bg-gradient-to-r ${getSentimentColor(stock.sentiment)} text-white hover:shadow-lg transition-all`}>
                                                {stock.analysisStatus === 'analyzing' ? '⏳ Analyzing...' : '🔍 Analyze Now'}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Analysis Panel */}
                    <div className="col-span-7">
                        {selectedStock ? (
                            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">{selected Stock.symbol}</h2>
                                        <p className="text-slate-400">{selectedStock.name}</p>
                                    </div>
                                    <div className={`px-4 py-2 rounded-xl bg-gradient-to-r ${getSentimentColor(selectedStock.sentiment)} text-white font-semibold`}>
                                        STRONG BUY
                                    </div>
                                </div>

                                {/* Price Card */}
                                <div className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 rounded-xl p-6 border border-emerald-500/20 mb-6">
                                    <div className="flex items-end justify-between">
                                        <div>
                                            <div className="text-sm text-slate-400">Current Price</div>
                                            <div className="text-4xl font-bold text-white mt-1">₹{selectedStock.price?.toLocaleString()}</div>
                                            <div className="flex items-center gap-2 mt-2">
                                                <TrendingUp className="w-4 h-4 text-emerald-400" />
                                                <span className="text-emerald-400 font-medium">+₹{selectedStock.change} ({selectedStock.changePercent}%)</span>
                                                <span className="text-xs text-slate-500">Today</span>
                                            </div>
                                        </div>

                                        {/* Mini Chart Placeholder */}
                                        <div className="w-32 h-16 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-lg" />
                                    </div>
                                </div>

                                {/* AI Insights */}
                                <div className="grid grid-cols-3 gap-4">
                                    {[
                                        { label: 'Entry Price', value: '₹2,420', color: 'blue' },
                                        { label: 'Target', value: '₹2,850', color: 'emerald' },
                                        { label: 'Stop Loss', value: '₹2,310', color: 'rose' }
                                    ].map((insight, i) => (
                                        <div key={i} className="bg-white/5 rounded-xl p-4 border border-white/10">
                                            <div className="text-xs text-slate-400">{insight.label}</div>
                                            <div className={`text-xl font-bold text-${insight.color}-400 mt-1`}>{insight.value}</div>
                                        </div>
                                    ))}
                                </div>

                                {/* Technical Indicators */}
                                <div className="mt-6 space-y-3">
                                    <h3 className="font-semibold text-white flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 text-yellow-400" />
                                        AI Analysis
                                    </h3>
                                    {[
                                        { name: 'Technical Score', value: 78, color: 'emerald' },
                                        { name: 'Sentiment Score', value: 85, color: 'blue' },
                                        { name: 'Momentum', value: 92, color: 'purple' }
                                    ].map((indicator, i) => (
                                        <div key={i} className="bg-white/5 rounded-lg p-3">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-slate-400">{indicator.name}</span>
                                                <span className={`text-sm font-semibold text-${indicator.color}-400`}>{indicator.value}/100</span>
                                            </div>
                                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full bg-gradient-to-r from-${indicator.color}-500 to-${indicator.color}-400 rounded-full transition-all`}
                                                    style={{ width: `${indicator.value}%` }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-12 text-center h-full flex flex-col items-center justify-center">
                                <div className="w-20 h-20 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-2xl flex items-center justify-center mb-4">
                                    <BarChart3 className="w-10 h-10 text-emerald-400" />
                                </div>
                                <h3 className="text-xl font-semibold text-white mb-2">Select a Stock</h3>
                                <p className="text-slate-400">Choose a stock from your watchlist to view AI-powered analysis</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
