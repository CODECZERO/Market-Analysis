"""
Technical Indicators Module
Computes 20+ technical indicators for Indian stock market analysis
Uses TA-Lib and pandas-ta for comprehensive technical analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import pandas_ta as ta

try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    print("TA-Lib not available, using pandas-ta fallback")


class TechnicalIndicators:
    """
    Comprehensive technical analysis for stock price data
    Computes all indicators needed for the market analysis system
    """
    
    def __init__(self, df):
        """
        Initialize TechnicalIndicators with stock data.
        
        ⚡ PERFORMANCE: Works with DataFrame views instead of copies
        to reduce memory usage.
        """
        # Store reference, don't copy (saves memory)
        self.df = df
        
        # Ensure we have required columns and convert to lowercase for internal consistency
        # This modifies the original DataFrame's columns, which is intended for memory efficiency.
        # If the original DataFrame should not be modified, a copy should be made before passing.
        self.df.columns = [c.lower() for c in self.df.columns]

        # Direct access to numpy arrays for performance in TA-Lib/pandas-ta calls
        self.close = self.df['close'].values if 'close' in self.df.columns else None
        self.high = self.df['high'].values if 'high' in self.df.columns else None
        self.low = self.df['low'].values if 'low' in self.df.columns else None
        self.volume = self.df['volume'].values if 'volume' in self.df.columns else None
        
        required = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def compute_all(self) -> Dict[str, Any]:
        """
        Compute all technical indicators and return as dictionary
        
        Returns:
            Dictionary with all indicator values (latest values + full series where useful)
        """
        indicators = {}
        
        # Trend Indicators
        indicators.update(self._compute_moving_averages())
        indicators.update(self._compute_macd())
        indicators.update(self._compute_adx())
        
        # Momentum Indicators
        indicators.update(self._compute_rsi())
        indicators.update(self._compute_stochastic())
        indicators.update(self._compute_cci())
        
        # Volatility Indicators
        indicators.update(self._compute_bollinger_bands())
        indicators.update(self._compute_atr())
        indicators.update(self._compute_keltner_channels())
        
        # Volume Indicators
        indicators.update(self._compute_obv())
        indicators.update(self._compute_vwap())
        indicators.update(self._compute_mfi())
        
        # Support/Resistance
        indicators.update(self._compute_pivot_points())
        indicators.update(self._compute_fibonacci_levels())
        
        return indicators
    
    def _compute_moving_averages(self) -> Dict[str, Any]:
        """SMA and EMA for trend analysis"""
        close = self.df['close']
        
        sma_50 = close.rolling(window=50).mean()
        sma_200 = close.rolling(window=200).mean()
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        ema_50 = close.ewm(span=50, adjust=False).mean()
        
        current_price = close.iloc[-1]
        
        return {
            'sma_50': float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None,
            'sma_200': float(sma_200.iloc[-1]) if not pd.isna(sma_200.iloc[-1]) else None,
            'ema_12': float(ema_12.iloc[-1]),
            'ema_26': float(ema_26.iloc[-1]),
            'ema_50': float(ema_50.iloc[-1]),
            'price_vs_sma50': float((current_price / sma_50.iloc[-1] - 1) * 100) if not pd.isna(sma_50.iloc[-1]) else None,
            'price_vs_sma200': float((current_price / sma_200.iloc[-1] - 1) * 100) if not pd.isna(sma_200.iloc[-1]) else None,
            'golden_cross': sma_50.iloc[-1] > sma_200.iloc[-1] if not pd.isna(sma_50.iloc[-1]) and not pd.isna(sma_200.iloc[-1]) else None,
        }
    
    def _compute_macd(self) -> Dict[str, Any]:
        """MACD for trend and momentum"""
        if HAS_TALIB:
            macd, signal, histogram = talib.MACD(
                self.df['close'].values,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
        else:
            macd_result = ta.macd(self.df['close'], fast=12, slow=26, signal=9)
            macd = macd_result['MACD_12_26_9'].values
            signal = macd_result['MACDs_12_26_9'].values
            histogram = macd_result['MACDh_12_26_9'].values
        
        return {
            'macd': float(macd[-1]) if not pd.isna(macd[-1]) else 0.0,
            'macd_signal': float(signal[-1]) if not pd.isna(signal[-1]) else 0.0,
            'macd_histogram': float(histogram[-1]) if not pd.isna(histogram[-1]) else 0.0,
            'macd_bullish': histogram[-1] > 0 if not pd.isna(histogram[-1]) else False,
        }
    
    def _compute_rsi(self) -> Dict[str, Any]:
        """RSI for overbought/oversold conditions"""
        if HAS_TALIB:
            rsi_14 = talib.RSI(self.df['close'].values, timeperiod=14)
        else:
            rsi_14 = ta.rsi(self.df['close'], length=14).values
        
        current_rsi = float(rsi_14[-1]) if not pd.isna(rsi_14[-1]) else 50.0
        
        return {
            'rsi_14': current_rsi,
            'rsi_overbought': current_rsi > 70,
            'rsi_oversold': current_rsi < 30,
            'rsi_signal': 'overbought' if current_rsi > 70 else 'oversold' if current_rsi < 30 else 'neutral',
        }
    
    def _compute_bollinger_bands(self) -> Dict[str, Any]:
        """Bollinger Bands for volatility and price extremes"""
        if HAS_TALIB:
            upper, middle, lower = talib.BBANDS(
                self.df['close'].values,
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
        else:
            bb = ta.bbands(self.df['close'], length=20, std=2)
            # Dynamic column finding to handle pandas-ta version differences
            cols = bb.columns.tolist()
            upper_col = next((c for c in cols if c.startswith('BBU')), cols[2] if len(cols) > 2 else None)
            middle_col = next((c for c in cols if c.startswith('BBM')), cols[1] if len(cols) > 1 else None)
            lower_col = next((c for c in cols if c.startswith('BBL')), cols[0] if len(cols) > 0 else None)
            
            upper = bb[upper_col].values if upper_col else np.zeros(len(self.df))
            middle = bb[middle_col].values if middle_col else np.zeros(len(self.df))
            lower = bb[lower_col].values if lower_col else np.zeros(len(self.df))
        
        current_price = self.df['close'].iloc[-1]
        bb_width = ((upper[-1] - lower[-1]) / middle[-1]) * 100 if not pd.isna(middle[-1]) else 0
        
        return {
            'bb_upper': float(upper[-1]) if not pd.isna(upper[-1]) else 0.0,
            'bb_middle': float(middle[-1]) if not pd.isna(middle[-1]) else 0.0,
            'bb_lower': float(lower[-1]) if not pd.isna(lower[-1]) else 0.0,
            'bb_width_pct': float(bb_width),
            'price_position_in_bb': float((current_price - lower[-1]) / (upper[-1] - lower[-1])) if not pd.isna(upper[-1]) and not pd.isna(lower[-1]) else 0.5,
        }
    
    def _compute_adx(self) -> Dict[str, Any]:
        """ADX for trend strength"""
        if HAS_TALIB:
            adx = talib.ADX(
                self.df['high'].values,
                self.df['low'].values,
                self.df['close'].values,
                timeperiod=14
            )
        else:
            adx_result = ta.adx(self.df['high'], self.df['low'], self.df['close'], length=14)
            adx = adx_result['ADX_14'].values
        
        current_adx = float(adx[-1]) if not pd.isna(adx[-1]) else 0.0
        
        return {
            'adx_14': current_adx,
            'trend_strength': 'strong' if current_adx > 25 else 'weak' if current_adx < 20 else 'moderate',
        }
    
    def _compute_obv(self) -> Dict[str, Any]:
        """On-Balance Volume for volume trend"""
        if HAS_TALIB:
            obv = talib.OBV(self.df['close'].values, self.df['volume'].values)
        else:
            obv = ta.obv(self.df['close'], self.df['volume']).values
        
        # Compute OBV trend (last 20 days)
        obv_trend = 'increasing' if obv[-1] > obv[-20] else 'decreasing'
        
        return {
            'obv': float(obv[-1]),
            'obv_trend': obv_trend,
            'obv_change_20d': float((obv[-1] - obv[-20]) / abs(obv[-20]) * 100) if obv[-20] != 0 else 0.0,
        }
    
    def _compute_stochastic(self) -> Dict[str, Any]:
        """Stochastic Oscillator"""
        if HAS_TALIB:
            slowk, slowd = talib.STOCH(
                self.df['high'].values,
                self.df['low'].values,
                self.df['close'].values,
                fastk_period=14,
                slowk_period=3,
                slowd_period=3
            )
        else:
            stoch = ta.stoch(self.df['high'], self.df['low'], self.df['close'], k=14, d=3)
            slowk = stoch['STOCHk_14_3_3'].values
            slowd = stoch['STOCHd_14_3_3'].values
        
        return {
            'stoch_k': float(slowk[-1]) if not pd.isna(slowk[-1]) else 50.0,
            'stoch_d': float(slowd[-1]) if not pd.isna(slowd[-1]) else 50.0,
            'stoch_overbought': slowk[-1] > 80 if not pd.isna(slowk[-1]) else False,
            'stoch_oversold': slowk[-1] < 20 if not pd.isna(slowk[-1]) else False,
        }
    
    def _compute_atr(self) -> Dict[str, Any]:
        """Average True Range for volatility"""
        if HAS_TALIB:
            atr = talib.ATR(
                self.df['high'].values,
                self.df['low'].values,
                self.df['close'].values,
                timeperiod=14
            )
        else:
            atr = ta.atr(self.df['high'], self.df['low'], self.df['close'], length=14).values
        
        current_price = self.df['close'].iloc[-1]
        atr_pct = (atr[-1] / current_price) * 100 if current_price > 0 else 0
        
        return {
            'atr_14': float(atr[-1]) if not pd.isna(atr[-1]) else 0.0,
            'atr_pct': float(atr_pct),
        }
    
    def _compute_pivot_points(self) -> Dict[str, Any]:
        """Pivot points for support/resistance"""
        high = self.df['high'].iloc[-1]
        low = self.df['low'].iloc[-1]
        close = self.df['close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': float(pivot),
            'resistance_1': float(r1),
            'resistance_2': float(r2),
            'resistance_3': float(r3),
            'support_1': float(s1),
            'support_2': float(s2),
            'support_3': float(s3),
        }
    
    def _compute_vwap(self) -> Dict[str, Any]:
        """Volume Weighted Average Price"""
        typical_price = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        vwap = (typical_price * self.df['volume']).cumsum() / self.df['volume'].cumsum()
        
        current_price = self.df['close'].iloc[-1]
        current_vwap = vwap.iloc[-1]
        
        return {
            'vwap': float(current_vwap),
            'price_vs_vwap': float((current_price / current_vwap - 1) * 100) if current_vwap > 0 else 0.0,
        }
    
    def _compute_mfi(self) -> Dict[str, Any]:
        """Money Flow Index"""
        if HAS_TALIB:
            mfi = talib.MFI(
                self.df['high'].values,
                self.df['low'].values,
                self.df['close'].values,
                self.df['volume'].values,
                timeperiod=14
            )
        else:
            mfi = ta.mfi(self.df['high'], self.df['low'], self.df['close'], self.df['volume'], length=14).values
        
        current_mfi = float(mfi[-1]) if not pd.isna(mfi[-1]) else 50.0
        
        return {
            'mfi_14': current_mfi,
            'mfi_overbought': current_mfi > 80,
            'mfi_oversold': current_mfi < 20,
        }
    
    def _compute_cci(self) -> Dict[str, Any]:
        """Commodity Channel Index"""
        if HAS_TALIB:
            cci = talib.CCI(
                self.df['high'].values,
                self.df['low'].values,
                self.df['close'].values,
                timeperiod=20
            )
        else:
            cci = ta.cci(self.df['high'], self.df['low'], self.df['close'], length=20).values
        
        return {
            'cci_20': float(cci[-1]) if not pd.isna(cci[-1]) else 0.0,
        }
    
    def _compute_keltner_channels(self) -> Dict[str, Any]:
        """Keltner Channels for trend and volatility"""
        ema = self.df['close'].ewm(span=20, adjust=False).mean()
        if HAS_TALIB:
            atr = talib.ATR(self.df['high'].values, self.df['low'].values, self.df['close'].values, timeperiod=20)
        else:
            atr = ta.atr(self.df['high'], self.df['low'], self.df['close'], length=20).values
        
        upper = ema + (2 * atr)
        lower = ema - (2 * atr)
        
        return {
            'keltner_upper': float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else 0.0,
            'keltner_middle': float(ema.iloc[-1]),
            'keltner_lower': float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else 0.0,
        }
    
    def _compute_fibonacci_levels(self) -> Dict[str, Any]:
        """Fibonacci retracement levels from recent high/low"""
        # Use last 90 days for swing high/low
        recent_df = self.df.tail(90)
        swing_high = recent_df['high'].max()
        swing_low = recent_df['low'].min()
        diff = swing_high - swing_low
        
        return {
            'fib_0': float(swing_high),
            'fib_236': float(swing_high - 0.236 * diff),
            'fib_382': float(swing_high - 0.382 * diff),
            'fib_500': float(swing_high - 0.500 * diff),
            'fib_618': float(swing_high - 0.618 * diff),
            'fib_786': float(swing_high - 0.786 * diff),
            'fib_100': float(swing_low),
        }


def calculate_indicators(ohlcv_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to calculate all indicators
    
    Args:
        ohlcv_data: DataFrame with OHLCV columns
        
    Returns:
        Dictionary of all technical indicators
    """
    ti = TechnicalIndicators(ohlcv_data)
    return ti.compute_all()
