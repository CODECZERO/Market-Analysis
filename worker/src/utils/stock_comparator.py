"""
Stock Comparison Utility
Compares sentiment, technicals, and ML predictions across stocks
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np

class StockComparator:
    def __init__(self):
        pass

    def compare_stocks(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Produce a comparison report between multiple stock analysis outputs
        """
        if not stocks_data:
            return {}

        comparison = {
            "symbols": [s.get('symbol') for s in stocks_data],
            "price_performance": {},
            "sentiment_ranking": [],
            "technical_alignment": {},
            "recommendation_summary": {}
        }

        # Sentiment Ranking
        sentiment_list = []
        for stock in stocks_data:
            symbol = stock.get('symbol')
            sentiment = stock.get('sentiment_score', 0.5)
            sentiment_list.append({"symbol": symbol, "score": sentiment})
        
        comparison["sentiment_ranking"] = sorted(sentiment_list, key=lambda x: x['score'], reverse=True)

        # Recommendation Matrix
        recs = {}
        for stock in stocks_data:
            symbol = stock.get('symbol')
            rec = stock.get('recommendation', 'HOLD')
            recs[symbol] = rec
        comparison["recommendation_summary"] = recs

        # Relative Technical Strength
        # (e.g., comparing RSIs)
        rsi_map = {}
        for stock in stocks_data:
            symbol = stock.get('symbol')
            rsi = stock.get('technical_indicators', {}).get('rsi', {}).get('value', 50)
            rsi_map[symbol] = rsi
        comparison["technical_alignment"]["rsi"] = rsi_map

        return comparison

def generate_comparison_text(comparison: Dict[str, Any]) -> str:
    """Helper to generate a text summary of the comparison"""
    if not comparison:
        return "No data for comparison."
    
    lines = ["STOCKS COMPARISON REPORT"]
    lines.append("=" * 25)
    
    # Best Sentiment
    top_sent = comparison["sentiment_ranking"][0]
    lines.append(f"🔥 Highest Sentiment: {top_sent['symbol']} ({top_sent['score']:.0%})")
    
    # Recommendation Summary
    lines.append("\nRecommendations:")
    for sym, rec in comparison["recommendation_summary"].items():
        lines.append(f"  • {sym}: {rec}")
        
    return "\n".join(lines)
