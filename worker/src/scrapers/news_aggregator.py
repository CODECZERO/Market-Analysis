"""
Combined News Aggregator
Aggregates news from multiple sources with weighted sentiment
"""

import asyncio
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scrapers.moneycontrol_scraper import MoneyControlScraper
from scrapers.economictimes_scraper import EconomicTimesScraper


class NewsAggregator:
    """Aggregate news from multiple sources"""
    
    def __init__(self):
        self.scrapers = {
            'moneycontrol': MoneyControlScraper(),
            'economictimes': EconomicTimesScraper()
        }
    
    async def fetch_all_news(self, symbol: str, max_per_source: int = 5) -> Dict[str, Any]:
        """
        Fetch news from all sources concurrently
        
        Args:
            symbol: Stock symbol
            max_per_source: Max articles per source
            
        Returns:
            Dict with articles from each source and combined sentiment
        """
        results = {}
        all_articles = []
        
        # Fetch from each source
        for source_name, scraper in self.scrapers.items():
            try:
                print(f"Fetching from {source_name}...")
                articles = scraper.scrape_news(symbol, max_articles=max_per_source)
                results[source_name] = {
                    'articles': articles,
                    'sentiment': scraper.get_sentiment_summary(articles)
                }
                all_articles.extend(articles)
            except Exception as e:
                print(f"Error fetching from {source_name}: {e}")
                results[source_name] = {
                    'articles': [],
                    'sentiment': {'score': 0, 'label': 'NEUTRAL', 'count': 0}
                }
        
        # Calculate combined sentiment
        combined_sentiment = self._calculate_combined_sentiment(results)
        
        return {
            'symbol': symbol,
            'sources': results,
            'all_articles': all_articles,
            'combined_sentiment': combined_sentiment,
            'total_articles': len(all_articles)
        }
    
    def _calculate_combined_sentiment(self, results: Dict) -> Dict:
        """Calculate weighted sentiment across all sources"""
        total_articles = sum(r['sentiment']['count'] for r in results.values())
        
        if total_articles == 0:
            return {'score': 0, 'label': 'NEUTRAL', 'count': 0}
        
        # Weight by article count
        weighted_sum = sum(
            r['sentiment']['score'] * r['sentiment']['count']
            for r in results.values()
            if r['sentiment']['count'] > 0
        )
        
        avg_score = weighted_sum / total_articles
        
        if avg_score > 0.3:
            label = 'POSITIVE'
        elif avg_score < -0.3:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        return {
            'score': avg_score,
            'label': label,
            'count': total_articles
        }
    
    def format_summary(self, result: Dict) -> str:
        """Format aggregated news as readable summary"""
        summary = f"""
{'='*70}
NEWS SUMMARY: {result['symbol']}
{'='*70}

Total Articles: {result['total_articles']}

"""
        
        for source, data in result['sources'].items():
            sentiment = data['sentiment']
            summary += f"{source.upper()}:\n"
            summary += f"  Articles: {sentiment['count']}\n"
            summary += f"  Sentiment: {sentiment['label']} ({sentiment['score']:.2f})\n\n"
        
        combined = result['combined_sentiment']
        summary += f"COMBINED SENTIMENT: {combined['label']} ({combined['score']:.2f})\n"
        summary += f"{'='*70}\n"
        
        return summary


async def demo():
    """Demo the aggregator"""
    aggregator = NewsAggregator()
    
    symbol = "RELIANCE"
    print(f"Aggregating news for {symbol}...\n")
    
    result = await aggregator.fetch_all_news(symbol, max_per_source=3)
    
    print(aggregator.format_summary(result))
    
    print("\nRecent Headlines:")
    for i, article in enumerate(result['all_articles'][:5], 1):
        print(f"{i}. [{article['source']}] {article['title']}")
        print(f"   Sentiment: {article['sentiment']['label']}")


if __name__ == "__main__":
    asyncio.run(demo())
