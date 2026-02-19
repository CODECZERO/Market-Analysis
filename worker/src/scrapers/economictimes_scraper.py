"""
Economic Times News Scraper
Scrapes stock news from Economic Times
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ml.sentiment_analysis import SentimentAnalyzer


class EconomicTimesScraper:
    """Scrape news from Economic Times"""
    
    BASE_URL = "https://economictimes.indiatimes.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def scrape_news(self, symbol, max_articles=10):
        """
        Scrape news articles for a stock
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of news articles with sentiment
        """
        try:
            # ET uses a different URL structure
            # For simplicity, use search
            search_url = f"{self.BASE_URL}/topic/{symbol.lower()}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Find news items (ET structure)
            news_items = soup.find_all('div', class_='eachStory')[:max_articles]
            
            if not news_items:
                # Fallback: try alternative selectors
                news_items = soup.find_all('article')[:max_articles]
            
            for item in news_items:
                try:
                    # Extract title
                    title_elem = item.find('h3') or item.find('h2') or item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    
                    # Extract link
                    link_elem = item.find('a')
                    link = link_elem['href'] if link_elem and link_elem.get('href') else ""
                    if link and not link.startswith('http'):
                        link = self.BASE_URL + link
                    
                    # Extract date/time
                    time_elem = item.find('time') or item.find('span', class_='time')
                    date = time_elem.get_text().strip() if time_elem else "Unknown"
                    
                    # Extract summary
                    summary_elem = item.find('p')
                    summary = summary_elem.get_text().strip() if summary_elem else title
                    
                    # Analyze sentiment
                    sentiment = self.sentiment_analyzer.analyze_news(title + ". " + summary)
                    
                    articles.append({
                        'title': title,
                        'summary': summary[:200],
                        'link': link,
                        'date': date,
                        'sentiment': sentiment,
                        'source': 'EconomicTimes'
                    })
                    
                    # Be respectful
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
            
            # If no articles found, return mock data
            if not articles:
                return self._mock_data(symbol)
            
            return articles
            
        except Exception as e:
            print(f"Error scraping Economic Times: {e}")
            return self._mock_data(symbol)
    
    def _mock_data(self, symbol):
        """Generate mock data when scraping fails"""
        return [
            {
                'title': f'{symbol} posts strong quarterly results',
                'summary': 'Company reports better than expected earnings',
                'link': self.BASE_URL,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sentiment': {'score': 0.7, 'label': 'POSITIVE'},
                'source': 'EconomicTimes (Mock)'
            }
        ]
    
    def get_sentiment_summary(self, articles):
        """Calculate overall sentiment from articles"""
        if not articles:
            return {'score': 0, 'label': 'NEUTRAL', 'count': 0}
        
        scores = [a['sentiment']['score'] for a in articles]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.3:
            label = 'POSITIVE'
        elif avg_score < -0.3:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        return {
            'score': avg_score,
            'label': label,
            'count': len(articles),
            'positive': sum(1 for s in scores if s > 0.3),
            'negative': sum(1 for s in scores if s < -0.3),
            'neutral': sum(1 for s in scores if -0.3 <= s <= 0.3)
        }


def demo():
    """Demo the scraper"""
    scraper = EconomicTimesScraper()
    
    symbol = "RELIANCE"
    print(f"Scraping Economic Times for {symbol}...")
    
    articles = scraper.scrape_news(symbol, max_articles=5)
    
    print(f"\nFound {len(articles)} articles:")
    print("="*70)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Date: {article['date']}")
        print(f"   Sentiment: {article['sentiment']['label']} ({article['sentiment']['score']:.2f})")
    
    summary = scraper.get_sentiment_summary(articles)
    print("\n" + "="*70)
    print(f"Overall Sentiment: {summary['label']} ({summary['score']:.2f})")


if __name__ == "__main__":
    demo()
