"""
Finnhub API Provider
Real-time stock data, fundamentals, and news from Finnhub
Requires API key: https://finnhub.io/
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

class FinnhubProvider:
    """Finnhub API provider for stock data and news"""
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY', '')
        self.session = requests.Session()
        
        if not self.api_key:
            print("⚠️  FINNHUB_API_KEY not set, using mock data")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        if not self.api_key:
            return None
        
        if params is None:
            params = {}
        
        params['token'] = self.api_key
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️  Rate limit exceeded, waiting...")
                time.sleep(60)
                return None
            else:
                print(f"⚠️  Finnhub API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error calling Finnhub API: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        data = self._make_request('quote', {'symbol': symbol})
        
        if data:
            return {
                'symbol': symbol,
                'current_price': data.get('c', 0),
                'change': data.get('d', 0),
                'change_percent': data.get('dp', 0),
                'high': data.get('h', 0),
                'low': data.get('l', 0),
                'open': data.get('o', 0),
                'previous_close': data.get('pc', 0),
                'timestamp': data.get('t', int(time.time()))
            }
        
        return self._mock_quote(symbol)
    
    def get_company_profile(self, symbol: str) -> Dict:
        """Get company fundamentals"""
        data = self._make_request('stock/profile2', {'symbol': symbol})
        
        if data:
            return {
                'symbol': symbol,
                'name': data.get('name', ''),
                'country': data.get('country', ''),
                'currency': data.get('currency', ''),
                'exchange': data.get('exchange', ''),
                'ipo': data.get('ipo', ''),
                'market_cap': data.get('marketCapitalization', 0),
                'shares_outstanding': data.get('shareOutstanding', 0),
                'industry': data.get('finnhubIndustry', ''),
                'logo': data.get('logo', ''),
                'weburl': data.get('weburl', '')
            }
        
        return self._mock_profile(symbol)
    
    def get_company_news(self, symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get company news"""
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        data = self._make_request('company-news', {
            'symbol': symbol,
            'from': from_date,
            'to': to_date
        })
        
        if data and isinstance(data, list):
            news = []
            for item in data[:20]:  # Limit to 20 articles
                news.append({
                    'title': item.get('headline', ''),
                    'description': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Finnhub'),
                    'published_at': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    'image': item.get('image', ''),
                    'category': item.get('category', ''),
                    'symbol': symbol
                })
            return news
        
        return self._mock_news(symbol)
    
    def get_market_news(self, category: str = 'general') -> List[Dict]:
        """Get general market news"""
        data = self._make_request('news', {'category': category})
        
        if data and isinstance(data, list):
            news = []
            for item in data[:15]:
                news.append({
                    'title': item.get('headline', ''),
                    'description': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Finnhub'),
                    'published_at': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    'image': item.get('image', ''),
                    'category': category
                })
            return news
        
        return []
    
    def get_basic_financials(self, symbol: str) -> Dict:
        """Get basic financial metrics"""
        data = self._make_request('stock/metric', {'symbol': symbol, 'metric': 'all'})
        
        if data and 'metric' in data:
            metrics = data['metric']
            return {
                'symbol': symbol,
                'pe_ratio': metrics.get('peNormalizedAnnual', 0),
                'pb_ratio': metrics.get('pbAnnual', 0),
                'dividend_yield': metrics.get('dividendYieldIndicatedAnnual', 0),
                'eps': metrics.get('epsInclExtraItemsAnnual', 0),
                'beta': metrics.get('beta', 0),
                '52week_high': metrics.get('52WeekHigh', 0),
                '52week_low': metrics.get('52WeekLow', 0),
                'roa': metrics.get('roaRfy', 0),
                'roe': metrics.get('roeRfy', 0),
                'profit_margin': metrics.get('netProfitMarginAnnual', 0)
            }
        
        return {}
    
    def get_recommendations(self, symbol: str) -> List[Dict]:
        """Get analyst recommendations"""
        data = self._make_request('stock/recommendation', {'symbol': symbol})
        
        if data and isinstance(data, list) and len(data) > 0:
            latest = data[0]
            return {
                'symbol': symbol,
                'strong_buy': latest.get('strongBuy', 0),
                'buy': latest.get('buy', 0),
                'hold': latest.get('hold', 0),
                'sell': latest.get('sell', 0),
                'strong_sell': latest.get('strongSell', 0),
                'period': latest.get('period', '')
            }
        
        return {}
    
    def _mock_quote(self, symbol: str) -> Dict:
        """Mock quote data"""
        return {
            'symbol': symbol,
            'current_price': 2456.80,
            'change': 25.40,
            'change_percent': 1.04,
            'high': 2475.00,
            'low': 2430.00,
            'open': 2440.00,
            'previous_close': 2431.40,
            'timestamp': int(time.time())
        }
    
    def _mock_profile(self, symbol: str) -> Dict:
        """Mock profile data"""
        return {
            'symbol': symbol,
            'name': f'{symbol} Limited',
            'country': 'IN',
            'currency': 'INR',
            'exchange': 'NSE',
            'market_cap': 1650000,
            'industry': 'Technology'
        }
    
    def _mock_news(self, symbol: str) -> List[Dict]:
        """Mock news data"""
        return [
            {
                'title': f'{symbol} announces quarterly results',
                'description': 'Company reports strong growth in Q4',
                'url': 'https://finnhub.io',
                'source': 'Finnhub (Mock)',
                'published_at': datetime.now().isoformat(),
                'symbol': symbol
            }
        ]

def demo():
    """Demo Finnhub provider"""
    provider = FinnhubProvider()
    
    print("Finnhub Provider Demo")
    print("="*70)
    
    symbol = "AAPL"  # Using US symbol for demo
    
    # Quote
    print(f"\nReal-time Quote for {symbol}:")
    quote = provider.get_quote(symbol)
    print(f"Price: ${quote['current_price']}")
    print(f"Change: {quote['change']} ({quote['change_percent']}%)")
    
    # Profile
    print(f"\nCompany Profile:")
    profile = provider.get_company_profile(symbol)
    print(f"Name: {profile['name']}")
    print(f"Market Cap: ${profile['market_cap']}B")
    print(f"Industry: {profile['industry']}")
    
    # News
    print(f"\nRecent News:")
    news = provider.get_company_news(symbol)
    for i, article in enumerate(news[:3], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
    
    # Financials
    print(f"\nBasic Financials:")
    financials = provider.get_basic_financials(symbol)
    if financials:
        print(f"P/E Ratio: {financials.get('pe_ratio', 'N/A')}")
        print(f"EPS: ${financials.get('eps', 'N/A')}")

if __name__ == "__main__":
    demo()
