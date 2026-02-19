/**
 * Stock Card Component
 * Individual stock item in watchlist
 */

import React from 'react';
import { TrendingUp, TrendingDown, Play, Trash2, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface Stock {
    id: string;
    symbol: string;
    exchange: string;
    addedAt: string;
    lastAnalyzedAt: string | null;
    analysisStatus: 'pending' | 'processing' | 'completed' | 'error';
}

interface StockCardProps {
    stock: Stock;
    selected: boolean;
    onSelect: () => void;
    onAnalyze: () => void;
    onRemove: () => void;
}

export default function StockCard({ stock, selected, onSelect, onAnalyze, onRemove }: StockCardProps) {
    const getStatusIcon = () => {
        switch (stock.analysisStatus) {
            case 'completed':
                return <CheckCircle className="w-4 h-4 text-emerald-400" />;
            case 'processing':
                return <Clock className="w-4 h-4 text-amber-400 animate-spin" />;
            case 'error':
                return <AlertCircle className="w-4 h-4 text-red-400" />;
            default:
                return <Clock className="w-4 h-4 text-slate-400" />;
        }
    };

    const getStatusText = () => {
        switch (stock.analysisStatus) {
            case 'completed':
                return 'Analyzed';
            case 'processing':
                return 'Analyzing...';
            case 'error':
                return 'Error';
            default:
                return 'Pending';
        }
    };

    return (
        <div
            onClick={onSelect}
            className={`p-4 rounded-lg cursor-pointer transition-all ${selected
                    ? 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border-2 border-emerald-500'
                    : 'bg-slate-700/30 border border-slate-600/50 hover:bg-slate-700/50 hover:border-slate-500'
                }`}
        >
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-bold text-white">{stock.symbol}</h3>
                        <span className="px-2 py-0.5 text-xs font-medium bg-slate-600 text-slate-300 rounded">
                            {stock.exchange}
                        </span>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-slate-400">
                        {getStatusIcon()}
                        <span>{getStatusText()}</span>
                    </div>

                    {stock.lastAnalyzedAt && (
                        <div className="text-xs text-slate-500 mt-1">
                            Last: {new Date(stock.lastAnalyzedAt).toLocaleDateString()}
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onAnalyze();
                        }}
                        className="p-2 hover:bg-emerald-500/20 rounded-lg transition-colors group"
                        title="Analyze"
                    >
                        <Play className="w-4 h-4 text-emerald-400 group-hover:text-emerald-300" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onRemove();
                        }}
                        className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                        title="Remove"
                    >
                        <Trash2 className="w-4 h-4 text-red-400 group-hover:text-red-300" />
                    </button>
                </div>
            </div>
        </div>
    );
}
