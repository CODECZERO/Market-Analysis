"""
Enhanced OHLCV Data Fetcher
Multiple timeframes: 5 years daily, 1 year weekly, 1 month hourly
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta

class EnhancedOHLCVFetcher:
    """Fetch OHLCV data across multiple timeframes"""
    
    def __init__(self):
        pass
    
    def fetch_all_timeframes(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for all timeframes
        
        Returns dict with keys: '5y_daily', '1y_weekly', '1m_hourly', '1d_1min'
        """
        ticker = yf.Ticker(symbol)
        
        data = {}
        
        # 5 years daily
        print(f"Fetching 5 years daily data for {symbol}...")
        try:
            data['5y_daily'] = ticker.history(period='5y', interval='1d')
            print(f"  ✅ Got {len(data['5y_daily'])} daily candles")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            data['5y_daily'] = pd.DataFrame()
        
        # 1 year weekly
        print(f"Fetching 1 year weekly data...")
        try:
            data['1y_weekly'] = ticker.history(period='1y', interval='1wk')
            print(f"  ✅ Got {len(data['1y_weekly'])} weekly candles")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            data['1y_weekly'] = pd.DataFrame()
        
        # 1 month hourly
        print(f"Fetching 1 month hourly data...")
        try:
            data['1m_hourly'] = ticker.history(period='1mo', interval='1h')
            print(f"  ✅ Got {len(data['1m_hourly'])} hourly candles")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            data['1m_hourly'] = pd.DataFrame()
        
        # 1 day 1-minute (for intraday)
        print(f"Fetching 1 day 1-minute data...")
        try:
            data['1d_1min'] = ticker.history(period='1d', interval='1m')
            print(f"  ✅ Got {len(data['1d_1min'])} 1-minute candles")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            data['1d_1min'] = pd.DataFrame()
        
        return data
    
    def fetch_custom_timeframe(self, symbol: str, start_date: str, 
                               end_date: str, interval: str = '1d') -> pd.DataFrame:
        """
        Fetch custom timeframe
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        ticker = yf.Ticker(symbol)
        
        try:
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            return data
        except Exception as e:
            print(f"Error fetching custom timeframe: {e}")
            return pd.DataFrame()
    
    def get_52_week_high_low(self, symbol: str) -> Dict:
        """Get 52-week high and low prices"""
        ticker = yf.Ticker(symbol)
        
        try:
            # Fetch 1 year data
            data = ticker.history(period='1y')
            
            if len(data) > 0:
                high_52w = float(data['High'].max())
                low_52w = float(data['Low'].min())
                current_price = float(data['Close'].iloc[-1])
                
                # Calculate distance from 52w high/low
                distance_from_high = ((current_price - high_52w) / high_52w) * 100
                distance_from_low = ((current_price - low_52w) / low_52w) * 100
                
                # Find dates
                high_date = data['High'].idxmax().strftime('%Y-%m-%d')
                low_date = data['Low'].idxmin().strftime('%Y-%m-%d')
                
                return {
                    'symbol': symbol,
                    'high_52w': high_52w,
                    'low_52w': low_52w,
                    'current_price': current_price,
                    'distance_from_high_percent': distance_from_high,
                    'distance_from_low_percent': distance_from_low,
                    'high_date': high_date,
                    'low_date': low_date,
                    'range_52w': high_52w - low_52w
                }
        
        except Exception as e:
            print(f"Error getting 52w high/low: {e}")
        
        return {}
    
    def calculate_multi_timeframe_trend(self, symbol: str) -> Dict:
        """
        Calculate trend across multiple timeframes
        Useful for determining overall market direction
        """
        data_all = self.fetch_all_timeframes(symbol)
        
        trends = {}
        
        for timeframe, df in data_all.items():
            if len(df) >= 2:
                # Simple trend: compare first and last close
                start_price = df['Close'].iloc[0]
                end_price = df['Close'].iloc[-1]
                change_percent = ((end_price - start_price) / start_price) * 100
                
                if change_percent > 2:
                    trend = 'UPTREND'
                elif change_percent < -2:
                    trend = 'DOWNTREND'
                else:
                    trend = 'SIDEWAYS'
                
                trends[timeframe] = {
                    'trend': trend,
                    'change_percent': float(change_percent),
                    'start_price': float(start_price),
                    'end_price': float(end_price),
                    'candles': len(df)
                }
        
        return trends
    
    def get_volume_profile(self, symbol: str, period: str = '3mo') -> Dict:
        """Calculate volume profile"""
        ticker = yf.Ticker(symbol)
        
        try:
            data = ticker.history(period=period)
            
            if len(data) > 0:
                avg_volume = float(data['Volume'].mean())
                max_volume = float(data['Volume'].max())
                min_volume = float(data['Volume'].min())
                
                # Recent vs average
                recent_volume = float(data['Volume'].iloc[-1])
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
                
                return {
                    'symbol': symbol,
                    'avg_volume': avg_volume,
                    'max_volume': max_volume,
                    'min_volume': min_volume,
                    'recent_volume': recent_volume,
                    'volume_ratio': volume_ratio,
                    'volume_spike': volume_ratio > 2.0  # 2x average = spike
                }
        
        except Exception as e:
            print(f"Error calculating volume profile: {e}")
        
        return {}

def demo():
    """Demo enhanced OHLCV fetcher"""
    fetcher = EnhancedOHLCVFetcher()
    
    print("Enhanced OHLCV Fetcher Demo")
    print("="*70)
    
    symbol = "RELIANCE.NS"
    
    # Fetch all timeframes
    print(f"\nFetching all timeframes for {symbol}:")
    print("="*70)
    data = fetcher.fetch_all_timeframes(symbol)
    
    print(f"\n✅ Successfully fetched {len(data)} timeframes")
    
    # 52-week high/low
    print(f"\n52-Week Analysis:")
    print("="*70)
    week_52 = fetcher.get_52_week_high_low(symbol)
    
    if week_52:
        print(f"Current Price: ₹{week_52['current_price']:,.2f}")
        print(f"52W High: ₹{week_52['high_52w']:,.2f} (on {week_52['high_date']})")
        print(f"52W Low: ₹{week_52['low_52w']:,.2f} (on {week_52['low_date']})")
        print(f"Distance from High: {week_52['distance_from_high_percent']:+.2f}%")
        print(f"Distance from Low: {week_52['distance_from_low_percent']:+.2f}%")
    
    # Multi-timeframe trend
    print(f"\nMulti-Timeframe Trend Analysis:")
    print("="*70)
    trends = fetcher.calculate_multi_timeframe_trend(symbol)
    
    for timeframe, trend_data in trends.items():
        print(f"\n{timeframe}:")
        print(f"  Trend: {trend_data['trend']}")
        print(f"  Change: {trend_data['change_percent']:+.2f}%")
        print(f"  Candles: {trend_data['candles']}")
    
    # Volume profile
    print(f"\nVolume Profile:")
    print("="*70)
    volume = fetcher.get_volume_profile(symbol)
    
    if volume:
        print(f"Average Volume: {volume['avg_volume']:,.0f}")
        print(f"Recent Volume: {volume['recent_volume']:,.0f}")
        print(f"Volume Ratio: {volume['volume_ratio']:.2f}x")
        print(f"Spike Detected: {'YES' if volume['volume_spike'] else 'NO'}")

if __name__ == "__main__":
    demo()
