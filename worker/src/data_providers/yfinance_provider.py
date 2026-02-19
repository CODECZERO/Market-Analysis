"""
YFinance Data Provider for Indian Stocks
Fetches OHLCV data for NSE/BSE stocks and Nifty indices
Provides 5 years daily, 1 year hourly data
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class YFinanceProvider:
    """
    Data provider for Indian stocks using yfinance
    Supports NSE and BSE exchanges
    """
    
    def __init__(self):
        self.session = None
    
    def fetch_stock_data(
        self,
        symbol: str,
        exchange: str = 'NSE',
        period: str = '5y'
    ) -> Dict[str, Any]:
        """
        Fetch comprehensive stock data
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            exchange: Exchange ('NSE' or 'BSE')
            period: Period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            
        Returns:
            Dictionary with OHLCV data, fundamentals, and metadata
        """
        # Format symbol for yfinance
        ticker_symbol = self._format_symbol(symbol, exchange)
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch historical data
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.error(f"No data found for {ticker_symbol}")
                return {'error': f'No data found for {ticker_symbol}'}
            
            # Fetch info (fundamentals)
            info = ticker.info
            
            # Fetch recent news
            try:
                news = ticker.news[:5] if hasattr(ticker, 'news') else []
            except:
                news = []
            
            # Process data
            result = {
                'symbol': symbol,
                'exchange': exchange,
                'ticker': ticker_symbol,
                'current_price': float(info.get('currentPrice', hist['Close'].iloc[-1])),
                'currency': 'INR',
                'ohlcv': {
                    'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                    'open': hist['Open'].tolist(),
                    'high': hist['High'].tolist(),
                    'low': hist['Low'].tolist(),
                    'close': hist['Close'].tolist(),
                    'volume': hist['Volume'].tolist(),
                },
                'fundamentals': {
                    'market_cap_cr': info.get('marketCap', 0) / 10000000,  # Convert to Crores
                    'pe_ratio': info.get('trailingPE'),
                    'pb_ratio': info.get('priceToBook'),
                    'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                    'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                    'debt_to_equity': info.get('debtToEquity'),
                    'current_ratio': info.get('currentRatio'),
                    'eps': info.get('trailingEps'),
                    'book_value': info.get('bookValue'),
                    '52_week_high': info.get('fiftyTwoWeekHigh'),
                    '52_week_low': info.get('fiftyTwoWeekLow'),
                    'avg_volume': info.get('averageVolume'),
                    'beta': info.get('beta'),
                },
                'company_info': {
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector'),
                    'industry': info.get('industry'),
                    'website': info.get('website'),
                    'employees': info.get('fullTimeEmployees'),
                    'description': info.get('longBusinessSummary', '')[:500],
                },
                'news': [
                    {
                        'title': n.get('title', ''),
                        'link': n.get('link', ''),
                        'published': datetime.fromtimestamp(n.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if n.get('providerPublishTime') else '',
                        'source': n.get('publisher', '')
                    }
                    for n in news
                ][:5],
                'timestamp': datetime.now().isoformat(),
            }
            
            # Calculate simple metrics
            result['metrics'] = self._calculate_metrics(hist)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker_symbol}: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
                'exchange': exchange
            }
    
    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        exchange: str = 'NSE',
        period: str = '1y'
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange
            period: Period
            
        Returns:
            Dictionary mapping symbol to data
        """
        results = {}
        
        for symbol in symbols:
            logger.info(f"Fetching {symbol}...")
            data = self.fetch_stock_data(symbol, exchange, period)
            results[symbol] = data
        
        return results
    
    def fetch_index_data(
        self,
        index_name: str = 'NIFTY',
        period: str = '5y'
    ) -> Dict[str, Any]:
        """
        Fetch Indian index data
        
        Args:
            index_name: Index name ('NIFTY', 'BANKNIFTY', 'SENSEX')
            period: Period
            
        Returns:
            Index OHLCV data
        """
        index_tickers = {
            'NIFTY': '^NSEI',
            'NIFTY50': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
            'SENSEX': '^BSESN',
            'BSE': '^BSESN'
        }
        
        ticker_symbol = index_tickers.get(index_name.upper(), '^NSEI')
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {'error': f'No data for index {index_name}'}
            
            return {
                'index_name': index_name,
                'ticker': ticker_symbol,
                'current_level': float(hist['Close'].iloc[-1]),
                'ohlcv': {
                    'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                    'open': hist['Open'].tolist(),
                    'high': hist['High'].tolist(),
                    'low': hist['Low'].tolist(),
                    'close': hist['Close'].tolist(),
                    'volume': hist['Volume'].tolist(),
                },
                'metrics': self._calculate_metrics(hist),
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error fetching index {index_name}: {e}")
            return {'error': str(e)}
    
    def _format_symbol(self, symbol: str, exchange: str) -> str:
        """Format symbol for yfinance"""
        # NSE symbols end with .NS
        # BSE symbols end with .BO
        
        if exchange.upper() == 'NSE':
            return f"{symbol}.NS"
        elif exchange.upper() == 'BSE':
            return f"{symbol}.BO"
        else:
            return symbol
    
    def _calculate_metrics(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate simple metrics from historical data"""
        if hist.empty:
            return {}
        
        close = hist['Close']
        
        # Returns
        returns_1d = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
        returns_7d = ((close.iloc[-1] - close.iloc[-7]) / close.iloc[-7]) * 100 if len(close) > 7 else 0
        returns_30d = ((close.iloc[-1] - close.iloc[-30]) / close.iloc[-30]) * 100 if len(close) > 30 else 0
        returns_ytd = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100
        
        # Volatility (annualized)
        daily_returns = close.pct_change().dropna()
        volatility_annual = float(daily_returns.std() * (252 ** 0.5) * 100) if len(daily_returns) > 1 else 0
        
        # 52-week high/low
        high_52w = float(hist['High'].tail(252).max()) if len(hist) >= 252 else float(hist['High'].max())
        low_52w = float(hist['Low'].tail(252).min()) if len(hist) >= 252 else float(hist['Low'].min())
        
        # Distance from 52-week high
        distance_from_high = ((close.iloc[-1] - high_52w) / high_52w) * 100
        
        return {
            'returns_1d_pct': float(returns_1d),
            'returns_7d_pct': float(returns_7d),
            'returns_30d_pct': float(returns_30d),
            'returns_ytd_pct': float(returns_ytd),
            'volatility_annual_pct': volatility_annual,
            '52_week_high': high_52w,
            '52_week_low': low_52w,
            'distance_from_52w_high_pct': float(distance_from_high),
            'average_volume_30d': float(hist['Volume'].tail(30).mean()),
        }


def get_stock_data(symbol: str, exchange: str = 'NSE', period: str = '5y') -> Dict[str, Any]:
    """
    Convenience function to fetch stock data
    
    Args:
        symbol: Stock symbol
        exchange: Exchange (NSE/BSE)
        period: Time period
        
    Returns:
        Stock data dictionary
    """
    provider = YFinanceProvider()
    return provider.fetch_stock_data(symbol, exchange, period)


def get_nifty_data(period: str = '5y') -> Dict[str, Any]:
    """Convenience function to fetch Nifty 50 index data"""
    provider = YFinanceProvider()
    return provider.fetch_index_data('NIFTY', period)
