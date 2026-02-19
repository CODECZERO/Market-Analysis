"""
Aggregator Service Adapter
Reuses the existing aggregator service to fetch mentions for stock symbols
This leverages all working providers: Reddit, X, Bluesky, News, HN, etc.
"""

import requests
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ml.sentiment_analysis import SentimentAnalyzer


class AggregatorAdapter:
    """
    Adapter to use existing aggregator service for stock data
    
    The aggregator already has working providers for:
    - Reddit
    - X/Twitter  
    - Bluesky
    - News API
    - Hacker News
    - Google Search
    - DuckDuckGo
    - YouTube
    - RSS feeds
    
    We just adapt it to search for stock symbols instead of brand names
    """
    
    def __init__(self, aggregator_url=None):
        self.aggregator_url = aggregator_url or os.getenv('AGGREGATOR_URL', 'http://localhost:4001')
        self.sentiment_analyzer = SentimentAnalyzer()
        self.session = requests.Session()
    
    def create_stock_brand(self, symbol: str, company_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a temporary "brand" for the stock symbol
        The aggregator treats stocks like brands
        """
        brand = {
            "name": symbol,
            "aliases": [],
            "keywords": [f"${symbol}", f"#{symbol}"]
        }
        
        if company_info:
            company_name = company_info.get('longName')
            if company_name:
                brand["aliases"].append(company_name)
                brand["keywords"].append(company_name)
            
            # 🆕 Add People Data (CEO/Founders)
            ceo = company_info.get('officer1_name') or company_info.get('company_officers', [{}])[0].get('name')
            if ceo:
                brand["keywords"].append(ceo)
                brand["aliases"].append(ceo)
                print(f"   👤 Added CEO tracking: {ceo}")
        
        # Add common stock-related keywords
        brand["keywords"].extend([
            f"{symbol} stock",
            f"{symbol} share",
            f"{symbol} price"
        ])
        
        return brand
    
    def fetch_mentions(self, symbol: str, company_name: str = None, platforms: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Fetch mentions from aggregator for a stock symbol
        
        Args:
            symbol: Stock symbol
            company_name: Optional company name
            platforms: List of platforms to fetch from (default: all)
            
        Returns:
            Dict mapping platform -> list of mentions
        """
        # Default to all platforms if not specified
        if platforms is None:
            platforms = ['reddit', 'x', 'bluesky', 'news', 'hn', 'youtube']
        
        try:
            # First, register the stock as a "brand" in aggregator
            # Fetch company info if not provided to get CEO data
            company_info = company_name if isinstance(company_name, dict) else {'longName': company_name}
            brand = self.create_stock_brand(symbol, company_info)
            
            # Call aggregator API to create/update brand
            create_response = self.session.post(
                f"{self.aggregator_url}/api/brands",
                json=brand,
                timeout=10
            )
            
            if create_response.status_code == 201 or create_response.status_code == 200:
                brand_data = create_response.json()
                brand_id = brand_data.get('data', {}).get('id')
                
                if not brand_id:
                    print("⚠️  Failed to get brand ID from aggregator")
                    return self._get_fallback_data(symbol)
                
                # Trigger aggregation for this brand
                aggregate_response = self.session.post(
                    f"{self.aggregator_url}/api/brands/{brand_id}/aggregate",
                    timeout=30
                )
                
                if aggregate_response.status_code == 200:
                    # Fetch the mentions
                    mentions_response = self.session.get(
                        f"{self.aggregator_url}/api/brands/{brand_id}/mentions",
                        params={'limit': 100},
                        timeout=10
                    )
                    
                    if mentions_response.status_code == 200:
                        mentions_data = mentions_response.json()
                        mentions = mentions_data.get('data', [])
                        
                        # Group by platform and analyze sentiment
                        return self._process_mentions(mentions)
                    
            print(f"⚠️  Aggregator returned status {create_response.status_code}")
            return self._get_fallback_data(symbol)
                
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Cannot connect to aggregator at {self.aggregator_url}")
            print("   Make sure aggregator is running: cd aggregator && npm start")
            return self._get_fallback_data(symbol)
        except Exception as e:
            print(f"⚠️  Error fetching from aggregator: {e}")
            return self._get_fallback_data(symbol)
    
    def _process_mentions(self, mentions: List[Dict]) -> Dict[str, List[Dict]]:
        """Process mentions from aggregator and add sentiment"""
        grouped = {}
        
        for mention in mentions:
            platform = mention.get('platform', 'unknown')
            text = mention.get('text', '')
            
            # Analyze sentiment
            if platform in ['reddit', 'x', 'twitter', 'bluesky']:
                sentiment = self.sentiment_analyzer.analyze_social(text)
            else:
                sentiment = self.sentiment_analyzer.analyze_news(text)
            
            processed = {
                'id': mention.get('id'),
                'text': text,
                'author': mention.get('author', 'unknown'),
                'timestamp': mention.get('timestamp'),
                'url': mention.get('url', ''),
                'score': mention.get('score', 0),
                'sentiment': sentiment,
                'platform': platform
            }
            
            if platform not in grouped:
                grouped[platform] = []
            grouped[platform].append(processed)
        
        return grouped
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, List[Dict]]:
        """Return empty data when aggregator is unavailable"""
        print(f"   Using fallback (empty) data for {symbol}")
        return {
            'reddit': [],
            'x': [],
            'news': [],
            'bluesky': [],
            'hn': []
        }
    
    def get_combined_sentiment(self, mentions_by_platform: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate combined sentiment across all platforms"""
        all_mentions = []
        for platform_mentions in mentions_by_platform.values():
            all_mentions.extend(platform_mentions)
        
        if not all_mentions:
            return {
                'score': 0,
                'label': 'NEUTRAL',
                'count': 0,
                'by_platform': {}
            }
        
        # Weight by score (engagement)
        total_score = sum(m.get('score', 1) for m in all_mentions)
        
        if total_score == 0:
            # Simple average
            scores = [m['sentiment']['score'] for m in all_mentions]
            avg_score = sum(scores) / len(scores)
        else:
            # Weighted average
            weighted_sum = sum(
                m['sentiment']['score'] * m.get('score', 1)
                for m in all_mentions
            )
            avg_score = weighted_sum / total_score
        
        # Determine label
        if avg_score > 0.3:
            label = 'POSITIVE'
        elif avg_score < -0.3:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        # Calculate per-platform sentiment
        by_platform = {}
        for platform, mentions in mentions_by_platform.items():
            if mentions:
                platform_scores = [m['sentiment']['score'] for m in mentions]
                platform_avg = sum(platform_scores) / len(platform_scores)
                by_platform[platform] = {
                    'score': platform_avg,
                    'count': len(mentions)
                }
        
        return {
            'score': avg_score,
            'label': label,
            'count': len(all_mentions),
            'by_platform': by_platform
        }


def demo():
    """Demo the aggregator adapter"""
    adapter = AggregatorAdapter()
    
    symbol = "RELIANCE"
    company_name = "Reliance Industries"
    
    print(f"Fetching data for {symbol} via aggregator...\n")
    
    mentions = adapter.fetch_mentions(symbol, company_name)
    
    print("\nMentions by platform:")
    print("="*70)
    for platform, platform_mentions in mentions.items():
        print(f"{platform}: {len(platform_mentions)} mentions")
    
    # Show sample mentions
    print("\nSample mentions:")
    print("="*70)
    for platform, platform_mentions in mentions.items():
        if platform_mentions:
            mention = platform_mentions[0]
            print(f"\n[{platform}] {mention['text'][:100]}...")
            print(f"Sentiment: {mention['sentiment']['label']} ({mention['sentiment']['score']:.2f})")
    
    # Combined sentiment
    combined = adapter.get_combined_sentiment(mentions)
    print("\n" + "="*70)
    print(f"Combined Sentiment: {combined['label']} ({combined['score']:.2f})")
    print(f"Total mentions: {combined['count']}")
    print(f"\nBy platform: {combined['by_platform']}")


if __name__ == "__main__":
    demo()
