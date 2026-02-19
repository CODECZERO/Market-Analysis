"""
Stock Screener & Recommender Service
Automatically finds top profitable stocks for long-term and short-term
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from providers.yfinance_provider import YFinanceProvider
from technical_indicators import calculate_indicators
from quant.momentum import calculate_momentum_scores
from quant.mean_reversion import calculate_zscore


class StockScreener:
    """Screen and rank stocks for investment opportunities"""
    
    # Top Indian stocks to screen
    NIFTY_50 = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "BAJFINANCE.NS", "KOTAKBANK.NS",
        "ITC.NS", "LT.NS", "ASIANPAINT.NS", "AXISBANK.NS", "MARUTI.NS",
        "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "WIPRO.NS",
        "POWERGRID.NS", "NTPC.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
        "HCLTECH.NS", "BAJAJFINSV.NS", "HINDALCO.NS", "ADANIENT.NS", "ONGC.NS"
    ]
    
    def __init__(self):
        self.results = []
    
    def calculate_stock_score(self, symbol: str, timeframe: str = "long") -> Dict[str, Any]:
        """Calculate comprehensive score for a stock"""
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            
            # Different periods for long vs short term
            if timeframe == "long":
                hist = ticker.history(period="1y")
                lookback = 90  # 3 months
            else:  # short term
                hist = ticker.history(period="3mo")
                lookback = 30  # 1 month
            
            if len(hist) < 20:
                return None
            
            # Current price
            current_price = hist['Close'].iloc[-1]
            
            # Calculate technical indicators
            indicators = calculate_indicators(hist)
            
            # Score components
            scores = {
                'symbol': symbol,
                'current_price': current_price,
                'timeframe': timeframe
            }
            
            # 1. Trend Score (0-25 points)
            sma_50 = indicators.get('sma_50')
            sma_200 = indicators.get('sma_200')
            
            # Null safety - use current price as fallback with warning
            if sma_50 is None or sma_200 is None:
                print(f"Warning: Missing SMAs for {symbol}, using conservative estimate")
                sma_50 = sma_50 if sma_50 is not None else current_price
                sma_200 = sma_200 if sma_200 is not None else current_price
            
            trend_score = 0
            if current_price > sma_50:
                trend_score += 10
            if current_price > sma_200:
                trend_score += 10
            if sma_50 > sma_200:  # Golden cross
                trend_score += 5
            
            scores['trend_score'] = trend_score
            
            # 2. Momentum Score (0-25 points)
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            
            momentum_score = 0
            if 40 < rsi < 70:  # Healthy RSI
                momentum_score += 10
            if macd > 0:  # Positive MACD
                momentum_score += 10
            
            # Recent performance (with bounds checking)
            if len(hist) < lookback:
                print(f"Warning: Insufficient data for {symbol}, using available data")
                recent_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
            else:
                recent_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[-lookback] - 1) * 100
            
            if recent_return > 0:
                momentum_score += min(5, recent_return / 2)  # Cap at 5 points
            
            scores['momentum_score'] = momentum_score
            scores['recent_return'] = recent_return
            
            # 3. Value Score (0-25 points)
            info = ticker.info
            pe_ratio = info.get('trailingPE', 0)
            pb_ratio = info.get('priceToBook', 0)
            
            value_score = 0
            if 0 < pe_ratio < 25:  # Reasonable P/E
                value_score += 10
            if 0 < pb_ratio < 5:  # Reasonable P/B
                value_score += 10
            
            # Market cap (prefer large caps for stability)
            market_cap = info.get('marketCap', 0)
            if market_cap > 1e11:  # > 1000 Cr
                value_score += 5
            
            scores['value_score'] = value_score
            scores['pe_ratio'] = pe_ratio
            scores['pb_ratio'] = pb_ratio
            scores['market_cap'] = market_cap
            
            # 4. Volatility Score (0-25 points)
            volatility = hist['Close'].pct_change().std() * 100
            
            volatility_score = 0
            if timeframe == "long":
                # Lower volatility preferred for long-term
                if volatility < 2:
                    volatility_score = 25
                elif volatility < 3:
                    volatility_score = 15
                elif volatility < 5:
                    volatility_score = 10
            else:
                # Moderate volatility ok for short-term
                if 1 < volatility < 4:
                    volatility_score = 20
                elif volatility < 6:
                    volatility_score = 10
            
            scores['volatility_score'] = volatility_score
            scores['volatility'] = volatility
            
            # Total Score (0-100)
            total_score = trend_score + momentum_score + value_score + volatility_score
            scores['total_score'] = total_score
            
            # Add company name
            scores['company_name'] = info.get('longName', symbol)
            scores['sector'] = info.get('sector', 'Unknown')
            
            return scores
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def screen_stocks(self, timeframe: str = "long", limit: int = 10) -> List[Dict[str, Any]]:
        """Screen all stocks and return top recommendations - PARALLEL"""
        print(f"\n🔍 Screening {len(self.NIFTY_50)} stocks for {timeframe}-term opportunities...")
        print(f"⚡ Using parallel processing (5 workers)...")
        
        results = []
        
        # ⚡ PERFORMANCE: Parallel processing with ThreadPoolExecutor
        import concurrent.futures
        from functools import partial
        
        # Create partial function with timeframe
        score_func = partial(self.calculate_stock_score, timeframe=timeframe)
        
        # Process 5 stocks simultaneously
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(score_func, symbol): symbol 
                for symbol in self.NIFTY_50
            }
            
            # Collect results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                print(f"  [{completed}/{len(self.NIFTY_50)}] Analyzing {symbol}...", end='\r')
                
                try:
                    score = future.result(timeout=10)  # 10 second timeout per stock
                    if score:
                        results.append(score)
                except concurrent.futures.TimeoutError:
                    print(f"\n  ⚠️  {symbol} timeout (skipping)")
                except Exception as e:
                    print(f"\n  ⚠️  {symbol} error: {e}")
        
        print(f"\n✅ Screened {len(results)} stocks successfully")
        
        # Sort by score
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Return top N
        return results[:limit]
    
    def get_recommendations(self, stock_name: str = None) -> Dict[str, Any]:
        """Get top recommendations for long and short term"""
        
        if stock_name:
            # Analyze specific stock
            print(f"\n📊 Analyzing {stock_name}...")
            
            # Ensure .NS suffix for NSE stocks
            if not stock_name.endswith('.NS'):
                stock_name = f"{stock_name}.NS"
            
            long_score = self.calculate_stock_score(stock_name, "long")
            short_score = self.calculate_stock_score(stock_name, "short")
            
            return {
                "mode": "specific_stock",
                "stock": stock_name,
                "long_term_analysis": long_score,
                "short_term_analysis": short_score
            }
        else:
            # Screen all stocks
            print("\n🎯 Finding best opportunities...")
            
            long_term_picks = self.screen_stocks("long", limit=10)
            short_term_picks = self.screen_stocks("short", limit=10)
            
            return {
                "mode": "auto_discover",
                "timestamp": datetime.now().isoformat(),
                "long_term_picks": long_term_picks,
                "short_term_picks": short_term_picks,
                "total_screened": len(self.NIFTY_50)
            }


def get_top_stocks(stock_name: str = None, timeframe: str = "both") -> Dict[str, Any]:
    """Main function to get stock recommendations"""
    screener = StockScreener()
    return screener.get_recommendations(stock_name)


if __name__ == "__main__":
    # Test the screener
    print("=" * 60)
    print("  STOCK SCREENER & RECOMMENDER TEST")
    print("=" * 60)
    
    # Test 1: Auto-discover best stocks
    print("\n[TEST 1] Auto-discovering top stocks...")
    recommendations = get_top_stocks()
    
    print("\n✅ Top 5 Long-Term Picks:")
    for i, stock in enumerate(recommendations['long_term_picks'][:5], 1):
        print(f"  {i}. {stock['company_name']} ({stock['symbol']})")
        print(f"     Score: {stock['total_score']:.1f}/100 | Return: {stock['recent_return']:.2f}%")
    
    print("\n✅ Top 5 Short-Term Picks:")
    for i, stock in enumerate(recommendations['short_term_picks'][:5], 1):
        print(f"  {i}. {stock['company_name']} ({stock['symbol']})")
        print(f"     Score: {stock['total_score']:.1f}/100 | Return: {stock['recent_return']:.2f}%")
    
    # Test 2: Specific stock analysis
    print("\n[TEST 2] Analyzing specific stock: RELIANCE...")
    specific = get_top_stocks("RELIANCE")
    
    if specific['long_term_analysis']:
        score = specific['long_term_analysis']['total_score']
        print(f"\n  Long-term Score: {score:.1f}/100")
