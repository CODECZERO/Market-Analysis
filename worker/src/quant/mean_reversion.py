"""
Mean Reversion Strategy
Z-score based mean reversion signals for short-term trading
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_zscore(
    prices: pd.Series,
    window: int = 20
) -> pd.Series:
    """
    Calculate rolling z-score
    
    Args:
        prices: Price series
        window: Rolling window for mean/std calculation
        
    Returns:
        Z-score series
    """
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    zscore = (prices - rolling_mean) / rolling_std
    return zscore


def generate_mean_reversion_signals(
    prices: pd.Series,
    window: int = 20,
    entry_threshold: float = 1.5,
    exit_threshold: float = 0.3
) -> Dict[str, any]:
    """
    Generate mean reversion signals based on z-score
    
    Args:
        prices: Price series
        window: Rolling window for z-score
        entry_threshold: Z-score threshold for entry (default 1.5 std dev)
        exit_threshold: Z-score threshold for exit
        
    Returns:
        Dictionary with signals and analysis
    """
    if len(prices) < window:
        return {
            'signal': 'INSUFFICIENT_DATA',
            'zscore': None,
            'reason': f'Need at least {window} data points'
        }
    
    # Calculate z-score
    zscore_series = calculate_zscore(prices, window)
    current_zscore = zscore_series.iloc[-1]
    current_price = prices.iloc[-1]
    rolling_mean = prices.rolling(window=window).mean().iloc[-1]
    
    if pd.isna(current_zscore):
        return {
            'signal': 'INSUFFICIENT_DATA',
            'zscore': None,
            'reason': 'Not enough data for z-score calculation'
        }
    
    # Generate signal
    if current_zscore > entry_threshold:
        signal = 'SELL'
        reason = f'Price {current_zscore:.2f} std devs above mean (overbought). Expect reversion down.'
        expected_direction = 'DOWN'
        
    elif current_zscore < -entry_threshold:
        signal = 'BUY'
        reason = f'Price {abs(current_zscore):.2f} std devs below mean (oversold). Expect reversion up.'
        expected_direction = 'UP'
        
    elif abs(current_zscore) < exit_threshold:
        signal = 'EXIT'
        reason = f'Price near mean (Z={current_zscore:.2f}). Mean reversion complete.'
        expected_direction = 'NEUTRAL'
        
    else:
        signal = 'HOLD'
        reason = f'Price moderately away from mean (Z={current_zscore:.2f}). Wait for extreme.'
        expected_direction = 'REVERTING' if current_zscore > 0 else 'REVERTING'
    
    # Calculate mean reversion target
    target_price = rolling_mean
    
    # Estimate confidence based on how extreme the z-score is
    confidence = min(abs(current_zscore) / 3.0, 1.0)  # Max confidence at 3 std devs
    
    return {
        'signal': signal,
        'reason': reason,
        'zscore': float(current_zscore),
        'current_price': float(current_price),
        'mean_price': float(rolling_mean),
        'target_price': float(target_price),
        'expected_direction': expected_direction,
        'confidence': float(confidence),
        'window': window,
        'entry_threshold': entry_threshold,
        'deviation_pct': float((current_price / rolling_mean - 1) * 100),
        'oversold': current_zscore < -entry_threshold,
        'overbought': current_zscore > entry_threshold,
    }


def backtest_mean_reversion(
    prices: pd.Series,
    window: int = 20,
    entry_threshold: float = 1.5,
    holding_period: int = 5
) -> Dict[str, any]:
    """
    Simple backtest of mean reversion strategy
    
    Args:
        prices: Price series
        window: Rolling window
        entry_threshold: Entry threshold for z-score
        holding_period: Days to hold position
        
    Returns:
        Backtest statistics
    """
    zscore_series = calculate_zscore(prices, window)
    
    # Identify entry points
    buy_signals = zscore_series < -entry_threshold
    sell_signals = zscore_series > entry_threshold
    
    trades = []
    i = window
    while i < len(prices) - holding_period:
        if buy_signals.iloc[i]:
            entry_price = prices.iloc[i]
            exit_price = prices.iloc[i + holding_period]
            pnl = (exit_price - entry_price) / entry_price
            trades.append({'type': 'BUY', 'pnl': pnl})
            i += holding_period
            
        elif sell_signals.iloc[i]:
            entry_price = prices.iloc[i]
            exit_price = prices.iloc[i + holding_period]
            pnl = (entry_price - exit_price) / entry_price  # Short position
            trades.append({'type': 'SELL', 'pnl': pnl})
            i += holding_period
        else:
            i += 1
    
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0,
            'avg_pnl': 0,
            'message': 'No trading signals generated'
        }
    
    pnls = [t['pnl'] for t in trades]
    wins = sum(1 for p in pnls if p > 0)
    
    return {
        'total_trades': len(trades),
        'win_rate': float(wins / len(trades)),
        'avg_pnl_pct': float(np.mean(pnls) * 100),
        'total_pnl_pct': float(np.sum(pnls) * 100),
        'best_trade_pct': float(max(pnls) * 100),
        'worst_trade_pct': float(min(pnls) * 100),
    }
