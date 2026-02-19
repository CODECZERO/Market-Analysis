"""
News Scraper - MoneyControl
Scrapes stock news and performs sentiment analysis
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ml.sentiment_analysis import SentimentAnalyzer


class MoneyControlScraper:
    """Scrape news from MoneyControl"""
    
    BASE_URL = "https://www.moneycontrol.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def get_stock_url(self, symbol):
        """Convert symbol to MoneyControl URL format"""
        # MoneyControl uses URLs like: /news/business/stocks/company-name-stock-number
        # For simplicity, use search
        return f"{self.BASE_URL}/stocks/cptmarket/comstock_search.php?search_data={symbol}"
    
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
            # Search for stock
            search_url = f"{self.BASE_URL}/news/business/stocks/?search={symbol}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Find news articles
            news_items = soup.find_all('li', class_='clearfix')[:max_articles]
            
            for item in news_items:
                try:
                    # Extract title
                    title_elem = item.find('h2') or item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    link = title_elem.find('a')['href'] if title_elem.find('a') else ""
                    
                    # Extract date
                    date_elem = item.find('span')
                    date = date_elem.get_text().strip() if date_elem else "Unknown"
                    
                    # Extract summary
                    summary_elem = item.find('p')
                    summary = summary_elem.get_text().strip() if summary_elem else title
                    
                    # Analyze sentiment
                    sentiment = self.sentiment_analyzer.analyze_news(title + ". " + summary)
                    
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'link': link if link.startswith('http') else self.BASE_URL + link,
                        'date': date,
                        'sentiment': sentiment,
                        'source': 'MoneyControl'
                    })
                    
                    # Be respectful - small delay
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error scraping MoneyControl: {e}")
            return []
    
    def get_sentiment_summary(self, articles):
        """Calculate overall sentiment from articles"""
        if not articles:
            return {'score': 0, 'label': 'NEUTRAL', 'count': 0}
        
        # Robust score extraction with fallback
        scores = []
        for a in articles:
            sentiment = a.get('sentiment', {})
            if isinstance(sentiment, dict):
                 scores.append(sentiment.get('score', 0))
            else:
                 scores.append(0)
                 
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine label
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
    scraper = MoneyControlScraper()
    
    symbol = "RELIANCE"
    print(f"Scraping news for {symbol}...")
    
    articles = scraper.scrape_news(symbol, max_articles=5)
    
    print(f"\nFound {len(articles)} articles:")
    print("="*70)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Date: {article['date']}")
        print(f"   Sentiment: {article['sentiment']['label']} ({article['sentiment']['score']:.2f})")
        print(f"   Link: {article['link']}")
    
    # Overall sentiment
    summary = scraper.get_sentiment_summary(articles)
    print("\n" + "="*70)
    print(f"Overall Sentiment: {summary['label']} ({summary['score']:.2f})")
    print(f"Positive: {summary['positive']}, Neutral: {summary['neutral']}, Negative: {summary['negative']}")


if __name__ == "__main__":
    demo()
