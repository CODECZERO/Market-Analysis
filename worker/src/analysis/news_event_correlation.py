"""
News-Event to Price Correlation Engine
Analyze how news events correlate with price movements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import yfinance as yf

class NewsEventCorrelation:
    """Analyze correlation between news events and price movements"""
    
    def __init__(self):
        self.price_data = {}
        self.news_events = []
    
    def add_news_event(self, date: str, sentiment_score: float, 
                      source: str, title: str):
        """
        Add a news event
        
        Args:
            date: Date of news (YYYY-MM-DD)
            sentiment_score: -1 to 1 (negative to positive)
            source: News source
            title: News title
        """
        self.news_events.append({
            'date': pd.to_datetime(date),
            'sentiment': sentiment_score,
            'source': source,
            'title': title
        })
    
    def load_price_data(self, symbol: str, period: str = '1y'):
        """Load historical price data"""
        ticker = yf.Ticker(symbol)
        self.price_data[symbol] = ticker.history(period=period)
    
    def calculate_price_reaction(self, symbol: str, event_date: datetime, 
                                lag_days: List[int] = [0, 1, 2, 3, 5, 7]) -> Dict:
        """
        Calculate price reaction to news event
        
        Args:
            symbol: Stock symbol
            event_date: Date of event
            lag_days: Days after event to measure (0=same day, 1=next day, etc.)
        
        Returns:
            Dict with price changes for each lag period
        """
        if symbol not in self.price_data:
            self.load_price_data(symbol)
        
        df = self.price_data[symbol]
        
        # Find closest date in price data
        event_date = pd.to_datetime(event_date)
        closest_idx = df.index.get_indexer([event_date], method='nearest')[0]
        
        if closest_idx == -1:
            return {}
        
        event_price = df.iloc[closest_idx]['Close']
        reactions = {}
        
        for lag in lag_days:
            future_idx = closest_idx + lag
            
            if future_idx < len(df):
                future_price = df.iloc[future_idx]['Close']
                price_change = ((future_price - event_price) / event_price) * 100
                
                reactions[f'T+{lag}'] = {
                    'price_change_percent': float(price_change),
                    'event_price': float(event_price),
                    'future_price': float(future_price)
                }
        
        return reactions
    
    def analyze_news_price_correlation(self, symbol: str) -> Dict:
        """
        Analyze overall correlation between news sentiment and price changes
        """
        if not self.news_events:
            return {'error': 'No news events loaded'}
        
        if symbol not in self.price_data:
            self.load_price_data(symbol)
        
        # Group news by date
        news_df = pd.DataFrame(self.news_events)
        daily_sentiment = news_df.groupby(news_df['date'].dt.date)['sentiment'].mean()
        
        # Calculate daily returns
        price_df = self.price_data[symbol]
        price_df['returns'] = price_df['Close'].pct_change() * 100
        
        # Align dates
        correlations = {}
        
        for lag in [0, 1, 2, 3, 5, 7]:
            aligned_data = []
            
            for date, sentiment in daily_sentiment.items():
                # Find price data for lag days later
                target_date = pd.to_datetime(date) + timedelta(days=lag)
                
                if target_date in price_df.index:
                    price_return = price_df.loc[target_date, 'returns']
                    if not np.isnan(price_return):
                        aligned_data.append({
                            'sentiment': sentiment,
                            'return': price_return
                        })
            
            if len(aligned_data) > 3:
                aligned_df = pd.DataFrame(aligned_data)
                corr, p_value = pearsonr(aligned_df['sentiment'], aligned_df['return'])
                
                correlations[f'lag_{lag}d'] = {
                    'correlation': float(corr),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'samples': len(aligned_data)
                }
        
        return correlations
    
    def identify_high_impact_news(self, symbol: str, threshold: float = 2.0) -> List[Dict]:
        """
        Identify news events that caused significant price movements
        
        Args:
            threshold: Minimum price change % to be considered high impact
        """
        high_impact = []
        
        for event in self.news_events:
            reactions = self.calculate_price_reaction(symbol, event['date'])
            
            # Check T+1 (next day) reaction
            if 'T+1' in reactions:
                price_change = abs(reactions['T+1']['price_change_percent'])
                
                if price_change >= threshold:
                    high_impact.append({
                        'date': event['date'].strftime('%Y-%m-%d'),
                        'title': event['title'],
                        'sentiment': event['sentiment'],
                        'price_change': reactions['T+1']['price_change_percent'],
                        'impact': 'HIGH'
                    })
        
        # Sort by impact
        high_impact.sort(key=lambda x: abs(x['price_change']), reverse=True)
        
        return high_impact
    
    def generate_correlation_report(self, symbol: str) -> str:
        """Generate a text report of correlations"""
        correlations = self.analyze_news_price_correlation(symbol)
        high_impact = self.identify_high_impact_news(symbol)
        
        report = f"News-Event Correlation Report for {symbol}\n"
        report += "="*70 + "\n\n"
        
        report += "Sentiment-Price Correlations by Lag:\n"
        report += "-"*70 + "\n"
        
        for lag, data in correlations.items():
            sig = "✓" if data['significant'] else "✗"
            report += f"{lag}: r={data['correlation']:+.3f} (p={data['p_value']:.4f}) {sig}\n"
        
        report += "\n\nHigh Impact News Events:\n"
        report += "-"*70 + "\n"
        
        for i, event in enumerate(high_impact[:5], 1):
            report += f"\n{i}. {event['date']}: {event['title'][:60]}...\n"
            report += f"   Sentiment: {event['sentiment']:+.2f}\n"
            report += f"   Price Impact: {event['price_change']:+.2f}%\n"
        
        return report

def demo():
    """Demo news-event correlation"""
    analyzer = NewsEventCorrelation()
    
    print("News-Event Correlation Demo")
    print("="*70)
    
    symbol = "RELIANCE.NS"
    
    # Load price data
    print(f"\nLoading price data for {symbol}...")
    analyzer.load_price_data(symbol)
    
    # Add mock news events
    print("Adding news events...")
    analyzer.add_news_event('2024-01-15', 0.8, 'MoneyControl', 'Reliance reports record quarterly profit')
    analyzer.add_news_event('2024-01-20', -0.6, 'ET', 'Reliance faces regulatory scrutiny')
    analyzer.add_news_event('2024-02-01', 0.5, 'BS', 'Reliance expands digital services')
    
    # Calculate event reactions
    print("\n\nPrice Reaction to News Events:")
    print("="*70)
    
    event_date = '2024-01-15'
    reactions = analyzer.calculate_price_reaction(symbol, event_date)
    
    print(f"\nEvent: {event_date}")
    for period, data in reactions.items():
        print(f"{period}: {data['price_change_percent']:+.2f}%")
    
    # Overall correlation
    print("\n\nSentiment-Price Correlation Analysis:")
    print("="*70)
    correlations = analyzer.analyze_news_price_correlation(symbol)
    
    for lag, data in correlations.items():
        sig = "✓ Significant" if data.get('significant') else "Not significant"
        print(f"\n{lag}:")
        print(f"  Correlation: {data['correlation']:+.3f}")
        print(f"  P-value: {data['p_value']:.4f}")
        print(f"  {sig}")
    
    # High impact events
    print("\n\nHigh Impact News:")
    print("="*70)
    high_impact = analyzer.identify_high_impact_news(symbol, threshold=1.5)
    
    for i, event in enumerate(high_impact[:3], 1):
        print(f"\n{i}. {event['date']}: {event['title'][:60]}...")
        print(f"   Impact: {event['price_change']:+.2f}%")

if __name__ == "__main__":
    demo()
