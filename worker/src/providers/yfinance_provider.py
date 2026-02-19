"""
YFinance Provider - Fetch stock data from Yahoo Finance
Supports NSE and BSE stocks
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta


class YFinanceProvider:
    """Provider for Yahoo Finance stock data (NSE/BSE)"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch stock price data from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., "TCS.NS", "RELIANCE.NS")
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if len(data) > 0:
                return data
            else:
                print(f"No data found for {symbol}")
                return None
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current/latest price for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if len(data) > 0:
                return float(data['Close'].iloc[-1])
            return None
        except:
            return None
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get stock information and fundamentals"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return {}

    def get_intraday_data(self, symbol: str, interval: str = "5m", period: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch granular intraday data safely
        
        Args:
            symbol: Stock symbol
            interval: 1m, 2m, 5m, 15m, 30m, 60m
            period: 1d, 5d (max 7d for 1m data)
            
        Returns:
            DataFrame with datetime index
        """
        try:
            # Add .NS suffix if missing for Indian context check
            if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
                # Try simple append, though Orchestrator usually handles this
                pass 
                
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if len(data) == 0:
                print(f"⚠️ No intraday data for {symbol} ({interval})")
                return None
            
            # Ensure columns are lower case
            data.columns = [c.lower() for c in data.columns]
            return data
            
        except Exception as e:
            print(f"❌ Error fetching intraday {interval} for {symbol}: {e}")
            return None
