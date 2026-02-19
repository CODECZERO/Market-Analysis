/**
 * Add Stock Modal Component
 * Modal for adding new stocks to watchlist
 */

import React, { useState } from 'react';
import { X, Search, TrendingUp } from 'lucide-react';

interface AddStockModalProps {
    onClose: () => void;
    onAdd: (symbol: string, exchange: string) => void;
}

export default function AddStockModal({ onClose, onAdd }: AddStockModalProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [exchange, setExchange] = useState('NSE');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [isSearching, setIsSearching] = useState(false);

    const handleSearch = async (query: string) => {
        if (query.length < 2) {
            setSearchResults([]);
            return;
        }

        setIsSearching(true);
        try {
            const response = await fetch(`/api/stocks/search?q=${query}&exchange=${exchange}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const data = await response.json();
            if (data.success) {
                setSearchResults(data.data);
            }
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setIsSearching(false);
        }
    };

    const handleSelectStock = (stock: any) => {
        onAdd(stock.symbol, stock.exchange);
    };

    const handleManualAdd = () => {
        if (searchQuery.trim()) {
            onAdd(searchQuery.toUpperCase().trim(), exchange);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-2xl w-full max-w-md mx-4">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-700">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-emerald-400" />
                        Add Stock
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6 space-y-4">
                    {/* Exchange Selector */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Exchange
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                onClick={() => setExchange('NSE')}
                                className={`py-2 px-4 rounded-lg font-medium transition-all ${exchange === 'NSE'
                                        ? 'bg-emerald-500 text-white'
                                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    }`}
                            >
                                NSE
                            </button>
                            <button
                                onClick={() => setExchange('BSE')}
                                className={`py-2 px-4 rounded-lg font-medium transition-all ${exchange === 'BSE'
                                        ? 'bg-emerald-500 text-white'
                                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    }`}
                            >
                                BSE
                            </button>
                        </div>
                    </div>

                    {/* Search Input */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Search Stock
                        </label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="text"
                                placeholder="Enter symbol or company name..."
                                value={searchQuery}
                                onChange={(e) => {
                                    setSearchQuery(e.target.value);
                                    handleSearch(e.target.value);
                                }}
                                className="w-full pl-10 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                        </div>
                    </div>

                    {/* Search Results */}
                    {searchQuery.length >= 2 && (
                        <div className="max-h-64 overflow-y-auto space-y-2">
                            {isSearching ? (
                                <div className="text-center py-8 text-slate-400">
                                    Searching...
                                </div>
                            ) : searchResults.length === 0 ? (
                                <div className="text-center py-8">
                                    <p className="text-slate-400 mb-3">No stocks found</p>
                                    <button
                                        onClick={handleManualAdd}
                                        className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                                    >
                                        Add "{searchQuery.toUpperCase()}" manually
                                    </button>
                                </div>
                            ) : (
                                searchResults.map((stock) => (
                                    <button
                                        key={stock.symbol}
                                        onClick={() => handleSelectStock(stock)}
                                        className="w-full p-4 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-left transition-colors border border-slate-600 hover:border-emerald-500"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <div className="font-semibold text-white">{stock.symbol}</div>
                                                <div className="text-sm text-slate-400">{stock.name}</div>
                                            </div>
                                            <div className="text-xs text-slate-400">
                                                {stock.sector}
                                            </div>
                                        </div>
                                    </button>
                                ))
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-700">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
}
