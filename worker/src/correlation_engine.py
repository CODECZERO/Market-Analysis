"""
Correlation Engine
Computes multi-dimensional correlations for market analysis:
- Price-to-price (stock vs market, stock vs sector)
- Sentiment-to-price with time lags
- Volume-to-price
- News events-to-price impact
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from scipy.stats import pearsonr, spearmanr
from scipy.signal import correlate

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Multi-signal correlation analysis for stock market data
    """
    
    def _safe_num(self, val, default=0.0):
        if val is None: return default
        try:
            fval = float(val)
            return fval if not np.isnan(fval) else default
        except: return default
    
    def __init__(self):
        self.correlation_cache = {}
    
    def compute_all_correlations(
        self,
        stock_prices: pd.Series,
        market_prices: pd.Series,
        sector_prices: Optional[pd.Series] = None,
        sentiment_series: Optional[pd.Series] = None,
        volume_series: Optional[pd.Series] = None,
        news_events: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Compute all correlation metrics
        
        Args:
            stock_prices: Stock price series (indexed by date)
            market_prices: Market index prices (Nifty 50)
            sector_prices: Sector index prices (optional)
            sentiment_series: Sentiment scores over time (optional)
            volume_series: Trading volume series (optional)
            news_events: DataFrame with news events and dates (optional)
            
        Returns:
            Dictionary with all correlation metrics
        """
        results = {}
        
        # Price-to-price correlations
        results['price_correlations'] = self._compute_price_correlations(
            stock_prices,
            market_prices,
            sector_prices
        )
        
        # Sentiment-to-price correlations with lags
        if sentiment_series is not None:
            results['sentiment_correlations'] = self._compute_sentiment_correlations(
                stock_prices,
                sentiment_series
            )
        
        # Volume-to-price correlations
        if volume_series is not None:
            results['volume_correlations'] = self._compute_volume_correlations(
                stock_prices,
                volume_series
            )
        
        # News event impact analysis
        if news_events is not None:
            results['news_impact'] = self._compute_news_impact(
                stock_prices,
                news_events
            )
        
        return results
    
    def _compute_price_correlations(
        self,
        stock_prices: pd.Series,
        market_prices: pd.Series,
        sector_prices: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """Compute price-to-price correlations"""
        
        # Align series
        df = pd.DataFrame({
            'stock': stock_prices,
            'market': market_prices
        }).dropna()
        
        if len(df) < 30:
            logger.warning(f"Insufficient data for correlation: {len(df)} < 30")
            return {'error': 'Insufficient data'}
        
        # Calculate returns
        df['stock_returns'] = df['stock'].pct_change()
        df['market_returns'] = df['market'].pct_change()
        df = df.dropna()
        
        # Pearson correlation (linear relationship)
        pearson_corr, pearson_pval = pearsonr(df['stock_returns'], df['market_returns'])
        
        # Spearman correlation (monotonic relationship, robust to outliers)
        spearman_corr, spearman_pval = spearmanr(df['stock_returns'], df['market_returns'])
        
        # Beta calculation (market sensitivity)
        covariance = np.cov(df['stock_returns'], df['market_returns'])[0, 1]
        market_variance = np.var(df['market_returns'])
        beta = covariance / market_variance if market_variance > 0 else 1.0
        
        # Rolling correlation (30-day window)
        rolling_corr = df['stock_returns'].rolling(window=30).corr(df['market_returns'])
        latest_30d_corr = rolling_corr.iloc[-1] if not rolling_corr.empty else pearson_corr
        
        results = {
            'market_correlation': {
                'pearson': float(pearson_corr),
                'spearman': float(spearman_corr),
                'pearson_pvalue': float(pearson_pval),
                'significant': self._safe_num(pearson_pval, 1.0) < 0.05,
                'rolling_30d': float(latest_30d_corr) if not pd.isna(latest_30d_corr) else None,
                'beta': float(beta),
                'interpretation': self._interpret_correlation(pearson_corr)
            }
        }
        
        # Sector correlation if provided
        if sector_prices is not None:
            df_sector = pd.DataFrame({
                'stock': stock_prices,
                'sector': sector_prices
            }).dropna()
            
            df_sector['stock_returns'] = df_sector['stock'].pct_change()
            df_sector['sector_returns'] = df_sector['sector'].pct_change()
            df_sector = df_sector.dropna()
            
            if len(df_sector) >= 30:
                sector_corr, sector_pval = pearsonr(df_sector['stock_returns'], df_sector['sector_returns'])
                results['sector_correlation'] = {
                    'pearson': float(sector_corr),
                    'pvalue': float(sector_pval),
                    'significant': self._safe_num(sector_pval, 1.0) < 0.05
                }
        
        return results
    
    def _compute_sentiment_correlations(
        self,
        stock_prices: pd.Series,
        sentiment_series: pd.Series
    ) -> Dict[str, Any]:
        """Compute sentiment-to-price correlations with time lags"""
        
        # Align series
        df = pd.DataFrame({
            'price': stock_prices,
            'sentiment': sentiment_series
        }).dropna()
        
        if len(df) < 30:
            return {'error': 'Insufficient data'}
        
        # Calculate price returns
        df['returns'] = df['price'].pct_change()
        df = df.dropna()
        
        # Test different lags (0, 1, 3, 7 days)
        lag_results = {}
        
        for lag in [0, 1, 3, 7]:
            if len(df) > lag + 10:
                sentiment_lagged = df['sentiment'].shift(lag)
                returns_future = df['returns']
                
                # Align
                aligned = pd.DataFrame({
                    'sentiment': sentiment_lagged,
                    'returns': returns_future
                }).dropna()
                
                if len(aligned) >= 20:
                    corr, pval = pearsonr(aligned['sentiment'], aligned['returns'])
                    lag_results[f'lag_{lag}d'] = {
                        'correlation': float(corr),
                        'pvalue': float(pval),
                        'significant': self._safe_num(pval, 1.0) < 0.05
                    }
        
        # Find optimal lag
        significant_lags = [
            (lag, data['correlation'])
            for lag, data in lag_results.items()
            if data['significant']
        ]
        
        optimal_lag = None
        optimal_corr = 0
        if significant_lags:
            optimal_lag, optimal_corr = max(significant_lags, key=lambda x: abs(x[1]))
        
        return {
            'lag_analysis': lag_results,
            'optimal_lag': optimal_lag,
            'optimal_correlation': optimal_corr,
            'interpretation': f"Sentiment leads price by {optimal_lag.split('_')[1]} with {abs(optimal_corr):.2f} correlation" if optimal_lag else "No significant sentiment-price relationship"
        }
    
    def _compute_volume_correlations(
        self,
        stock_prices: pd.Series,
        volume_series: pd.Series
    ) -> Dict[str, Any]:
        """Compute volume-to-price correlations"""
        
        df = pd.DataFrame({
            'price': stock_prices,
            'volume': volume_series
        }).dropna()
        
        if len(df) < 30:
            return {'error': 'Insufficient data'}
        
        # Calculate metrics
        df['returns'] = df['price'].pct_change()
        df['volume_change'] = df['volume'].pct_change()
        df = df.dropna()
        
        # Price-volume correlation
        pv_corr, pv_pval = pearsonr(df['returns'].abs(), df['volume'])
        
        # Volume precedes price? (lag analysis)
        volume_leads_price = False
        if len(df) > 5:
            vol_lagged = df['volume'].shift(1)
            aligned = pd.DataFrame({
                'vol_lag1': vol_lagged,
                'returns': df['returns'].abs()
            }).dropna()
            
            if len(aligned) >= 20:
                lag_corr, lag_pval = pearsonr(aligned['vol_lag1'], aligned['returns'])
                volume_leads_price = self._safe_num(lag_pval, 1.0) < 0.05 and abs(self._safe_num(lag_corr)) > 0.3
        
        return {
            'price_volume_correlation': float(pv_corr),
            'pvalue': float(pv_pval),
            'significant': self._safe_num(pv_pval, 1.0) < 0.05,
            'volume_leads_price': volume_leads_price,
            'interpretation': 'High volume correlates with large price moves' if abs(self._safe_num(pv_corr)) > 0.5 else 'Volume and price moves are independent'
        }
    
    def _compute_news_impact(
        self,
        stock_prices: pd.Series,
        news_events: pd.DataFrame
    ) -> Dict[str, Any]:
        """Analyze news event impact on price"""
        
        # news_events should have columns: date, sentiment, headline
        if 'date' not in news_events.columns:
            return {'error': 'News events must have date column'}
        
        # Convert to datetime
        news_events['date'] = pd.to_datetime(news_events['date'])
        
        impacts = []
        
        for _, event in news_events.iterrows():
            event_date = event['date']
            
            # Get price 1 day before and 1 day after
            try:
                price_before = stock_prices[stock_prices.index < event_date].iloc[-1]
                price_after = stock_prices[stock_prices.index > event_date].iloc[0]
                
                impact_pct = ((price_after - price_before) / price_before) * 100
                
                impacts.append({
                    'date': event_date.strftime('%Y-%m-%d'),
                    'headline': event.get('headline', '')[:50],
                    'sentiment': event.get('sentiment', 0),
                    'price_impact_pct': float(impact_pct)
                })
            except:
                continue
        
        if not impacts:
            return {'error': 'Could not compute news impact'}
        
        # Summary stats
        avg_abs_impact = np.mean([abs(i['price_impact_pct']) for i in impacts])
        avg_positive_impact = np.mean([i['price_impact_pct'] for i in impacts if i['price_impact_pct'] > 0] or [0])
        avg_negative_impact = np.mean([i['price_impact_pct'] for i in impacts if i['price_impact_pct'] < 0] or [0])
        
        return {
            'event_count': len(impacts),
            'average_absolute_impact_pct': float(avg_abs_impact),
            'average_positive_impact_pct': float(avg_positive_impact),
            'average_negative_impact_pct': float(avg_negative_impact),
            'recent_events': impacts[-5:],  # Last 5 events
            'interpretation': f"News events move price by average {avg_abs_impact:.2f}%"
        }
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(corr)
        
        if abs_corr > 0.8:
            strength = "very strong"
        elif abs_corr > 0.6:
            strength = "strong"
        elif abs_corr > 0.4:
            strength = "moderate"
        elif abs_corr > 0.2:
            strength = "weak"
        else:
            strength = "very weak"
        
        direction = "positive" if corr > 0 else "negative"
        
        return f"{strength} {direction} correlation"


def compute_correlations(
    stock_prices: pd.Series,
    market_prices: pd.Series,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to compute all correlations
    
    Args:
        stock_prices: Stock price series
        market_prices: Market index prices
        **kwargs: Optional sentiment_series, volume_series, sector_prices, news_events
        
    Returns:
        Correlation analysis results
    """
    engine = CorrelationEngine()
    return engine.compute_all_correlations(
        stock_prices,
        market_prices,
        sector_prices=kwargs.get('sector_prices'),
        sentiment_series=kwargs.get('sentiment_series'),
        volume_series=kwargs.get('volume_series'),
        news_events=kwargs.get('news_events')
    )
