/**
 * Add Stock Modal - Modern Design
 * Search and add stocks to watchlist
 */

import React, { useState } from 'react';
import { Search, X, TrendingUp, Plus } from 'lucide-react';

interface Props {
    onClose: () => void;
    onAdd: (symbol: string, exchange: string) => void;
}

const popularStocks = [
    { symbol: 'RELIANCE.NS', name: 'Reliance Industries', exchange: 'NSE' },
    { symbol: 'TCS.NS', name: 'Tata Consultancy Services', exchange: 'NSE' },
    { symbol: 'INFY.NS', name: 'Infosys', exchange: 'NSE' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank', exchange: 'NSE' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank', exchange: 'NSE' },
    { symbol: 'SBIN.NS', name: 'State Bank of India', exchange: 'NSE' },
    { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel', exchange: 'NSE' },
    { symbol: 'ITC.NS', name: 'ITC Limited', exchange: 'NSE' }
];

export default function ModernAddStockModal({ onClose, onAdd }: Props) {
    const [search, setSearch] = useState('');
    const [selectedExchange, setSelectedExchange] = useState('NSE');

    const filteredStocks = popularStocks.filter(stock =>
        stock.symbol.toLowerCase().includes(search.toLowerCase()) ||
        stock.name.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-900 rounded-2xl border border-white/10 max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
                {/* Header */}
                <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border-b border-white/10 p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                                <Plus className="w-6 h-6 text-emerald-400" />
                                Add Stock
                            </h2>
                            <p className="text-sm text-slate-400 mt-1">Search and add stocks to your watchlist</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <X className="w-5 h-5 text-slate-400" />
                        </button>
                    </div>
                </div>

                {/* Search */}
                <div className="p-6 border-b border-white/10">
                    <div className="relative">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search stocks (e.g., RELIANCE, TCS)..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all"
                            autoFocus
                        />
                    </div>

                    {/* Exchange Filter */}
                    <div className="flex gap-2 mt-4">
                        {['NSE', 'BSE'].map(exchange => (
                            <button
                                key={exchange}
                                onClick={() => setSelectedExchange(exchange)}
                                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${selectedExchange === exchange
                                        ? 'bg-emerald-500 text-white'
                                        : 'bg-white/5 text-slate-400 hover:bg-white/10'
                                    }`}
                            >
                                {exchange}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Stock List */}
                <div className="p-6 max-h-96 overflow-y-auto">
                    {filteredStocks.length === 0 ? (
                        <div className="text-center py-12">
                            <Search className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                            <p className="text-slate-400">No stocks found</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {filteredStocks.map((stock) => (
                                <button
                                    key={stock.symbol}
                                    onClick={() => {
                                        onAdd(stock.symbol, stock.exchange);
                                        onClose();
                                    }}
                                    className="w-full bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-500/50 rounded-xl p-4 transition-all text-left group"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-semibold text-white">{stock.symbol}</h3>
                                                <span className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded">
                                                    {stock.exchange}
                                                </span>
                                            </div>
                                            <p className="text-sm text-slate-400 mt-1">{stock.name}</p>
                                        </div>
                                        <Plus className="w-5 h-5 text-slate-400 group-hover:text-emerald-400 transition-colors" />
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="bg-white/5 border-t border-white/10 p-4">
                    <p className="text-xs text-slate-500 text-center">
                        Can't find a stock? Enter the symbol directly in the format: SYMBOL.{selectedExchange}
                    </p>
                </div>
            </div>
        </div>
    );
}
