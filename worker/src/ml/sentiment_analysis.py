"""
Sentiment Analysis with Fusion
Combines VADER (for social media) and FinBERT (for financial news)
Applies volatility scaling for robust sentiment signals
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
except ImportError:
    HAS_VADER = False
    logging.warning("VADER not available")

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not available")

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Fused sentiment analysis for financial data
    """
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer() if HAS_VADER else None
        self.finbert = None
        
        if HAS_TRANSFORMERS:
            try:
                self.finbert = pipeline(
                    "text-classification",
                    model="ProsusAI/finbert",
                    top_k=None
                )
            except Exception as e:
                logger.warning(f"Could not load FinBERT: {e}")
    
    def analyze_social_media(self, texts: List[str]) -> Dict[str, any]:
        """
        Analyze social media posts using VADER
        
        Args:
            texts: List of social media posts/tweets
            
        Returns:
            Aggregated sentiment scores
        """
        if not self.vader:
            logger.warning("VADER not available, returning neutral sentiment")
            return {
                'compound': 0.0,
                'positive_ratio': 0.5,
                'negative_ratio': 0.5,
                'neutral_ratio': 0.5,
                'count': 0
            }
        
        if not texts:
            return {
                'compound': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 1.0,
                'count': 0
            }
        
        scores = []
        for text in texts:
            score = self.vader.polarity_scores(text)
            scores.append(score)
        
        # Aggregate
        compound_scores = [s['compound'] for s in scores]
        pos_count = sum(1 for s in scores if s['compound'] > 0.05)
        neg_count = sum(1 for s in scores if s['compound'] < -0.05)
        neu_count = len(scores) - pos_count - neg_count
        
        return {
            'compound': float(np.mean(compound_scores)),
            'positive_ratio': pos_count / len(scores),
            'negative_ratio': neg_count / len(scores),
            'neutral_ratio': neu_count / len(scores),
            'count': len(scores),
            'std': float(np.std(compound_scores))
        }
    
    def analyze_news(self, articles: List[str]) -> Dict[str, any]:
        """
        Analyze financial news using FinBERT
        
        Args:
            articles: List of news article texts
            
        Returns:
            Aggregated sentiment scores
        """
        if not self.finbert:
            logger.warning("FinBERT not available, using fallback")
            return self._simple_news_sentiment(articles)
        
        if not articles:
            return {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'count': 0
            }
        
        sentiments = []
        for article in articles:
            # Truncate to 512 tokens (FinBERT limit)
            truncated = article[:512]
            try:
                result = self.finbert(truncated)[0]
                sentiments.append(result)
            except Exception as e:
                logger.debug(f"FinBERT analysis failed: {e}")
                continue
        
        if not sentiments:
            return self._simple_news_sentiment(articles)
        
        # Aggregate scores
        pos_scores = []
        neg_scores = []
        neu_scores = []
        
        for sentiment_list in sentiments:
            sentiment_dict = {s['label']: s['score'] for s in sentiment_list}
            pos_scores.append(sentiment_dict.get('positive', 0))
            neg_scores.append(sentiment_dict.get('negative', 0))
            neu_scores.append(sentiment_dict.get('neutral', 0))
        
        return {
            'positive': float(np.mean(pos_scores)),
            'negative': float(np.mean(neg_scores)),
            'neutral': float(np.mean(neu_scores)),
            'count': len(sentiments),
            'net_score': float(np.mean(pos_scores) - np.mean(neg_scores))
        }
    
    def _simple_news_sentiment(self, articles: List[str]) -> Dict[str, any]:
        """Fallback sentiment using keyword matching"""
        if not articles:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'count': 0}
        
        positive_keywords = ['surge', 'rally', 'gain', 'profit', 'growth', 'beat', 'upgrade']
        negative_keywords = ['fall', 'drop', 'loss', 'decline', 'downgrade', 'miss', 'crash']
        
        pos_count = 0
        neg_count = 0
        
        for article in articles:
            article_lower = article.lower()
            pos_count += sum(keyword in article_lower for keyword in positive_keywords)
            neg_count += sum(keyword in article_lower for keyword in negative_keywords)
        
        total = max(pos_count + neg_count, 1)
        
        return {
            'positive': pos_count / total,
            'negative': neg_count / total,
            'neutral': 1 - ((pos_count + neg_count) / total),
            'count': len(articles),
            'net_score': (pos_count - neg_count) / total,
            'method': 'keyword_fallback'
        }


def fuse_sentiment(
    social_sentiment: Dict[str, any],
    news_sentiment: Dict[str, any],
    volatility: float,
    social_weight: float = 0.4,
    news_weight: float = 0.6
) -> Dict[str, any]:
    """
    Fuse social media and news sentiment with volatility scaling
    
    Args:
        social_sentiment: Output from analyze_social_media
        news_sentiment: Output from analyze_news
        volatility: Current stock volatility (0-1 scale)
        social_weight: Weight for social sentiment (default 0.4)
        news_weight: Weight for news sentiment (default 0.6)
        
    Returns:
        Fused sentiment score
    """
    # Convert VADER compound (-1 to 1) to comparable scale
    social_score = social_sentiment.get('compound', 0)
    
    # FinBERT net score (pos - neg)
    news_score = news_sentiment.get('net_score', 0)
    
    # Volatility scaling: reduce sentiment influence during high volatility
    volatility_weight = 1.0 / (1.0 + volatility * 2)  # Higher vol → lower weight
    
    # Weighted fusion
    fused = (social_score * social_weight + news_score * news_weight) * volatility_weight
    
    return {
        'fused_sentiment': float(fused),
        'social_component': float(social_score * social_weight),
        'news_component': float(news_score * news_weight),
        'volatility_scaling': float(volatility_weight),
        'signal': 'POSITIVE' if fused > 0.2 else 'NEGATIVE' if fused < -0.2 else 'NEUTRAL',
        'confidence': min(abs(fused), 1.0),
        'social_data_points': social_sentiment.get('count', 0),
        'news_data_points': news_sentiment.get('count', 0),
    }


def calculate_sentiment_velocity(
    sentiment_series: pd.Series,
    window: int = 3
) -> float:
    """
    Calculate rate of change of sentiment (momentum indicator)
    
    Args:
        sentiment_series: Time series of sentiment scores
        window: Lookback window for slope calculation
        
    Returns:
        Sentiment velocity (positive = improving, negative = deteriorating)
    """
    if len(sentiment_series) < window:
        return 0.0
    
    recent = sentiment_series.tail(window).values
    x = np.arange(len(recent))
    
    # Linear regression slope
    slope = np.polyfit(x, recent, 1)[0]
    
    return float(slope)
