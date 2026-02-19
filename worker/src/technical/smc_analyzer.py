"""
Smart Money Concepts (SMC) & ICT Analyzer
Detects institutional footprints: BOS, CHoCH, Order Blocks, and FVGs
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any

class SMCAnalyzer:
    """
    Analyzes price action using Smart Money Concepts (SMC)
    Used to provide professional 'Why Buy/Sell' reasoning
    """
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Master method to run all SMC checks
        """
        if len(df) < 50:
            return {"error": "Insufficient data"}
            
        # Ensure column names are lowercase
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        
        results = {
            "market_structure": self._analyze_market_structure(df),
            "order_blocks": self._find_order_blocks(df),
            "fvg": self._find_fvgs(df),
            "liquidity": self._detect_liquidity_pools(df),
            "fib_confluence": self._calculate_fib_confluence(df)
        }
        
        # Synthesize final SMC signal
        results["signal"] = self._synthesize_smc_signal(results)
        return results
        
    def _analyze_market_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect BOS (Break of Structure) and CHoCH (Change of Character)"""
        # Logic: Detect swing highs/lows and see if price closed above/below them
        window = 5
        df['swing_high'] = df['high'].rolling(window=window*2+1, center=True).max() == df['high']
        df['swing_low'] = df['low'].rolling(window=window*2+1, center=True).min() == df['low']
        
        last_high = df[df['swing_high']]['high'].iloc[-2] if len(df[df['swing_high']]) > 1 else None
        last_low = df[df['swing_low']]['low'].iloc[-2] if len(df[df['swing_low']]) > 1 else None
        
        current_close = df['close'].iloc[-1]
        
        bos = False
        choch = False
        trend = "Neutral"
        
        if last_high and current_close > last_high:
            bos = True
            trend = "Bullish"
        elif last_low and current_close < last_low:
            bos = True
            trend = "Bearish"
            
        # CHoCH is typically the first BOS in a new direction
        # Simplified here as whether the most recent break aligns with overall trend
        return {
            "trend": trend,
            "bos": bos,
            "last_swing_high": float(last_high) if last_high else None,
            "last_swing_low": float(last_low) if last_low else None
        }
        
    def _find_order_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find recent Bullish/Bearish Order Blocks (OB)"""
        obs = []
        # Bullish OB: Last down candle before a strong move up (impulse)
        # Bearish OB: Last up candle before a strong move down (impulse)
        
        for i in range(len(df) - 5, len(df) - 1):
            # Check for impulse (e.g., price move > 1.5 ATR or similar)
            move = df['close'].iloc[i+1] - df['open'].iloc[i+1]
            prev_move = df['close'].iloc[i] - df['open'].iloc[i]
            
            # Simplified OB detection: 
            # Bullish: Previous was RED, current is GREEN and very large
            if prev_move < 0 and move > abs(prev_move) * 2:
                obs.append({
                    "type": "Bullish OB",
                    "price": float(df['low'].iloc[i]),
                    "high": float(df['high'].iloc[i]),
                    "status": "Valid" if df['low'].iloc[-1] > df['low'].iloc[i] else "Mitigated"
                })
            # Bearish: Previous was GREEN, current is RED and very large
            elif prev_move > 0 and move < -prev_move * 2:
                obs.append({
                    "type": "Bearish OB",
                    "price": float(df['high'].iloc[i]),
                    "low": float(df['low'].iloc[i]),
                    "status": "Valid" if df['high'].iloc[-1] < df['high'].iloc[i] else "Mitigated"
                })
        
        return obs[-2:] # Return last 2 OBs
        
    def _find_fvgs(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Fair Value Gaps (FVG) / Imbalace"""
        fvgs = []
        # FVG is gap between High of candle 1 and Low of candle 3 in an up move
        # or Low of candle 1 and High of candle 3 in a down move
        for i in range(len(df) - 4, len(df) - 1):
            # Bullish FVG
            if df['low'].iloc[i+1] > df['high'].iloc[i-1]:
                fvgs.append({
                    "type": "Bullish FVG",
                    "top": float(df['low'].iloc[i+1]),
                    "bottom": float(df['high'].iloc[i-1]),
                    "status": "Open"
                })
            # Bearish FVG
            elif df['high'].iloc[i+1] < df['low'].iloc[i-1]:
                fvgs.append({
                    "type": "Bearish FVG",
                    "top": float(df['low'].iloc[i-1]),
                    "bottom": float(df['high'].iloc[i+1]),
                    "status": "Open"
                })
        return fvgs
        
    def _detect_liquidity_pools(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Detect areas of Buy-Side and Sell-Side Liquidity"""
        # Liquidity sits at equal highs (BSL) or equal lows (SSL)
        bsl = [float(h) for h in df['high'].tail(20).nlargest(3)]
        ssl = [float(l) for l in df['low'].tail(20).nsmallest(3)]
        return {"buy_side": bsl, "sell_side": ssl}

    def _calculate_fib_confluence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for Fibonacci Confluence (Golden Pocket)"""
        try:
            # Find significant swing high/low in last 50 candles
            high_idx = df['high'].tail(50).idxmax()
            low_idx = df['low'].tail(50).idxmin()
            
            high_price = df['high'].loc[high_idx]
            low_price = df['low'].loc[low_idx]
            current = df['close'].iloc[-1]
            
            trend = "Bullish" if low_idx < high_idx else "Bearish" # Retracing from High down or Low up?
            
            # Calculate Retracements
            diff = high_price - low_price
            fib_levels = {}
            if trend == "Bullish": # Retracing DOWN from High
                # 0 is High, 1 is Low
                fib_levels['0.382'] = high_price - (diff * 0.382)
                fib_levels['0.5'] = high_price - (diff * 0.5)
                fib_levels['0.618'] = high_price - (diff * 0.618) # Golden Pocket Top
                fib_levels['0.786'] = high_price - (diff * 0.786)
            else: # Retracing UP from Low
                # 0 is Low, 1 is High
                fib_levels['0.382'] = low_price + (diff * 0.382)
                fib_levels['0.5'] = low_price + (diff * 0.5)
                fib_levels['0.618'] = low_price + (diff * 0.618)
                fib_levels['0.786'] = low_price + (diff * 0.786)
                
            # Check Confluence (Is price near a level?)
            confluence_level = None
            for level, price in fib_levels.items():
                if abs(current - price) / price < 0.005: # Within 0.5%
                    confluence_level = level
                    break
                    
            return {
                "trend_context": trend,
                "golden_pocket": fib_levels.get('0.618'),
                "current_confluence": confluence_level
            }
        except:
            return {}

    def _synthesize_smc_signal(self, results: Dict) -> str:
        """Combine all to produce a single Signal string"""
        structure = results['market_structure']['trend']
        fvgs = results['fvg']
        obs = results['order_blocks']
        
        if structure == "Bullish" and any(f['type'] == "Bullish FVG" for f in fvgs):
            base_sig = "Institutional Support Detected (ICT Bullish)"
        elif structure == "Bearish" and any(f['type'] == "Bearish FVG" for f in fvgs):
            base_sig = "Institutional Selling Detected (ICT Bearish)"
        else:
            base_sig = "Consolidation / Liquidity Seek"
            
        # Add Confluence details
        fib = results.get('fib_confluence', {})
        if fib.get('current_confluence') == '0.618':
            return f"{base_sig} + Golden Pocket (0.618) Rejection"
            
        return base_sig
