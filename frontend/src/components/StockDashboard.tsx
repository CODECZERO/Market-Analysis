/**
 * Stock Dashboard Component
 * Main dashboard for viewing stock watchlist and analysis
 */

import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, TrendingDown, Search, RefreshCw } from 'lucide-react';
import StockCard from './StockCard';
import AddStockModal from './AddStockModal';
import AnalysisPanel from './AnalysisPanel';

interface Stock {
    id: string;
    symbol: string;
    exchange: string;
    addedAt: string;
    lastAnalyzedAt: string | null;
    analysisStatus: 'pending' | 'processing' | 'completed' | 'error';
}

export default function StockDashboard() {
    const [watchlist, setWatchlist] = useState<Stock[]>([]);
    const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchWatchlist();
    }, []);

    const fetchWatchlist = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/stocks/watchlist', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            if (data.success) {
                setWatchlist(data.data);
            }
        } catch (error) {
            console.error('Failed to fetch watchlist:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddStock = async (symbol: string, exchange: string) => {
        try {
            const response = await fetch('/api/stocks/watchlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ symbol, exchange })
            });
            const data = await response.json();
            if (data.success) {
                setWatchlist([...watchlist, data.data]);
                setShowAddModal(false);
            }
        } catch (error) {
            console.error('Failed to add stock:', error);
        }
    };

    const handleRemoveStock = async (stock: Stock) => {
        try {
            const response = await fetch(`/api/stocks/watchlist/${stock.symbol}?exchange=${stock.exchange}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            if (data.success) {
                setWatchlist(watchlist.filter(s => s.id !== stock.id));
                if (selectedStock?.id === stock.id) {
                    setSelectedStock(null);
                }
            }
        } catch (error) {
            console.error('Failed to remove stock:', error);
        }
    };

    const handleAnalyzeStock = async (stock: Stock) => {
        try {
            const response = await fetch('/api/stocks/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    symbol: stock.symbol,
                    exchange: stock.exchange,
                    refresh: true
                })
            });
            const data = await response.json();
            if (data.success) {
                // Update stock status
                setWatchlist(watchlist.map(s =>
                    s.id === stock.id
                        ? { ...s, analysisStatus: 'processing' }
                        : s
                ));
                setSelectedStock(stock);
            }
        } catch (error) {
            console.error('Failed to analyze stock:', error);
        }
    };

    const filteredWatchlist = watchlist.filter(stock =>
        stock.symbol.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {/* Header */}
            <div className="bg-slate-800/50 backdrop-blur-lg border-b border-slate-700/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                                <TrendingUp className="w-8 h-8 text-emerald-400" />
                                Stock Analysis Dashboard
                            </h1>
                            <p className="text-slate-400 mt-1">
                                Institutional-grade Indian market analysis powered by AI
                            </p>
                        </div>
                        <button
                            onClick={() => setShowAddModal(true)}
                            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg hover:shadow-emerald-500/50"
                        >
                            <Plus className="w-5 h-5" />
                            Add Stock
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Watchlist Panel */}
                    <div className="lg:col-span-1">
                        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700/50 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-bold text-white">Watchlist</h2>
                                <button
                                    onClick={fetchWatchlist}
                                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                                >
                                    <RefreshCw className="w-4 h-4 text-slate-400" />
                                </button>
                            </div>

                            {/* Search */}
                            <div className="relative mb-4">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="Search stocks..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                                />
                            </div>

                            {/* Stock List */}
                            <div className="space-y-2 max-h-[600px] overflow-y-auto">
                                {loading ? (
                                    <div className="text-center py-8 text-slate-400">Loading...</div>
                                ) : filteredWatchlist.length === 0 ? (
                                    <div className="text-center py-8 text-slate-400">
                                        No stocks in watchlist
                                    </div>
                                ) : (
                                    filteredWatchlist.map(stock => (
                                        <StockCard
                                            key={stock.id}
                                            stock={stock}
                                            selected={selectedStock?.id === stock.id}
                                            onSelect={() => setSelectedStock(stock)}
                                            onAnalyze={() => handleAnalyzeStock(stock)}
                                            onRemove={() => handleRemoveStock(stock)}
                                        />
                                    ))
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Analysis Panel */}
                    <div className="lg:col-span-2">
                        {selectedStock ? (
                            <AnalysisPanel stock={selectedStock} />
                        ) : (
                            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700/50 p-12 text-center">
                                <TrendingUp className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-slate-400 mb-2">
                                    Select a stock to analyze
                                </h3>
                                <p className="text-slate-500">
                                    Choose a stock from your watchlist to view detailed analysis
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Add Stock Modal */}
            {showAddModal && (
                <AddStockModal
                    onClose={() => setShowAddModal(false)}
                    onAdd={handleAddStock}
                />
            )}
        </div>
    );
}
