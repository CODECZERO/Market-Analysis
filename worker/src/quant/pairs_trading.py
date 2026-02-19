"""
Pairs Trading with Kalman Filter
Institutional-grade statistical arbitrage strategy for Indian stock market
Uses cointegration testing and dynamic hedge ratio estimation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from statsmodels.tsa.stattools import coint, adfuller
from scipy.optimize import minimize
import logging

logger = logging.getLogger(__name__)


class KalmanFilter:
    """
    Kalman Filter for dynamic hedge ratio estimation in pairs trading
    Adapts to changing market conditions better than static OLS regression
    """
    
    def __init__(self, delta=1e-4, Ve=1e-3):
        """
        Initialize Kalman Filter
        
        Args:
            delta: Process noise variance (smaller = slower adaptation)
            Ve: Measurement noise variance
        """
        self.delta = delta
        self.Ve = Ve
        self.wt = None  # State estimate (hedge ratio)
        self.Ct = None  # Covariance estimate
        self.R = None   # Prediction covariance
        
    def update(self, x: float, y: float) -> float:
        """
        Update filter with new observation and return current hedge ratio
        
        Args:
            x: Price of stock X
            y: Price of stock Y
            
        Returns:
            Current hedge ratio estimate
        """
        if self.wt is None:
            # Initialize
            self.wt = np.array([0.0])
            self.Ct = np.array([[1.0]])
            
        # Prediction
        self.R = self.Ct + self.delta
        
        # Update
        x_arr = np.array([x])
        y_val = y
        
        # Kalman gain
        K = self.R @ x_arr / (x_arr.T @ self.R @ x_arr + self.Ve)
        K = K.reshape(-1, 1)
        
        # Measurement residual
        e = y_val - x_arr.T @ self.wt
        
        # State update
        self.wt = self.wt + (K @ np.array([e])).flatten()
        
        # Covariance update
        self.Ct = self.R - K @ x_arr.T @ self.R
        
        return float(self.wt[0])


def find_cointegrated_pairs(
    price_matrix: pd.DataFrame,
    p_threshold: float = 0.05,
    min_data_points: int = 60
) -> List[Tuple[str, str, float, float]]:
    """
    Find all cointegrated stock pairs from a price matrix
    
    Args:
        price_matrix: DataFrame where columns are stock symbols, rows are dates with prices
        p_threshold: Max p-value for cointegration (default 0.05 = 95% confidence)
        min_data_points: Minimum number of data points required
        
    Returns:
        List of tuples: (stock1, stock2, p_value, hedge_ratio)
    """
    if len(price_matrix) < min_data_points:
        logger.warning(f"Not enough data points: {len(price_matrix)} < {min_data_points}")
        return []
    
    pairs = []
    symbols = price_matrix.columns.tolist()
    n = len(symbols)
    
    for i in range(n):
        for j in range(i + 1, n):
            stock1 = symbols[i]
            stock2 = symbols[j]
            
            # Drop NaN values
            combined = price_matrix[[stock1, stock2]].dropna()
            if len(combined) < min_data_points:
                continue
            
            s1 = combined[stock1].values
            s2 = combined[stock2].values
            
            try:
                # Cointegration test
                score, pvalue, _ = coint(s1, s2)
                
                if pvalue < p_threshold:
                    # Calculate hedge ratio using OLS
                    hedge_ratio = np.polyfit(s1, s2, 1)[0]
                    pairs.append((stock1, stock2, float(pvalue), float(hedge_ratio)))
                    
            except Exception as e:
                logger.debug(f"Cointegration test failed for {stock1}-{stock2}: {e}")
                continue
    
    # Sort by p-value (best pairs first)
    return sorted(pairs, key=lambda x: x[2])


def calculate_spread(
    prices1: np.ndarray,
    prices2: np.ndarray,
    hedge_ratios: np.ndarray
) -> np.ndarray:
    """
    Calculate spread for pairs trading
    
    Args:
        prices1: Prices of stock 1
        prices2: Prices of stock 2
        hedge_ratios: Dynamic hedge ratios from Kalman Filter
        
    Returns:
        Spread time series
    """
    return prices2 - hedge_ratios * prices1


def calculate_zscore(spread: np.ndarray, lookback: int = 20) -> np.ndarray:
    """
    Calculate rolling z-score of spread
    
    Args:
        spread: Spread time series
        lookback: Rolling window for z-score calculation
        
    Returns:
        Z-score time series
    """
    spread_series = pd.Series(spread)
    rolling_mean = spread_series.rolling(window=lookback).mean()
    rolling_std = spread_series.rolling(window=lookback).std()
    
    zscore = (spread_series - rolling_mean) / rolling_std
    return zscore.values


def generate_pairs_signals(
    stock1_symbol: str,
    stock2_symbol: str,
    prices1: pd.Series,
    prices2: pd.Series,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.5,
    stop_loss_threshold: float = 3.5
) -> Dict[str, any]:
    """
    Generate pairs trading signals using Kalman Filter hedge ratio
    
    Args:
        stock1_symbol: Symbol of stock 1
        stock2_symbol: Symbol of stock 2
        prices1: Price series of stock 1
        prices2: Price series of stock 2
        entry_threshold: Z-score threshold for entry (default 2.0 = 2 std deviations)
        exit_threshold: Z-score threshold for exit (default 0.5)
        stop_loss_threshold: Z-score threshold for stop loss
        
    Returns:
        Dictionary with trading signals and analysis
    """
    # Align series
    combined = pd.DataFrame({
        'stock1': prices1,
        'stock2': prices2
    }).dropna()
    
    if len(combined) < 60:
        return {
            'signal': 'INSUFFICIENT_DATA',
            'reason': f'Need at least 60 data points, only have {len(combined)}',
            'spread_zscore': None,
            'hedge_ratio': None,
        }
    
    stock1_prices = combined['stock1'].values
    stock2_prices = combined['stock2'].values
    
    # Apply Kalman Filter to get dynamic hedge ratios
    kf = KalmanFilter(delta=1e-4, Ve=1e-3)
    hedge_ratios = []
    
    for i in range(len(stock1_prices)):
        hr = kf.update(stock1_prices[i], stock2_prices[i])
        hedge_ratios.append(hr)
    
    hedge_ratios = np.array(hedge_ratios)
    
    # Calculate spread
    spread = calculate_spread(stock1_prices, stock2_prices, hedge_ratios)
    
    # Calculate z-score
    zscore = calculate_zscore(spread, lookback=20)
    
    # Current values
    current_zscore = zscore[-1] if not np.isnan(zscore[-1]) else 0
    current_hedge_ratio = hedge_ratios[-1]
    current_spread = spread[-1]
    
    # Generate signal
    if abs(current_zscore) > stop_loss_threshold:
        signal = 'STOP_LOSS'
        reason = f'Z-score {current_zscore:.2f} exceeded stop loss threshold'
        
    elif current_zscore > entry_threshold:
        signal = 'SHORT_SPREAD'
        reason = f'Spread overextended (Z={current_zscore:.2f}). Short {stock2_symbol}, Long {stock1_symbol}'
        
    elif current_zscore < -entry_threshold:
        signal = 'LONG_SPREAD'
        reason = f'Spread underextended (Z={current_zscore:.2f}). Long {stock2_symbol}, Short {stock1_symbol}'
        
    elif abs(current_zscore) < exit_threshold:
        signal = 'EXIT'
        reason = f'Spread mean-reverting (Z={current_zscore:.2f}). Close positions'
        
    else:
        signal = 'NEUTRAL'
        reason = f'Spread within normal range (Z={current_zscore:.2f}). No action'
    
    # Test for stationarity of spread (ADF test)
    try:
        adf_stat, adf_pvalue, _, _, _, _ = adfuller(spread, autolag='AIC')
        spread_stationary = adf_pvalue < 0.05
    except:
        adf_pvalue = 1.0
        spread_stationary = False
    
    return {
        'signal': signal,
        'reason': reason,
        'spread_zscore': float(current_zscore),
        'hedge_ratio': float(current_hedge_ratio),
        'spread_value': float(current_spread),
        'spread_stationary': spread_stationary,
        'adf_pvalue': float(adf_pvalue),
        'stock1_symbol': stock1_symbol,
        'stock2_symbol': stock2_symbol,
        'stock1_position': 'LONG' if signal == 'SHORT_SPREAD' else 'SHORT' if signal == 'LONG_SPREAD' else 'NONE',
        'stock2_position': 'SHORT' if signal == 'SHORT_SPREAD' else 'LONG' if signal == 'LONG_SPREAD' else 'NONE',
        'entry_threshold': entry_threshold,
        'exit_threshold': exit_threshold,
        'confidence': min(abs(current_zscore) / entry_threshold, 1.0) if signal != 'NEUTRAL' else 0.0,
    }


def scan_pairs_opportunities(
    price_matrix: pd.DataFrame,
    top_n: int = 5
) -> List[Dict[str, any]]:
    """
    Scan all stocks for best pairs trading opportunities
    
    Args:
        price_matrix: DataFrame with stock prices (columns = symbols, index = dates)
        top_n: Number of top pairs to return
        
    Returns:
        List of dictionaries with pairs analysis, sorted by opportunity score
    """
    # Find cointegrated pairs
    pairs = find_cointegrated_pairs(price_matrix, p_threshold=0.05)
    
    if not pairs:
        logger.info("No cointegrated pairs found")
        return []
    
    logger.info(f"Found {len(pairs)} cointegrated pairs")
    
    # Generate signals for each pair
    results = []
    for stock1, stock2, pvalue, static_hedge_ratio in pairs[:top_n * 2]:  # Scan more, keep top_n
        try:
            signals = generate_pairs_signals(
                stock1,
                stock2,
                price_matrix[stock1],
                price_matrix[stock2]
            )
            
            signals['stock1'] = stock1
            signals['stock2'] = stock2
            signals['cointegration_pvalue'] = pvalue
            signals['static_hedge_ratio'] = static_hedge_ratio
            
            # Opportunity score: higher z-score + lower p-value = better
            if signals['spread_zscore'] is not None:
                signals['opportunity_score'] = abs(signals['spread_zscore']) * (1 - pvalue)
            else:
                signals['opportunity_score'] = 0
            
            results.append(signals)
            
        except Exception as e:
            logger.error(f"Error analyzing pair {stock1}-{stock2}: {e}")
            continue
    
    # Sort by opportunity score
    results = sorted(results, key=lambda x: x['opportunity_score'], reverse=True)
    
    return results[:top_n]
