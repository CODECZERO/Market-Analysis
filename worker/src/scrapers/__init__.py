"""
Scrapers Package
News and social media scrapers for sentiment analysis
"""

from .moneycontrol_scraper import MoneyControlScraper
from .economictimes_scraper import EconomicTimesScraper
from .business_standard_scraper import BusinessStandardScraper
from .stocktwits_scraper import StockTwitsScraper
from .reddit_scraper import RedditScraper
from .twitter_scraper import XTwitterScraper
from .news_aggregator import NewsAggregator
from .aggregator_adapter import AggregatorAdapter

__all__ = [
    'MoneyControlScraper',
    'EconomicTimesScraper',
    'BusinessStandardScraper',
    'StockTwitsScraper',
    'RedditScraper',
    'XTwitterScraper',
    'NewsAggregator',
    'AggregatorAdapter'  # Recommended: 9-platform coverage!
]
