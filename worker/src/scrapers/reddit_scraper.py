"""
Reddit Scraper for Stock Discussion
Scrapes stock-related posts and comments from Reddit
"""

import praw
import os
from datetime import datetime, timedelta
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ml.sentiment_analysis import SentimentAnalyzer


class RedditScraper:
    """Scrape Reddit for stock discussions"""
    
    def __init__(self):
        # Reddit API credentials (need to be added to .env)
        client_id = os.getenv('REDDIT_CLIENT_ID', '')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'MarketAnalysis/1.0')
        
        if not client_id or not client_secret:
            print("⚠️  Reddit API credentials not found")
            print("   Get credentials from: https://www.reddit.com/prefs/apps")
            print("   Add to .env: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET")
            self.reddit = None
        else:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
            except Exception as e:
                print(f"Failed to initialize Reddit API: {e}")
                self.reddit = None
        
        self.sentiment_analyzer = SentimentAnalyzer()
        self.subreddits = ['IndianStockMarket', 'IndianStreetBets', 'investing', 'stocks']
    
    def scrape_discussions(self, symbol, limit=50):
        """
        Scrape Reddit discussions about a stock
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of posts to fetch
            
        Returns:
            List of posts with sentiment
        """
        if not self.reddit:
            return self._mock_data(symbol)
        
        posts = []
        
        try:
            for subreddit_name in self.subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for symbol
                    for submission in subreddit.search(symbol, limit=limit//len(self.subreddits), time_filter='week'):
                        # Analyze title + selftext
                        text = f"{submission.title}. {submission.selftext}"
                        sentiment = self.sentiment_analyzer.analyze_social(text)
                        
                        posts.append({
                            'title': submission.title,
                            'text': submission.selftext[:200],  # First 200 chars
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'created': datetime.fromtimestamp(submission.created_utc).isoformat(),
                            'url': f"https://reddit.com{submission.permalink}",
                            'subreddit': subreddit_name,
                            'sentiment': sentiment,
                            'source': 'Reddit'
                        })
                        
                except Exception as e:
                    print(f"Error scraping r/{subreddit_name}: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            print(f"Error scraping Reddit: {e}")
            return self._mock_data(symbol)
    
    def _mock_data(self, symbol):
        """Generate mock data when API is unavailable"""
        return [
            {
                'title': f'{symbol} looks bullish',
                'text': 'Strong fundamentals and technical breakout',
                'score': 42,
                'num_comments': 15,
                'created': datetime.now().isoformat(),
                'url': 'https://reddit.com',
                'subreddit': 'IndianStockMarket',
                'sentiment': {'score': 0.6, 'label': 'POSITIVE'},
                'source': 'Reddit (Mock)'
            },
            {
                'title': f'Concerns about {symbol} valuation',
                'text': 'PE ratio seems high compared to sector',
                'score': 28,
                'num_comments': 8,
                'created': (datetime.now() - timedelta(days=1)).isoformat(),
                'url': 'https://reddit.com',
                'subreddit': 'investing',
                'sentiment': {'score': -0.4, 'label': 'NEGATIVE'},
                'source': 'Reddit (Mock)'
            }
        ]
    
    def get_sentiment_summary(self, posts):
        """Calculate weighted sentiment from posts"""
        if not posts:
            return {'score': 0, 'label': 'NEUTRAL', 'count': 0}
        
        # Weight by score (upvotes)
        total_score = sum(p['score'] for p in posts)
        if total_score == 0:
            # Fallback to simple average
            scores = [p['sentiment']['score'] for p in posts]
            avg_score = sum(scores) / len(scores)
        else:
            weighted_sum = sum(p['sentiment']['score'] * p['score'] for p in posts)
            avg_score = weighted_sum / total_score
        
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
            'count': len(posts),
            'total_upvotes': total_score
        }


def demo():
    """Demo the scraper"""
    scraper = RedditScraper()
    
    symbol = "RELIANCE"
    print(f"Scraping Reddit for {symbol}...")
    
    posts =scraper.scrape_discussions(symbol, limit=10)
    
    print(f"\nFound {len(posts)} posts:")
    print("="*70)
    
    for i, post in enumerate(posts[:5], 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Subreddit: r/{post['subreddit']}")
        print(f"   Score: {post['score']} upvotes, {post['num_comments']} comments")
        print(f"   Sentiment: {post['sentiment']['label']} ({post['sentiment']['score']:.2f})")
    
    # Overall sentiment
    summary = scraper.get_sentiment_summary(posts)
    print("\n" + "="*70)
    print(f"Overall Sentiment: {summary['label']} ({summary['score']:.2f})")
    print(f"Total posts: {summary['count']}, Total upvotes: {summary.get('total_upvotes', 0)}")


if __name__ == "__main__":
    demo()
