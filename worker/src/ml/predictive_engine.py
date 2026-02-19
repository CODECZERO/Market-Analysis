"""
Predictive Stock Price Forecasting Engine
Uses pattern recognition and historical analysis to predict future price movements

Features:
- 1-day, 3-day, 7-day forecasts
- Pattern matching (Cup & Handle, Head & Shoulders, etc.)
- Anomaly detection
- Confidence scoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class PredictiveEngine:
    """
    Stock price prediction engine
    
    Methods:
    1. Pattern Recognition - Find historical similar patterns
    2. Trend Analysis - Identify current trend direction
    3. Anomaly Detection - Spot unusual price movements
    4. Confidence Scoring - Calculate prediction reliability
    """
    
    def __init__(self):
        """Initialize predictive engine"""
        self.patterns_db = defaultdict(list)  # Store historical patterns
        self.prediction_history = []  # Track accuracy
        
    def predict(self, symbol: str, price_data: pd.DataFrame, 
                forecast_days: List[int] = [1, 3, 7]) -> Dict:
        """
        Predict future stock prices
        
        Args:
            symbol: Stock symbol
            price_data: Historical OHLCV data
            forecast_days: Days to forecast (e.g., [1, 3, 7])
        
        Returns:
            Dict with predictions and metadata
        """
        if len(price_data) < 30:
            return {'error': 'Insufficient data (need 30+ days)'}
        
        current_price = price_data['Close'].iloc[-1]
        
        # 1. Detect current pattern
        pattern = self._detect_pattern(price_data)
        
        # 2. Find similar historical patterns
        similar_patterns = self._find_similar_patterns(price_data, limit=20)
        
        # 3. Calculate predictions
        predictions = {}
        for days in forecast_days:
            predicted_price, confidence = self._predict_n_days(
                price_data, similar_patterns, days
            )
            
            direction = 'UP' if predicted_price > current_price else 'DOWN'
            change_pct = ((predicted_price - current_price) / current_price) * 100
            
            predictions[f'{days}_day'] = {
                'price': round(predicted_price, 2),
                'confidence': round(confidence, 2),
                'direction': direction,
                'change_percent': round(change_pct, 2),
            }
        
        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'predictions': predictions,
            'pattern_detected': pattern,
            'similar_past_moves': len(similar_patterns),
            'timestamp': datetime.now().isoformat(),
        }
    
    def _detect_pattern(self, data: pd.DataFrame) -> str:
        """
        Detect chart patterns
        
        Patterns:
        - Bullish: Cup & Handle, Ascending Triangle, Golden Cross
        - Bearish: Head & Shoulders, Descending Triangle, Death Cross
        - Neutral: Consolidation, Range-bound
        """
        prices = data['Close'].values
        
        if len(prices) < 50:
            return 'Insufficient data'
        
        # Calculate moving averages
        sma_20 = pd.Series(prices).rolling(20).mean().values
        sma_50 = pd.Series(prices).rolling(50).mean().values
        
        # Golden Cross (bullish)
        if len(sma_20) > 2 and len(sma_50) > 2:
            if sma_20[-1] > sma_50[-1] and sma_20[-2] <= sma_50[-2]:
                return 'Golden Cross (Bullish)'
        
        # Death Cross (bearish)
        if len(sma_20) > 2 and len(sma_50) > 2:
            if sma_20[-1] < sma_50[-1] and sma_20[-2] >= sma_50[-2]:
                return 'Death Cross (Bearish)'
        
        # Cup and Handle (simplified)
        recent_20 = prices[-20:]
        if self._is_cup_and_handle(recent_20):
            return 'Cup and Handle (Bullish)'
        
        # Head and Shoulders (simplified)
        if self._is_head_and_shoulders(prices[-30:]):
            return 'Head and Shoulders (Bearish)'
        
        # Trending vs Range-bound
        returns = np.diff(prices[-20:]) / prices[-20:-1]
        volatility = np.std(returns)
        
        if abs(np.mean(returns)) > volatility:
            if np.mean(returns) > 0:
                return 'Strong Uptrend'
            else:
                return 'Strong Downtrend'
        else:
            return 'Consolidation (Range-bound)'
    
    def _is_cup_and_handle(self, prices: np.ndarray) -> bool:
        """Detect cup and handle pattern"""
        if len(prices) < 15:
            return False
        
        # Cup: U-shape (drop then recovery)
        mid = len(prices) // 2
        left_half = prices[:mid]
        right_half = prices[mid:]
        
        # Check if middle is lower than sides
        if min(prices) in prices[mid-2:mid+2]:  # Bottom in middle
            # Check if recovered
            if prices[-1] > prices[0] * 0.95:
                return True
        
        return False
    
    def _is_head_and_shoulders(self, prices: np.ndarray) -> bool:
        """Detect head and shoulders pattern"""
        if len(prices) < 20:
            return False
        
        # Find local maxima
        peaks = []
        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                peaks.append((i, prices[i]))
        
        if len(peaks) >= 3:
            # Check if middle peak is highest (head)
            sorted_peaks = sorted(peaks, key=lambda x: x[1], reverse=True)
            head = sorted_peaks[0]
            
            # Check if head is in middle
            if len(prices) * 0.3 < head[0] < len(prices) * 0.7:
                return True
        
        return False
    
    def _find_similar_patterns(self, data: pd.DataFrame, 
                              window: int = 20, limit: int = 20) -> List[Dict]:
        """
        Find similar historical patterns
        
        Uses correlation to find past price movements similar to current
        """
        prices = data['Close'].values
        
        if len(prices) < window * 2:
            return []
        
        # Current pattern (last N days)
        current_pattern = prices[-window:]
        current_normalized = (current_pattern - current_pattern.mean()) / current_pattern.std()
        
        # Search historical data
        similar = []
        
        for i in range(window, len(prices) - 7):  # Leave room for future
            historical_pattern = prices[i-window:i]
            historical_normalized = (historical_pattern - historical_pattern.mean()) / historical_pattern.std()
            
            # Calculate correlation
            correlation = np.corrcoef(current_normalized, historical_normalized)[0, 1]
            
            if correlation > 0.7:  # High similarity
                # Get what happened next
                future_1d = prices[i] if i < len(prices) else None
                future_3d = prices[i+2] if i+2 < len(prices) else None
                future_7d = prices[i+6] if i+6 < len(prices) else None
                
                similar.append({
                    'correlation': correlation,
                    'start_idx': i - window,
                    'pattern_price': prices[i-1],
                    'future_1d': future_1d,
                    'future_3d': future_3d,
                    'future_7d': future_7d,
                })
        
        # Sort by correlation
        similar.sort(key=lambda x: x['correlation'], reverse=True)
        
        return similar[:limit]
    
    def _predict_n_days(self, data: pd.DataFrame, 
                       similar_patterns: List[Dict], days: int) -> Tuple[float, float]:
        """
        Predict price N days ahead
        
        Returns:
            (predicted_price, confidence)
        """
        current_price = data['Close'].iloc[-1]
        
        if not similar_patterns:
            # No patterns found, use trend
            returns = data['Close'].pct_change()
            avg_return = returns.mean()
            predicted = current_price * (1 + avg_return * days)
            return (predicted, 0.3)  # Low confidence
        
        # Get future prices from similar patterns
        future_key = f'future_{days}d'
        if days == 3:
            future_prices = [p.get('future_3d') for p in similar_patterns if p.get('future_3d')]
        elif days == 7:
            future_prices = [p.get('future_7d') for p in similar_patterns if p.get('future_7d')]
        else:  # 1 day
            future_prices = [p.get('future_1d') for p in similar_patterns if p.get('future_1d')]
        
        if not future_prices:
            # Fallback
            avg_return = data['Close'].pct_change().mean()
            predicted = current_price * (1 + avg_return * days)
            return (predicted, 0.3)
        
        # Calculate weighted average (weight by correlation)
        weights = [p['correlation'] for p in similar_patterns[:len(future_prices)]]
        weighted_avg_future = np.average(future_prices, weights=weights)
        
        # Calculate change from pattern price to future
        pattern_prices = [p['pattern_price'] for p in similar_patterns[:len(future_prices)]]
        avg_pattern_price = np.mean(pattern_prices)
        
        # Apply same change to current price
        change_ratio = weighted_avg_future / avg_pattern_price
        predicted_price = current_price * change_ratio
        
        # Confidence based on:
        # 1. Number of similar patterns found
        # 2. Agreement among patterns
        std_dev = np.std(future_prices)
        agreement = 1.0 - (std_dev / np.mean(future_prices)) if np.mean(future_prices) > 0 else 0.5
        
        pattern_count_score = min(len(similar_patterns) / 20.0, 1.0)
        
        confidence = (agreement * 0.6) + (pattern_count_score * 0.4)
        confidence = min(max(confidence, 0.1), 0.95)  # Clamp to 10-95%
        
        return (predicted_price, confidence)
    
    def detect_anomaly(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        Detect unusual price movements
        
        Returns:
            Dict with anomaly info or None
        """
        if len(data) < 30:
            return None
        
        prices = data['Close'].values
        volumes = data['Volume'].values if 'Volume' in data.columns else None
        
        # Calculate statistics
        returns = np.diff(prices) / prices[:-1]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Check latest movement
        latest_return = returns[-1]
        z_score = (latest_return - avg_return) / std_return if std_return > 0 else 0
        
        # Anomaly if > 2 standard deviations
        if abs(z_score) > 2:
            return {
                'type': 'price_spike' if z_score > 0 else 'price_drop',
                'severity': 'high' if abs(z_score) > 3 else 'moderate',
                'z_score': round(z_score, 2),
                'change_percent': round(latest_return * 100, 2),
                'description': f"Unusual {'surge' if z_score > 0 else 'drop'} detected ({abs(z_score):.1f}σ)",
            }
        
        # Check volume anomaly
        if volumes is not None and len(volumes) > 30:
            avg_volume = np.mean(volumes[:-1])
            latest_volume = volumes[-1]
            volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 3:
                return {
                    'type': 'volume_surge',
                    'severity': 'high' if volume_ratio > 5 else 'moderate',
                    'volume_ratio': round(volume_ratio, 2),
                    'description': f"Unusual trading volume ({volume_ratio:.1f}x normal)",
                }
        
        return None


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("PREDICTIVE ENGINE DEMO")
    print("=" * 60)
    
    # Generate sample price data
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    
    # Simulate bullish trend with noise
    trend = np.linspace(3700, 3850, 100)
    noise = np.random.normal(0, 30, 100)
    prices = trend + noise
    
    data = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, 100),
    })
    data.set_index('Date', inplace=True)
    
    # Create engine
    engine = PredictiveEngine()
    
    # Make predictions
    result = engine.predict('TCS.NS', data, forecast_days=[1, 3, 7])
    
    print(f"\n📊 Predictions for {result['symbol']}")
    print(f"Current Price: ₹{result['current_price']}")
    print(f"Pattern: {result['pattern_detected']}")
    print(f"Similar Patterns Found: {result['similar_past_moves']}")
    
    print(f"\n🔮 Price Forecasts:")
    for period, pred in result['predictions'].items():
        print(f"\n  {period.replace('_', ' ').title()}:")
        print(f"    Price: ₹{pred['price']} ({pred['direction']} {abs(pred['change_percent']):.1f}%)")
        print(f"    Confidence: {pred['confidence']:.0%}")
    
    # Anomaly detection
    anomaly = engine.detect_anomaly(data)
    if anomaly:
        print(f"\n⚠️  Anomaly Detected:")
        print(f"    {anomaly['description']}")
    else:
        print(f"\n✅ No anomalies detected")
    
    print("\n" + "=" * 60)
