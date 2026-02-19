"""
StockTwits Scraper - Social sentiment from StockTwits
Alternative to Twitter for stock discussions
"""

import requests
from datetime import datetime
from typing import List, Dict
import time

class StockTwitsScraper:
    """Scrape StockTwits for stock sentiment"""
    
    BASE_URL = "https://api.stocktwits.com/api/2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_discussions(self, symbol: str, limit: int = 30) -> List[Dict]:
        """
        Scrape StockTwits discussions for a symbol
        Uses public API (no authentication needed)
        """
        messages = []
        
        # Clean symbol (remove exchange suffix .NS, .BO etc)
        clean_symbol = symbol.split('.')[0]
        
        try:
            print(f"Fetching StockTwits data for ${clean_symbol}...")
            
            # StockTwits streams API (public)
            url = f"{self.BASE_URL}/streams/symbol/{clean_symbol}.json"
            
            params = {
                'limit': min(limit, 30)  # API max is 30
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'messages' in data:
                    for msg in data['messages']:
                        # Extract sentiment
                        sentiment = msg.get('entities', {}).get('sentiment', {})
                        sentiment_label = sentiment.get('basic') if sentiment else 'neutral'
                        
                        # Map to our sentiment format
                        if sentiment_label == 'Bullish':
                            score = 0.7
                            label = 'POSITIVE'
                        elif sentiment_label == 'Bearish':
                            score = -0.7
                            label = 'NEGATIVE'
                        else:
                            score = 0.0
                            label = 'NEUTRAL'
                        
                        messages.append({
                            'text': msg.get('body', ''),
                            'author': msg.get('user', {}).get('username', 'unknown'),
                            'timestamp': msg.get('created_at', ''),
                            'url': f"https://stocktwits.com/{msg.get('user', {}).get('username', '')}/message/{msg.get('id', '')}",
                            'likes': msg.get('likes', {}).get('total', 0),
                            'source': 'StockTwits',
                            'sentiment': {
                                'score': score,
                                'label': label,
                                'raw': sentiment_label
                            },
                            'platform': 'stocktwits'
                        })
                
                print(f"✅ Found {len(messages)} messages from StockTwits")
            
            elif response.status_code == 404:
                print(f"⚠️  Symbol ${clean_symbol} not found on StockTwits")
                # Return mock data for demo
                return self._mock_data(clean_symbol)
            
            else:
                print(f"⚠️  StockTwits API error: {response.status_code}")
                return self._mock_data(clean_symbol)
        
        except Exception as e:
            print(f"Error scraping StockTwits: {e}")
            return self._mock_data(clean_symbol)
        
        return messages
    
    def _mock_data(self, symbol: str) -> List[Dict]:
        """Generate mock StockTwits data"""
        return [
            {
                'text': f'${symbol} looking strong! Breaking resistance 📈',
                'author': 'trader_pro',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://stocktwits.com',
                'likes': 45,
                'source': 'StockTwits (Mock)',
                'sentiment': {'score': 0.8, 'label': 'POSITIVE', 'raw': 'Bullish'},
                'platform': 'stocktwits'
            },
            {
                'text': f'Taking profits on ${symbol}, might consolidate here',
                'author': 'market_watcher',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://stocktwits.com',
                'likes': 23,
                'source': 'StockTwits (Mock)',
                'sentiment': {'score': -0.3, 'label': 'NEGATIVE', 'raw': 'Bearish'},
                'platform': 'stocktwits'
            },
            {
                'text': f'Watching ${symbol} for entry point',
                'author': 'swing_trader',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://stocktwits.com',
                'likes': 12,
                'source': 'StockTwits (Mock)',
                'sentiment': {'score': 0.0, 'label': 'NEUTRAL', 'raw': 'neutral'},
                'platform': 'stocktwits'
            }
        ]
    
    def get_trending_symbols(self) -> List[Dict]:
        """Get trending symbols from StockTwits"""
        try:
            url = f"{self.BASE_URL}/trending/symbols.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                symbols = []
                
                for item in data.get('symbols', [])[:10]:  # Top 10
                    symbols.append({
                        'symbol': item.get('symbol', ''),
                        'title': item.get('title', ''),
                        'watchlist_count': item.get('watchlist_count', 0)
                    })
                
                return symbols
        
        except Exception as e:
            print(f"Error getting trending symbols: {e}")
        
        return []

def demo():
    """Demo StockTwits scraper"""
    scraper = StockTwitsScraper()
    
    print("StockTwits Scraper Demo")
    print("="*70)
    
    # For Indian stocks, use US equivalent or company name
    # RELIANCE -> RIL (if listed on StockTwits)
    symbol = "AAPL"  # Using AAPL as demo since it's popular on StockTwits
    
    messages = scraper.scrape_discussions(symbol, limit=10)
    
    print(f"\nFound {len(messages)} messages for ${symbol}:")
    print("="*70)
    
    for i, msg in enumerate(messages[:5], 1):
        print(f"\n{i}. @{msg['author']}: {msg['text'][:80]}...")
        print(f"   Sentiment: {msg['sentiment']['label']} ({msg['sentiment']['score']:.2f})")
        print(f"   Likes: {msg['likes']}")
    
    # Trending symbols
    print("\n\nTrending Symbols:")
    print("="*70)
    trending = scraper.get_trending_symbols()
    for sym in trending[:5]:
        print(f"${sym['symbol']} - {sym['title']} ({sym['watchlist_count']} watchers)")

if __name__ == "__main__":
    demo()
