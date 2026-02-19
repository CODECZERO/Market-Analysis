"""
X (Twitter) Scraper for Stock Discussion
Adapted from aggregator's X provider for stock sentiment analysis
Uses nitter instances (free) or Twitter API v2 (if key available)
"""

import os
import requests
from datetime import datetime, timedelta
import time
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ml.sentiment_analysis import SentimentAnalyzer


class XTwitterScraper:
    """
    Scrape X (Twitter) for stock discussions
    
    Methods:
    1. Nitter (free, no API key) - scrapes public nitter instances
    2. Twitter API v2 (requires bearer token)
    """
    
    # Public Nitter instances (rotate if one fails)
    NITTER_INSTANCES = [
        "https://nitter.net",
        "https://nitter.poast.org",
        "https://nitter.privacydev.net"
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Check for Twitter API v2 bearer token
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        self.use_api = bool(self.twitter_bearer_token)
        
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def scrape_discussions(self, symbol, limit=50, method='nitter'):
        """
        Scrape Twitter discussions about a stock
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            limit: Maximum number of tweets
            method: 'nitter' (free) or 'api' (requires token)
            
        Returns:
            List of tweets with sentiment
        """
        if method == 'api' and self.use_api:
            return self._scrape_via_api(symbol, limit)
        else:
            return self._scrape_via_nitter(symbol, limit)
    
    def _scrape_via_nitter(self, symbol, limit):
        """Scrape via Nitter (free, no API key needed)"""
        tweets = []
        
        # Build search query
        query = f"${symbol} OR #{symbol} OR {symbol}"
        
        for instance in self.NITTER_INSTANCES:
            try:
                print(f"Trying Nitter instance: {instance}")
                
                url = f"{instance}/search"
                params = {
                    'q': query,
                    'f': 'tweets'  # tweets only, not users
                }
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    # Parse Nitter HTML
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    tweet_items = soup.find_all('div', class_='timeline-item')[:limit]
                    
                    for item in tweet_items:
                        try:
                            # Extract tweet text
                            text_elem = item.find('div', class_='tweet-content')
                            if not text_elem:
                                continue
                            
                            text = text_elem.get_text().strip()
                            
                            # Extract author
                            author_elem = item.find('a', class_='username')
                            author = author_elem.get_text().strip() if author_elem else "unknown"
                            
                            # Extract timestamp
                            time_elem = item.find('span', class_='tweet-date')
                            timestamp = time_elem.get('title') if time_elem else datetime.now().isoformat()
                            
                            # Extract link
                            link_elem = item.find('a', class_='tweet-link')
                            link = instance + link_elem['href'] if link_elem and link_elem.get('href') else ""
                            
                            # Analyze sentiment
                            sentiment = self.sentiment_analyzer.analyze_social(text)
                            
                            tweets.append({
                                'text': text,
                                'author': author,
                                'timestamp': timestamp,
                                'url': link,
                                'source': f'X/Twitter (via Nitter)',
                                'sentiment': sentiment,
                                'platform': 'twitter'
                            })
                            
                        except Exception as e:
                            print(f"Error parsing tweet: {e}")
                            continue
                    
                    if tweets:
                        print(f"Successfully scraped {len(tweets)} tweets from {instance}")
                        return tweets
                    
                # Be respectful
                time.sleep(1)
                    
            except Exception as e:
                print(f"Error with {instance}: {e}")
                continue
        
        # If all Nitter instances fail, return mock data
        print("⚠️  All Nitter instances failed, using mock data")
        return self._mock_data(symbol)
    
    def _scrape_via_api(self, symbol, limit):
        """Scrape via Twitter API v2 (requires bearer token)"""
        print("Using Twitter API v2...")
        
        url = "https://api.twitter.com/2/tweets/search/recent"
        
        headers = {
            "Authorization": f"Bearer {self.twitter_bearer_token}"
        }
        
        # Build query
        query = f"(${symbol} OR #{symbol} OR {symbol}) lang:en -is:retweet"
        
        params = {
            "query": query,
            "max_results": min(limit, 100),  # API limit 100
            "tweet.fields": "created_at,public_metrics,author_id",
            "expansions": "author_id",
            "user.fields": "username"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            tweets = []
            
            if 'data' in data:
                users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                
                for tweet in data['data']:
                    text = tweet.get('text', '')
                    author_id = tweet.get('author_id', '')
                    author = users.get(author_id, {}).get('username', 'unknown')
                    
                    sentiment = self.sentiment_analyzer.analyze_social(text)
                    
                    tweets.append({
                        'text': text,
                        'author': f"@{author}",
                        'timestamp': tweet.get('created_at', ''),
                        'url': f"https://twitter.com/{author}/status/{tweet['id']}",
                        'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                        'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                        'source': 'X/Twitter (API v2)',
                        'sentiment': sentiment,
                        'platform': 'twitter'
                    })
            
            return tweets
            
        except Exception as e:
            print(f"Twitter API error: {e}")
            return self._mock_data(symbol)
    
    def _mock_data(self, symbol):
        """Generate mock data when scraping fails"""
        return [
            {
                'text': f'${symbol} breaking out! Strong momentum',
                'author': '@trader123',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://twitter.com',
                'source': 'X/Twitter (Mock)',
                'sentiment': {'score': 0.8, 'label': 'POSITIVE'},
                'platform': 'twitter'
            },
            {
                'text': f'Concerns about {symbol} valuation at current levels',
                'author': '@analyst456',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'url': 'https://twitter.com',
                'source': 'X/Twitter (Mock)',
                'sentiment': {'score': -0.3, 'label': 'NEGATIVE'},
                'platform': 'twitter'
            }
        ]
    
    def get_sentiment_summary(self, tweets):
        """Calculate weighted sentiment from tweets"""
        if not tweets:
            return {'score': 0, 'label': 'NEUTRAL', 'count': 0}
        
        # Weight by engagement (likes + retweets)
        total_engagement = sum(t.get('likes', 0) + t.get('retweets', 0) for t in tweets)
        
        if total_engagement == 0:
            # Simple average
            scores = [t['sentiment']['score'] for t in tweets]
            avg_score = sum(scores) / len(scores)
        else:
            # Weighted average
            weighted_sum = sum(
                t['sentiment']['score'] * (t.get('likes', 0) + t.get('retweets', 0))
                for t in tweets
            )
            avg_score = weighted_sum / total_engagement
        
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
            'count': len(tweets),
            'total_engagement': total_engagement
        }


def demo():
    """Demo the scraper"""
    scraper = XTwitterScraper()
    
    symbol = "RELIANCE"
    print(f"Scraping X/Twitter for ${symbol}...\n")
    
    # Try Nitter first (free)
    tweets = scraper.scrape_discussions(symbol, limit=10, method='nitter')
    
    print(f"\nFound {len(tweets)} tweets:")
    print("="*70)
    
    for i, tweet in enumerate(tweets[:5], 1):
        print(f"\n{i}. @{tweet['author']}: {tweet['text'][:80]}...")
        print(f"   Sentiment: {tweet['sentiment']['label']} ({tweet['sentiment']['score']:.2f})")
        print(f"   Source: {tweet['source']}")
    
    # Overall sentiment
    summary = scraper.get_sentiment_summary(tweets)
    print("\n" + "="*70)
    print(f"Overall Sentiment: {summary['label']} ({summary['score']:.2f})")
    print(f"Total tweets: {summary['count']}")


if __name__ == "__main__":
    demo()
