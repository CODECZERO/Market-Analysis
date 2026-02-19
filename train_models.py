#!/usr/bin/env python3
"""
Continuous ML Training & Improvement System
Trains LSTM and XGBoost models on historical data and improves from real-time feedback
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import json
from typing import Dict, List, Any, Tuple
import yfinance as yf

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker', 'src'))

from ml.lstm_model_optimized import train_lstm_model, predict_prices
from ml.xgboost_model import train_xgboost_model, predict_signal
from technical_indicators import calculate_all_indicators


class ContinuousLearningPipeline:
    """
    Automated ML training pipeline that:
    1. Trains on historical data
    2. Validates predictions vs actual outcomes
    3. Continuously improves models
    4. Uses unsupervised learning for pattern discovery
    """
    
    def __init__(self, data_dir="./ml_training_data"):
        self.data_dir = data_dir
        self.models_dir = os.path.join(data_dir, "models")
        self.metrics_dir = os.path.join(data_dir, "metrics")
        self.predictions_dir = os.path.join(data_dir, "predictions")
        
        # Create directories
        for directory in [self.data_dir, self.models_dir, self.metrics_dir, self.predictions_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Training configuration
        self.nifty_50_stocks = [
            "TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS", "SBIN.NS", "BAJFINANCE.NS",
            "BHARTIARTL.NS", "ASIANPAINT.NS", "MARUTI.NS", "LT.NS", "AXISBANK.NS"
        ]
        
        self.performance_history = {}
    
    def fetch_training_data(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """Fetch historical data for training"""
        print(f"📊 Fetching {period} training data for {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if len(data) > 100:
                print(f"   ✅ Downloaded {len(data)} data points")
                return data
            else:
                print(f"   ⚠️  Insufficient data")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def prepare_training_dataset(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and targets for training
        Uses technical indicators + unsupervised patterns
        """
        # Calculate technical indicators
        indicators = calculate_all_indicators(data)
        
        # Create feature matrix
        features = []
        targets = []
        
        for i in range(60, len(data)):  # Use 60-day lookback
            # Price sequences (normalized)
            price_seq = data['Close'].iloc[i-60:i].values
            price_seq_norm = (price_seq - price_seq.mean()) / price_seq.std()
            
            # Volume sequences (normalized)
            volume_seq = data['Volume'].iloc[i-60:i].values
            volume_seq_norm = (volume_seq - volume_seq.mean()) / volume_seq.std()
            
            # Technical indicators at time i
            tech_features = [
                indicators.get('rsi', 50),
                indicators.get('macd', 0),
                indicators.get('sma_20', data['Close'].iloc[i]),
                indicators.get('sma_50', data['Close'].iloc[i]),
                indicators.get('sma_200', data['Close'].iloc[i]),
            ]
            
            # Combine features
            combined_features = np.concatenate([
                price_seq_norm,
                volume_seq_norm,
                tech_features
            ])
            
            features.append(combined_features)
            
            # Target: Next day return (in %)
            target = (data['Close'].iloc[i] / data['Close'].iloc[i-1] - 1) * 100
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def train_models_on_stock(self, symbol: str, retrain: bool = True):
        """
        Train both LSTM and XGBoost models for a stock
        """
        print(f"\n🧠 Training models for {symbol}...")
        
        # Fetch data
        data = self.fetch_training_data(symbol, period="2y")
        if data is None or len(data) < 200:
            print(f"   ❌ Skipping {symbol} - insufficient data")
            return None
        
        # Prepare dataset
        X, y = self.prepare_training_dataset(data)
        
        # Split into train/validation
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        print(f"   Train samples: {len(X_train)}, Val samples: {len(X_val)}")
        
        # Train LSTM
        print("   🔄 Training LSTM...")
        lstm_model = train_lstm_model(X_train.reshape(X_train.shape[0], X_train.shape[1], 1), y_train)
        
        # Validate LSTM
        lstm_predictions = lstm_model.predict(X_val.reshape(X_val.shape[0], X_val.shape[1], 1))
        lstm_mae = np.mean(np.abs(lstm_predictions.flatten() - y_val))
        print(f"   ✅ LSTM MAE: {lstm_mae:.4f}%")
        
        # Train XGBoost
        print("   🔄 Training XGBoost...")
        xgb_model = train_xgboost_model(X_train, y_train)
        
        # Validate XGBoost
        xgb_predictions = xgb_model.predict(X_val)
        xgb_mae = np.mean(np.abs(xgb_predictions - y_val))
        print(f"   ✅ XGBoost MAE: {xgb_mae:.4f}%")
        
        # Save models
        model_path = os.path.join(self.models_dir, f"{symbol.replace('.', '_')}")
        os.makedirs(model_path, exist_ok=True)
        
        lstm_model.save(os.path.join(model_path, "lstm_model.h5"))
        with open(os.path.join(model_path, "xgb_model.pkl"), 'wb') as f:
            pickle.dump(xgb_model, f)
        
        # Save metrics
        metrics = {
            "symbol": symbol,
            "trained_at": datetime.now().isoformat(),
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "lstm_mae": float(lstm_mae),
            "xgb_mae": float(xgb_mae)
        }
        
        with open(os.path.join(model_path, "metrics.json"), 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"   💾 Models saved to {model_path}")
        
        return metrics
    
    def train_all_stocks(self, stocks_subset: List[str] = None):
        """Train models for all NIFTY 50 stocks (or subset)"""
        stocks = stocks_subset or self.nifty_50_stocks
        
        print(f"\n{'='*70}")
        print(f"🚀 STARTING BATCH TRAINING - {len(stocks)} STOCKS")
        print(f"{'='*70}\n")
        
        results = []
        for i, symbol in enumerate(stocks, 1):
            print(f"[{i}/{len(stocks)}] Processing {symbol}...")
            metrics = self.train_models_on_stock(symbol)
            if metrics:
                results.append(metrics)
        
        # Save summary
        summary = {
            "training_session": datetime.now().isoformat(),
            "total_stocks": len(stocks),
            "successful": len(results),
            "failed": len(stocks) - len(results),
            "results": results
        }
        
        summary_path = os.path.join(self.metrics_dir, f"training_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ TRAINING COMPLETE")
        print(f"{'='*70}")
        print(f"Successful: {len(results)}/{len(stocks)}")
        print(f"Summary saved: {summary_path}")
        
        return summary
    
    def evaluate_prediction_accuracy(self, symbol: str, days_back: int = 30):
        """
        Evaluate how accurate past predictions were
        Compares predicted vs actual prices
        """
        print(f"\n📈 Evaluating prediction accuracy for {symbol}...")
        
        # Load prediction history
        pred_file = os.path.join(self.predictions_dir, f"{symbol.replace('.', '_')}_predictions.json")
        if not os.path.exists(pred_file):
            print("   ⚠️  No prediction history found")
            return None
        
        with open(pred_file, 'r') as f:
            predictions = json.load(f)
        
        # Fetch actual prices
        data = self.fetch_training_data(symbol, period="3mo")
        if data is None:
            return None
        
        # Compare predictions vs actuals
        accuracies = []
        for pred in predictions[-days_back:]:
            pred_date = datetime.fromisoformat(pred['date'])
            pred_price = pred['predicted_price']
            
            # Find actual price on that date (or closest)
            try:
                actual_price = data.loc[pred_date, 'Close']
                error = abs(pred_price - actual_price) / actual_price * 100
                accuracies.append({
                    'date': pred_date.isoformat(),
                    'predicted': pred_price,
                    'actual': actual_price,
                    'error_pct': error
                })
            except:
                continue
        
        if accuracies:
            avg_error = np.mean([a['error_pct'] for a in accuracies])
            print(f"   📊 Average prediction error: {avg_error:.2f}%")
            print(f"   📊 Predictions evaluated: {len(accuracies)}")
            
            return {
                'symbol': symbol,
                'avg_error_pct': avg_error,
                'predictions_evaluated': len(accuracies),
                'details': accuracies
            }
        
        return None


def main():
    """Main training pipeline"""
    print("🧠 ML MODEL TRAINING & IMPROVEMENT PIPELINE")
    print("=" * 70)
    
    pipeline = ContinuousLearningPipeline()
    
    # Train on a subset first (for testing)
    test_stocks = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ITC.NS"]
    
    print("\n🎯 Phase 1: Initial Training")
    print("Training on subset:", test_stocks)
    
    summary = pipeline.train_all_stocks(test_stocks)
    
    print("\n🎯 Phase 2: Prediction Accuracy Evaluation")
    for symbol in test_stocks[:2]:  # Evaluate first 2
        pipeline.evaluate_prediction_accuracy(symbol)
    
    print("\n" + "=" * 70)
    print("✅ TRAINING PIPELINE COMPLETE!")
    print(f"Models saved in: {pipeline.models_dir}")
    print(f"Metrics saved in: {pipeline.metrics_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
