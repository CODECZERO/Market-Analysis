import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, BarChart2, Clock, Award } from 'lucide-react';
import { API_CONFIG } from '../config';

interface StockPick {
    symbol: string;
    company_name: string;
    current_price: number;
    total_score: number;
    recent_return: number;
    trend_score: number;
    momentum_score: number;
    value_score: number;
    volatility_score: number;
    sector: string;
    pe_ratio: number;
    timeframe: string;
}

interface RecommendationsData {
    mode: string;
    long_term_picks?: StockPick[];
    short_term_picks?: StockPick[];
    total_screened?: number;
}

const StockRecommendations: React.FC = () => {
    const [recommendations, setRecommendations] = useState<RecommendationsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedTimeframe, setSelectedTimeframe] = useState<'long' | 'short'>('long');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchRecommendations();
    }, []);

    const fetchRecommendations = async (stockName?: string) => {
        setLoading(true);
        setError(null);

        try {
            const url = stockName
                ? `${API_CONFIG.BASE_URL}/api/stocks/recommendations?stock_name=${stockName}`
                : `${API_CONFIG.BASE_URL}/api/stocks/recommendations`;

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                setRecommendations(data.data);
            } else {
                setError(data.error || 'Failed to fetch recommendations');
            }
        } catch (err) {
            setError('Network error. Please try again.');
            console.error('Fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 75) return 'text-green-400';
        if (score >= 60) return 'text-yellow-400';
        return 'text-orange-400';
    };

    const getReturnColor = (returnVal: number) => {
        return returnVal >= 0 ? 'text-green-400' : 'text-red-400';
    };

    const renderStockCard = (stock: StockPick, index: number) => (
        <div
            key={stock.symbol}
            className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10 hover:border-blue-400/50 transition-all hover:shadow-lg hover:shadow-blue-500/20"
        >
            {/* Rank Badge */}
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                        #{index + 1}
                    </div>
                    {stock.total_score >= 75 && (
                        <Award className="w-5 h-5 text-yellow-400" />
                    )}
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(stock.total_score)}`}>
                    {stock.total_score.toFixed(0)}
                </div>
            </div>

            {/* Stock Info */}
            <div className="mb-3">
                <h3 className="text-lg font-bold text-white mb-1">{stock.symbol}</h3>
                <p className="text-sm text-gray-400 truncate">{stock.company_name}</p>
                <p className="text-xs text-gray-500 mt-1">{stock.sector}</p>
            </div>

            {/* Price & Return */}
            <div className="flex justify-between items-center mb-3 pb-3 border-b border-white/10">
                <div>
                    <p className="text-xs text-gray-400">Current Price</p>
                    <p className="text-lg font-semibold text-white">₹{stock.current_price.toFixed(2)}</p>
                </div>
                <div className="text-right">
                    <p className="text-xs text-gray-400">Return</p>
                    <p className={`text-lg font-semibold flex items-center gap-1 ${getReturnColor(stock.recent_return)}`}>
                        {stock.recent_return >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        {stock.recent_return.toFixed(2)}%
                    </p>
                </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                    <p className="text-gray-400">Trend</p>
                    <div className="flex items-center gap-1">
                        <div className="flex-1 bg-gray-700 rounded-full h-2">
                            <div
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${(stock.trend_score / 25) * 100}%` }}
                            />
                        </div>
                        <span className="text-white font-semibold">{stock.trend_score}</span>
                    </div>
                </div>
                <div>
                    <p className="text-gray-400">Momentum</p>
                    <div className="flex items-center gap-1">
                        <div className="flex-1 bg-gray-700 rounded-full h-2">
                            <div
                                className="bg-purple-500 h-2 rounded-full"
                                style={{ width: `${(stock.momentum_score / 25) * 100}%` }}
                            />
                        </div>
                        <span className="text-white font-semibold">{stock.momentum_score}</span>
                    </div>
                </div>
                <div>
                    <p className="text-gray-400">Value</p>
                    <div className="flex items-center gap-1">
                        <div className="flex-1 bg-gray-700 rounded-full h-2">
                            <div
                                className="bg-green-500 h-2 rounded-full"
                                style={{ width: `${(stock.value_score / 25) * 100}%` }}
                            />
                        </div>
                        <span className="text-white font-semibold">{stock.value_score}</span>
                    </div>
                </div>
                <div>
                    <p className="text-gray-400">Volatility</p>
                    <div className="flex items-center gap-1">
                        <div className="flex-1 bg-gray-700 rounded-full h-2">
                            <div
                                className="bg-yellow-500 h-2 rounded-full"
                                style={{ width: `${(stock.volatility_score / 25) * 100}%` }}
                            />
                        </div>
                        <span className="text-white font-semibold">{stock.volatility_score}</span>
                    </div>
                </div>
            </div>

            {/* P/E Ratio */}
            {stock.pe_ratio > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-gray-400">P/E Ratio: <span className="text-white font-semibold">{stock.pe_ratio.toFixed(2)}</span></p>
                </div>
            )}
        </div>
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-400">Analyzing stocks...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-6 text-center">
                <p className="text-red-400">{error}</p>
                <button
                    onClick={() => fetchRecommendations()}
                    className="mt-4 px-6 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition"
                >
                    Retry
                </button>
            </div>
        );
    }

    if (!recommendations) return null;

    const currentPicks = selected Timeframe === 'long'
        ? recommendations.long_term_picks || []
        : recommendations.short_term_picks || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                        🎯 Top Stock Recommendations
                    </h2>
                    {recommendations.total_screened && (
                        <p className="text-gray-400 text-sm">
                            Screened {recommendations.total_screened} stocks from Nifty 50
                        </p>
                    )}
                </div>

                {/* Timeframe Selector */}
                <div className="flex gap-2 bg-white/5 backdrop-blur-lg rounded-lg p-1">
                    <button
                        onClick={() => setSelectedTimeframe('long')}
                        className={`px-4 py-2 rounded-md transition flex items-center gap-2 ${selectedTimeframe === 'long'
                                ? 'bg-blue-500 text-white'
                                : 'text-gray-400 hover:text-white'
                            }`}
                    >
                        <Clock className="w-4 h-4" />
                        Long Term
                    </button>
                    <button
                        onClick={() => setSelectedTimeframe('short')}
                        className={`px-4 py-2 rounded-md transition flex items-center gap-2 ${selectedTimeframe === 'short'
                                ? 'bg-purple-500 text-white'
                                : 'text-gray-400 hover:text-white'
                            }`}
                    >
                        <BarChart2 className="w-4 h-4" />
                        Short Term
                    </button>
                </div>
            </div>

            {/* Stock Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {currentPicks.map((stock, index) => renderStockCard(stock, index))}
            </div>

            {/* Empty State */}
            {currentPicks.length === 0 && (
                <div className="text-center py-12 bg-white/5 backdrop-blur-lg rounded-xl">
                    <p className="text-gray-400">No recommendations available</p>
                </div>
            )}
        </div>
    );
};

export default StockRecommendations;
