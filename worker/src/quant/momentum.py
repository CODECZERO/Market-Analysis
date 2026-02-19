"""
Cross-Sectional Momentum Strategy
Ranks stocks by momentum and generates long/short signals
Based on Jegadeesh and Titman (1993)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def calculate_momentum_scores(
    returns_matrix: pd.DataFrame,
    lookback_periods: List[int] = [21, 63, 126]
) -> pd.DataFrame:
    """
    Calculate cross-sectional momentum scores
    
    Args:
        returns_matrix: DataFrame with daily returns (columns = stocks, index = dates)
        lookback_periods: List of lookback periods in days (default: 1m, 3m, 6m)
        
    Returns:
        DataFrame with percentile-ranked momentum scores
    """
    scores = pd.DataFrame(index=returns_matrix.index, columns=returns_matrix.columns)
    
    for period in lookback_periods:
        # Cumulative returns over lookback period
        cumulative_returns = returns_matrix.rolling(window=period).sum()
        
        # Percentile rank across stocks (0 to 1)
        percentile_ranks = cumulative_returns.rank(axis=1, pct=True)
        
        # Average across all lookback periods
        if scores.isna().all().all():
            scores = percentile_ranks
        else:
            scores = scores + percentile_ranks
    
    # Average the scores
    scores = scores / len(lookback_periods)
    
    return scores


def generate_momentum_signals(
    returns_matrix: pd.DataFrame,
    long_threshold: float = 0.9,
    short_threshold: float = 0.1,
    lookback_periods: List[int] = [21, 63, 126]
) -> Dict[str, List[str]]:
    """
    Generate long/short momentum signals
    
    Args:
        returns_matrix: DataFrame with daily returns
        long_threshold: Percentile for long positions (default 0.9 = top 10%)
        short_threshold: Percentile for short positions (default 0.1 = bottom 10%)
        lookback_periods: Momentum calculation periods
        
    Returns:
        Dictionary with 'long', 'short', and 'neutral' stock lists
    """
    # Calculate momentum scores
    scores = calculate_momentum_scores(returns_matrix, lookback_periods)
    
    # Get most recent scores
    latest_scores = scores.iloc[-1]
    
    # Filter out NaN values
    latest_scores = latest_scores.dropna()
    
    # Generate signals
    long_stocks = latest_scores[latest_scores >= long_threshold].index.tolist()
    short_stocks = latest_scores[latest_scores <= short_threshold].index.tolist()
    neutral_stocks = latest_scores[
        (latest_scores > short_threshold) & (latest_scores < long_threshold)
    ].index.tolist()
    
    return {
        'long': long_stocks,
        'short': short_stocks,
        'neutral': neutral_stocks,
        'scores': latest_scores.to_dict()
    }


def momentum_rank_for_stock(
    stock_symbol: str,
    returns_matrix: pd.DataFrame,
    lookback_periods: List[int] = [21, 63, 126]
) -> Dict[str, any]:
    """
    Get momentum analysis for a specific stock
    
    Args:
        stock_symbol: Stock symbol to analyze
        returns_matrix: DataFrame with daily returns
        lookback_periods: Momentum calculation periods
        
    Returns:
        Dictionary with momentum rank and signal
    """
    if stock_symbol not in returns_matrix.columns:
        return {
            'symbol': stock_symbol,
            'error': 'Stock not found in returns matrix',
            'momentum_rank': None,
            'signal': 'UNKNOWN'
        }
    
    # Calculate scores
    scores = calculate_momentum_scores(returns_matrix, lookback_periods)
    latest_scores = scores.iloc[-1].dropna()
    
    stock_score = latest_scores.get(stock_symbol)
    if stock_score is None or pd.isna(stock_score):
        return {
            'symbol': stock_symbol,
            'error': 'Insufficient data',
            'momentum_rank': None,
            'signal': 'UNKNOWN'
        }
    
    # Determine signal
    if stock_score >= 0.9:
        signal = 'STRONG_LONG'
        description = 'Top 10% momentum (strong buy)'
    elif stock_score >= 0.7:
        signal = 'LONG'
        description = 'Top 30% momentum (buy)'
    elif stock_score <= 0.1:
        signal = 'STRONG_SHORT'
        description = 'Bottom 10% momentum (strong sell)'
    elif stock_score <= 0.3:
        signal = 'SHORT'
        description = 'Bottom 30% momentum (sell)'
    else:
        signal = 'NEUTRAL'
        description = 'Middle quintile momentum (hold)'
    
    # Calculate percentile rank in words
    rank_pct = stock_score * 100
    
    return {
        'symbol': stock_symbol,
        'momentum_score': float(stock_score),
        'percentile_rank': float(rank_pct),
        'signal': signal,
        'description': description,
        'rank_category': 'top_decile' if stock_score >= 0.9 else 
                        'top_quintile' if stock_score >= 0.8 else
                        'top_third' if stock_score >= 0.66 else
                        'middle' if stock_score >= 0.33 else
                        'bottom_third' if stock_score >= 0.2 else
                        'bottom_quintile' if stock_score >= 0.1 else
                        'bottom_decile'
    }
