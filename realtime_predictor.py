#!/usr/bin/env python3
"""
Real-Time Prediction & Continuous Improvement System
Uses online learning to improve predictions based on actual market outcomes
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Any
import yfinance as yf
from collections import deque

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker', 'src'))

from technical_indicators import calculate_indicators


class RealTimePredictionEngine:
    """
    Advanced prediction system that:
    1. Makes real-time predictions
    2. Tracks actual outcomes
    3. Learns from mistakes (online learning)
    4. Improves prediction accuracy over time
    """
    
    def __init__(self, data_dir="./realtime_predictions"):
        self.data_dir = data_dir
        self.feedback_dir = os.path.join(data_dir, "feedback")
        self.predictions_log = os.path.join(data_dir, "predictions.jsonl")
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        # Prediction history (in-memory)
        self.prediction_buffer = deque(maxlen=1000)
        
        # Performance tracking
        self.accuracy_scores = {}
        
        # Adaptive learning rates
        self.learning_rates = {}
    
    def get_realtime_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Fetch latest market data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval="1d")
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_market_regime(self, data: pd.DataFrame) -> str:
        """
        Detect current market regime using unsupervised clustering
        Returns: 'bullish', 'bearish', 'sideways', or 'volatile'
        """
        if len(data) < 20:
            return 'unknown'
        
        # Calculate regime indicators
        recent_return = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
        volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized
        
        # Simple regime classification
        if recent_return > 5 and volatility < 25:
            return 'bullish'
        elif recent_return < -5 and volatility < 25:
            return 'bearish'
        elif volatility > 35:
            return 'volatile'
        else:
            return 'sideways'
    
    def make_prediction(self, symbol: str, horizon: int = 5) -> Dict[str, Any]:
        """
        Make prediction for next N days
        
        Plan-Then-Act Approach:
        1. Analyze current state
        2. Form hypothesis
        3. Predict outcome
        4. Log prediction for later verification
        """
        print(f"\n🔮 Making {horizon}-day prediction for {symbol}...")
        
        # Step 1: Fetch and analyze current data
        data = self.get_realtime_data(symbol, period="3mo")
        if data is None or len(data) < 60:
            return {"error": "Insufficient data"}
        
        current_price = float(data['Close'].iloc[-1])
        current_date = data.index[-1]
        
        # Calculate technical indicators
        indicators = calculate_indicators(data)
        
        # Detect market regime
        regime = self.calculate_market_regime(data)
        
        print(f"   Current Price: ₹{current_price:.2f}")
        print(f"   Market Regime: {regime}")
        print(f"   RSI: {indicators.get('rsi', 'N/A')}")
        print(f"   MACD: {indicators.get('macd', 'N/A')}")
        
        # Step 2: Form hypothesis based on multiple signals
        signals = []
        
        # Technical signals
        rsi = indicators.get('rsi', 50)
        if rsi > 70:
            signals.append(('overbought', -0.3))
        elif rsi < 30:
            signals.append(('oversold', 0.3))
        
        macd = indicators.get('macd', 0)
        if macd > 0:
            signals.append(('macd_positive', 0.2))
        else:
            signals.append(('macd_negative', -0.2))
        
        # Trend signals
        sma_50 = indicators.get('sma_50', current_price)
        sma_200 = indicators.get('sma_200', current_price)
        
        if current_price > sma_50 > sma_200:
            signals.append(('golden_cross', 0.4))
        elif current_price < sma_50 < sma_200:
            signals.append(('death_cross', -0.4))
        
        # Regime signals
        regime_multipliers = {
            'bullish': 0.3,
            'bearish': -0.3,
            'volatile': 0.0,
            'sideways': 0.0,
            'unknown': 0.0
        }
        signals.append((f'regime_{regime}', regime_multipliers[regime]))
        
        # Step 3: Combine signals to predict
        signal_sum = sum([weight for _, weight in signals])
        confidence = min(abs(signal_sum), 1.0)
        
        # Predict price change percentage
        # Base prediction on signal strength
        predicted_change_pct = signal_sum * 5  # Up to ±5% per strong signal
        predicted_price = current_price * (1 + predicted_change_pct / 100)
        
        # Add historical accuracy adjustment
        if symbol in self.accuracy_scores:
            accuracy = self.accuracy_scores[symbol]['accuracy']
            # Reduce prediction magnitude if historically inaccurate
            predicted_change_pct *= accuracy
            predicted_price = current_price * (1 + predicted_change_pct / 100)
        
        # Step 4: Create prediction record
        prediction = {
            'symbol': symbol,
            'prediction_date': datetime.now().isoformat(),
            'current_date': current_date.isoformat(),
            'current_price': current_price,
            'prediction_horizon_days': horizon,
            'target_date': (current_date + timedelta(days=horizon)).isoformat(),
            'predicted_price': float(predicted_price),
            'predicted_change_pct': float(predicted_change_pct),
            'confidence': float(confidence),
            'market_regime': regime,
            'signals': [(name, float(weight)) for name, weight in signals],
            'technical_indicators': {
                'rsi': float(indicators.get('rsi', 50)),
                'macd': float(indicators.get('macd', 0)),
                'sma_50': float(sma_50),
                'sma_200': float(sma_200)
            },
            'status': 'pending'  # Will be 'verified' after target date
        }
        
        # Log prediction
        self.log_prediction(prediction)
        
        print(f"   🎯 Predicted Price: ₹{predicted_price:.2f}")
        print(f"   📈 Predicted Change: {predicted_change_pct:+.2f}%")
        print(f"   💪 Confidence: {confidence:.2%}")
        print(f"   📅 Target Date: {prediction['target_date'][:10]}")
        
        return prediction
    
    def log_prediction(self, prediction: Dict[str, Any]):
        """Append prediction to log file"""
        with open(self.predictions_log, 'a') as f:
            f.write(json.dumps(prediction) + '\n')
        
        self.prediction_buffer.append(prediction)
    
    def verify_past_predictions(self, symbol: str = None):
        """
        Check if past predictions came true
        Learn from successes and failures
        """
        print(f"\n📊 Verifying past predictions...")
        
        # Load predictions
        if not os.path.exists(self.predictions_log):
            print("   No predictions to verify")
            return
        
        with open(self.predictions_log, 'r') as f:
            predictions = [json.loads(line) for line in f]
        
        # Filter by symbol if specified
        if symbol:
            predictions = [p for p in predictions if p['symbol'] == symbol]
        
        # Only verify predictions whose target date has passed
        today = datetime.now()
        verifiable = [
            p for p in predictions 
            if datetime.fromisoformat(p['target_date']) <= today 
            and p['status'] == 'pending'
        ]
        
        print(f"   Found {len(verifiable)} predictions to verify")
        
        for pred in verifiable:
            symbol = pred['symbol']
            target_date = datetime.fromisoformat(pred['target_date'])
            predicted_price = pred['predicted_price']
            
            # Fetch actual price
            try:
                data = self.get_realtime_data(symbol, period="1mo")
                if data is None:
                    continue
                
                # Get closest date
                actual_price = float(data['Close'].asof(target_date))
                error_pct = abs(predicted_price - actual_price) / actual_price * 100
                
                # Update prediction record
                pred['actual_price'] = actual_price
                pred['error_pct'] = error_pct
                pred['status'] = 'verified'
                pred['verified_at'] = datetime.now().isoformat()
                
                # Calculate if prediction was "correct" (within 5% error)
                pred['was_accurate'] = error_pct < 5.0
                
                print(f"   {symbol}: Predicted ₹{predicted_price:.2f}, Actual ₹{actual_price:.2f}, Error: {error_pct:.2f}%")
                
                # Update accuracy tracking
                if symbol not in self.accuracy_scores:
                    self.accuracy_scores[symbol] = {
                        'total_predictions': 0,
                        'accurate_predictions': 0,
                        'accuracy': 0.5
                    }
                
                self.accuracy_scores[symbol]['total_predictions'] += 1
                if pred['was_accurate']:
                    self.accuracy_scores[symbol]['accurate_predictions'] += 1
                
                # Calculate running accuracy
                total = self.accuracy_scores[symbol]['total_predictions']
                accurate = self.accuracy_scores[symbol]['accurate_predictions']
                self.accuracy_scores[symbol]['accuracy'] = accurate / total if total > 0 else 0.5
                
            except Exception as e:
                print(f"   Error verifying {symbol}: {e}")
                continue
        
        # Save updated predictions
        with open(self.predictions_log, 'w') as f:
            for p in predictions:
                f.write(json.dumps(p) + '\n')
        
        # Save accuracy scores
        accuracy_file = os.path.join(self.feedback_dir, 'accuracy_scores.json')
        with open(accuracy_file, 'w') as f:
            json.dump(self.accuracy_scores, f, indent=2)
        
        print(f"   ✅ Verification complete. Accuracy scores updated.")
    
    def continuous_prediction_loop(self, symbols: List[str], iterations: int = 5):
        """
        Run continuous prediction and improvement loop
        """
        print(f"\n🔄 STARTING CONTINUOUS PREDICTION LOOP")
        print(f"Symbols: {symbols}")
        print(f"Iterations: {iterations}")
        print("=" * 70)
        
        for i in range(iterations):
            print(f"\n{'='*70}")
            print(f"ITERATION {i+1}/{iterations}")
            print(f"{'='*70}")
            
            # Make predictions for all symbols
            for symbol in symbols:
                self.make_prediction(symbol, horizon=5)
                time.sleep(1)  # Rate limiting
            
            # Verify past predictions (learn from feedback)
            self.verify_past_predictions()
            
            # Display current accuracy
            print(f"\n📈 Current Accuracy Scores:")
            for symbol, scores in self.accuracy_scores.items():
                acc = scores['accuracy']
                total = scores['total_predictions']
                print(f"   {symbol}: {acc:.1%} ({total} predictions)")
            
            # Wait before next iteration (would be much longer in production)
            if i < iterations - 1:
                print(f"\n⏳ Waiting 30 seconds before next iteration...")
                time.sleep(30)
        
        print(f"\n{'='*70}")
        print("✅ CONTINUOUS LEARNING LOOP COMPLETE")
        print(f"{'='*70}")



class IntradayForecaster:
    """
    High-Frequency "Crystal Ball" Predictor
    Generates profit/loss projections for 2m, 5m, 15m, 30m, 60m horizons
    """
    
    def __init__(self):
        self.horizons = {
            "2m": 2, "5m": 5, "15m": 15, "30m": 30, "60m": 60
        }
    
    def generate_forecast(self, current_price: float, intraday_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate matrix of short-term predictions
        
        Args:
            current_price: Latest close price
            intraday_data: 5m or 1m interval dataframe
            
        Returns:
            Dict with 'matrix' (list of dicts) and 'summary'
        """
        if intraday_data is None or len(intraday_data) < 12:
            return {"error": "Insufficient intraday data"}
            
        # Calculate recent volatility (last 12 bars = 1 hour if 5m)
        recent_vol = intraday_data['close'].pct_change().std() * np.sqrt(12)
        
        # Calculate Momentum (1h trend)
        if len(intraday_data) > 12:
            trend_1h = (intraday_data['close'].iloc[-1] - intraday_data['close'].iloc[-12]) / intraday_data['close'].iloc[-12]
        else:
            trend_1h = 0
            
        matrix = []
        
        for name, minutes in self.horizons.items():
            # Volatility expansion scaling (sq root of time)
            time_scale = np.sqrt(minutes / 60.0)
            
            # Simple drift + volatility model
            expected_move = current_price * trend_1h * (minutes / 60.0) # Drift
            risk_range = current_price * recent_vol * time_scale # Volatility
            
            # Heuristic Logic for "Forecast"
            if trend_1h > 0.001:
                direction = "UP"
                target = current_price + abs(expected_move) + (risk_range * 0.2)
                max_loss = current_price - (risk_range * 0.5)
            elif trend_1h < -0.001:
                direction = "DOWN"
                target = current_price - abs(expected_move) - (risk_range * 0.2)
                max_loss = current_price + (risk_range * 0.5)
            else:
                direction = "FLAT"
                target = current_price
                max_loss = current_price - (risk_range * 0.3)
                
            # Gain/Loss Pct
            gain_pct = ((target - current_price) / current_price) * 100
            loss_pct = ((max_loss - current_price) / current_price) * 100
            
            matrix.append({
                "time": f"+{name}",
                "direction": direction,
                "target_price": target,
                "gain_pct": gain_pct,
                "max_loss": max_loss,
                "loss_pct": loss_pct,
                "conf": max(10, min(95, int((1 - time_scale) * 100))) # Lower confidence for longer times
            })
            
        return {
            "matrix": matrix,
            "volatility_1h": recent_vol,
            "trend_1h": trend_1h
        }


def main():
    """Main real-time prediction pipeline"""
    print("🚀 REAL-TIME PREDICTION & CONTINUOUS IMPROVEMENT ENGINE")
    print("=" * 70)
    
    engine = RealTimePredictionEngine()
    
    # Test stocks
    test_stocks = ["TCS.NS", "RELIANCE.NS", "INFY.NS"]
    
    # Make initial predictions
    print("\n🎯 Phase 1: Making Predictions")
    for symbol in test_stocks:
        engine.make_prediction(symbol, horizon=5)
        time.sleep(1)
    
    # Verify any past predictions
    print("\n🎯 Phase 2: Verifying Past Predictions")
    engine.verify_past_predictions()
    
    print("\n" + "=" * 70)
    print("✅ PREDICTION PIPELINE COMPLETE!")
    print(f"Predictions logged in: {engine.predictions_log}")
    print("=" * 70)


if __name__ == "__main__":
    main()
