"""
Market Analysis API Client
Python client library for easy API interaction
"""

import requests
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketAnalysisClient:
    """
    Python client for Market Analysis System API
    
    Usage:
        client = MarketAnalysisClient(api_url="http://localhost:3000")
        
        # Add stock to watchlist
        client.add_to_watchlist("RELIANCE", "NSE")
        
        # Trigger analysis
        result = client.analyze_stock("RELIANCE", "NSE")
        
        # Get quote
        quote = client.get_quote("RELIANCE", "NSE")
    """
    
    def __init__(
        self,
        api_url: str = "http://localhost:3000",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize API client
        
        Args:
            api_url: Base API URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.api_url}/api/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=kwargs.pop('timeout', self.timeout),
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # Watchlist operations
    
    def get_watchlist(self) -> List[Dict]:
        """Get user's watchlist"""
        result = self._request('GET', '/stocks/watchlist')
        return result.get('data', [])
    
    def add_to_watchlist(self, symbol: str, exchange: str = "NSE") -> Dict:
        """Add stock to watchlist"""
        return self._request(
            'POST',
            '/stocks/watchlist',
            json={'symbol': symbol, 'exchange': exchange}
        )
    
    def remove_from_watchlist(self, symbol: str, exchange: str = "NSE") -> Dict:
        """Remove stock from watchlist"""
        return self._request(
            'DELETE',
            f'/stocks/watchlist/{symbol}',
            params={'exchange': exchange}
        )
    
    # Stock analysis
    
    def analyze_stock(
        self,
        symbol: str,
        exchange: str = "NSE",
        refresh: bool = False,
        wait_for_completion: bool = False,
        poll_interval: int = 5,
        max_wait: int = 300
    ) -> Dict:
        """
        Trigger stock analysis
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE/BSE)
            refresh: Force new analysis
            wait_for_completion: Wait for analysis to complete
            poll_interval: Seconds between status checks
            max_wait: Maximum wait time in seconds
            
        Returns:
            Analysis result or job info
        """
        # Trigger analysis
        result = self._request(
            'POST',
            '/stocks/analyze',
            json={
                'symbol': symbol,
                'exchange': exchange,
                'refresh': refresh
            }
        )
        
        analysis_id = result.get('data', {}).get('analysisId')
        
        if not wait_for_completion:
            return result
        
        # Poll for completion
        import time
        elapsed = 0
        
        while elapsed < max_wait:
            status = self.get_analysis(analysis_id)
            
            if status.get('data', {}).get('status') == 'completed':
                logger.info(f"Analysis complete for {symbol}")
                return status
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Analysis did not complete within {max_wait}s")
    
    def get_analysis(self, analysis_id: str) -> Dict:
        """Get analysis result by ID"""
        return self._request('GET', f'/stocks/analyze/{analysis_id}')
    
    def get_analysis_progress(self, analysis_id: str) -> Dict:
        """Get analysis progress"""
        return self._request('GET', f'/stocks/analyze/{analysis_id}/progress')
    
    # Stock data
    
    def get_quote(self, symbol: str, exchange: str = "NSE") -> Dict:
        """Get current stock quote"""
        return self._request(
            'GET',
            f'/stocks/quotes/{symbol}',
            params={'exchange': exchange}
        )
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for stocks"""
        result = self._request(
            'GET',
            '/stocks/search',
            params={'q': query, 'limit': limit}
        )
        return result.get('data', [])
    
    # Batch operations
    
    def analyze_watchlist(
        self,
        batch_size: int = 2,
        delay: int = 10
    ) -> List[Dict]:
        """
        Analyze all stocks in watchlist
        
        Args:
            batch_size: Number of concurrent analyses
            delay: Delay between batches
            
        Returns:
            List of analysis results
        """
        watchlist = self.get_watchlist()
        results = []
        
        import time
        
        for i, stock in enumerate(watchlist):
            symbol = stock['symbol']
            exchange = stock['exchange']
            
            logger.info(f"Analyzing {symbol} ({i+1}/{len(watchlist)})")
            
            try:
                result = self.analyze_stock(symbol, exchange, refresh=True)
                results.append({
                    'symbol': symbol,
                    'success': True,
                    'data': result
                })
            except Exception as e:
                logger.error(f"Failed to analyze {symbol}: {e}")
                results.append({
                    'symbol': symbol,
                    'success': False,
                    'error': str(e)
                })
            
            # Delay between batches
            if (i + 1) % batch_size == 0 and i + 1 < len(watchlist):
                logger.info(f"Waiting {delay}s before next batch...")
                time.sleep(delay)
        
        return results


# Convenience functions

def quick_analyze(symbol: str, exchange: str = "NSE") -> Dict:
    """Quick analysis of a stock"""
    client = MarketAnalysisClient()
    return client.analyze_stock(
        symbol,
        exchange,
        refresh=True,
        wait_for_completion=True
    )


def bulk_analyze(symbols: List[str], exchange: str = "NSE") -> List[Dict]:
    """Analyze multiple stocks"""
    client = MarketAnalysisClient()
    results = []
    
    for symbol in symbols:
        try:
            result = client.analyze_stock(symbol, exchange, refresh=True)
            results.append({'symbol': symbol, 'success': True, 'data': result})
        except Exception as e:
            results.append({'symbol': symbol, 'success': False, 'error': str(e)})
    
    return results


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize client
    client = MarketAnalysisClient()
    
    # Test watchlist
    print("=== Watchlist ===")
    watchlist = client.get_watchlist()
    print(f"Found {len(watchlist)} stocks")
    
    # Add stock
    print("\n=== Add Stock ===")
    client.add_to_watchlist("RELIANCE", "NSE")
    print("Added RELIANCE to watchlist")
    
    # Get quote
    print("\n=== Stock Quote ===")
    quote = client.get_quote("RELIANCE", "NSE")
    print(f"RELIANCE: ₹{quote.get('data', {}).get('price', 0):,.2f}")
    
    # Search
    print("\n=== Search ===")
    results = client.search_stocks("TCS")
    print(f"Found {len(results)} results for 'TCS'")
    
    print("\n✓ API client working!")
