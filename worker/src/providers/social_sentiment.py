"""
Social Sentiment Provider
"""
from typing import Dict, Any, List

def get_social_sentiment(symbol: str) -> Dict[str, Any]:
    # Mock return
    return {
        "score": 0.05,
        "label": "NEUTRAL",
        "mentions": 10,
        "source": "Mock"
    }

class RedditScraper:
    def get_sentiment_summary(self, posts: List) -> Dict:
        return {"score": 0.0, "label": "NEUTRAL"}
    
    def fetch_posts(self, symbol, limit=10):
        return []
