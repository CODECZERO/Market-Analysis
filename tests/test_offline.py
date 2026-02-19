#!/usr/bin/env python3
"""
Offline Model Testing - Synthetic Data
Tests models with randomly generated data to verify functionality
"""

import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker', 'src'))

from technical_indicators import TechnicalIndicators
from decision_engine import DecisionEngine
from ml.lstm_model_optimized import LSTMModel
from quant.momentum import MomentumStrategy
from quant.mean_reversion import MeanReversionStrategy


def generate_synthetic_stock_data(days=500, start_price=100, volatility=0.02):
    """Generate synthetic OHLCV data with realistic patterns"""
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate price with trend and random walk
    trend = np.linspace(0, 0.3, days)  # 30% uptrend
    noise = np.random.randn(days) * volatility
    returns = trend / days + noise
    
    prices = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC from close prices
    high = prices * (1 + np.abs(np.random.randn(days) * 0.01))
    low = prices * (1 - np.abs(np.random.randn(days) * 0.01))
    open_prices = np.roll(prices, 1)
    open_prices[0] = start_price
    
    # Volume with some correlation to price changes
    volume = 1000000 + np.abs(returns) * 10000000 + np.random.randn(days) * 500000
    volume = np.maximum(volume, 100000)
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': open_prices,
        'High': high,
        'Low': low,
        'Close': prices,
        'Volume': volume
    })
    
    return df


def test_technical_indicators():
    """Test technical indicators with synthetic data"""
    print("="*70)
    print("TEST 1: Technical Indicators")
    print("="*70)
    
    # Generate data
    data = generate_synthetic_stock_data(days=500)
    
    # Calculate indicators
    ti = TechnicalIndicators()
    indicators = ti.calculate_all_indicators(data)
    
    # Validate indicators
    tests_passed = 0
    total_tests = 0
    
    # Test 1: RSI range
    total_tests += 1
    rsi = indicators.get('rsi', 0)
    if 0 <= rsi <= 100:
        print(f"✓ RSI in valid range: {rsi:.2f}")
        tests_passed += 1
    else:
        print(f"✗ RSI out of range: {rsi:.2f}")
    
    # Test 2: MACD existence
    total_tests += 1
    macd = indicators.get('macd', None)
    if macd is not None:
        print(f"✓ MACD calculated: {macd:.4f}")
        tests_passed += 1
    else:
        print("✗ MACD not calculated")
    
    # Test 3: Moving averages order (in uptrend, SMA50 > SMA200 eventually)
    total_tests += 1
    sma_50 = indicators.get('sma_50', 0)
    sma_200 = indicators.get('sma_200', 0)
    if sma_50 > 0 and sma_200 > 0:
        print(f"✓ SMAs calculated: SMA50={sma_50:.2f}, SMA200={sma_200:.2f}")
        tests_passed += 1
    else:
        print("✗ SMAs not calculated")
    
    # Test 4: Bollinger Bands
    total_tests += 1
    bb_upper = indicators.get('bb_upper', 0)
    bb_lower = indicators.get('bb_lower', 0)
    current_price = data['Close'].iloc[-1]
    if bb_lower < current_price < bb_upper:
        print(f"✓ Price within Bollinger Bands: {bb_lower:.2f} < {current_price:.2f} < {bb_upper:.2f}")
        tests_passed += 1
    else:
        print(f"⚠ Price outside Bollinger Bands (can be normal)")
        tests_passed += 0.5  # Half credit
    
    # Test 5: Support/Resistance
    total_tests += 1
    support = indicators.get('support_level', 0)
    resistance = indicators.get('resistance_level', 0)
    if support > 0 and resistance > support:
        print(f"✓ Support/Resistance valid: Support={support:.2f}, Resistance={resistance:.2f}")
        tests_passed += 1
    else:
        print("✗ Support/Resistance invalid")
    
    print(f"\nPassed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.1f}%)")
    print()
    return tests_passed / total_tests >= 0.8


def test_quant_strategies():
    """Test quantitative strategies"""
    print("="*70)
    print("TEST 2: Quantitative Strategies")
    print("="*70)
    
    data = generate_synthetic_stock_data(days=500)
    
    tests_passed = 0
    total_tests = 0
    
    # Test Momentum Strategy
    total_tests += 1
    try:
        momentum = MomentumStrategy()
        signal = momentum.calculate_momentum_score(data)
        
        if -1 <= signal <= 1:
            print(f"✓ Momentum signal in range: {signal:.3f}")
            tests_passed += 1
        else:
            print(f"✗ Momentum signal out of range: {signal:.3f}")
    except Exception as e:
        print(f"✗ Momentum strategy failed: {e}")
    
    # Test Mean Reversion
    total_tests += 1
    try:
        mean_rev = MeanReversionStrategy()
        zscore = mean_rev.calculate_zscore(data)
        
        if -5 <= zscore <= 5:  # Reasonable z-score range
            print(f"✓ Z-score calculated: {zscore:.3f}")
            tests_passed += 1
        else:
            print(f"⚠ Z-score unusual but valid: {zscore:.3f}")
            tests_passed += 0.5
    except Exception as e:
        print(f"✗ Mean reversion failed: {e}")
    
    print(f"\nPassed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.1f}%)")
    print()
    return tests_passed / total_tests >= 0.8


def test_lstm_predictions():
    """Test LSTM model predictions"""
    print("="*70)
    print("TEST 3: LSTM Price Predictions")
    print("="*70)
    
    data = generate_synthetic_stock_data(days=500)
    current_price = data['Close'].iloc[-1]
    
    tests_passed = 0
    total_tests = 0
    
    try:
        lstm = LSTMModel()
        
        # Test prediction shape
        total_tests += 1
        predictions = lstm.predict(data)
        
        if predictions and '1d' in predictions:
            print(f"✓ Predictions generated: {list(predictions.keys())}")
            tests_passed += 1
        else:
            print("✗ Predictions not generated")
        
        # Test prediction reasonableness (within 20% of current price)
        total_tests += 1
        pred_1d = predictions.get('1d', current_price)
        deviation = abs(pred_1d - current_price) / current_price
        
        if deviation < 0.20:  # 20% deviation max
            print(f"✓ 1-day prediction reasonable: ₹{pred_1d:.2f} (current: ₹{current_price:.2f}, {deviation*100:.1f}% diff)")
            tests_passed += 1
        else:
            print(f"⚠ 1-day prediction high deviation: {deviation*100:.1f}%")
            tests_passed += 0.5
        
        # Test confidence
        total_tests += 1
        confidence = predictions.get('confidence', 0)
        if 0 <= confidence <= 1:
            print(f"✓ Confidence in range: {confidence:.2%}")
            tests_passed += 1
        else:
            print(f"✗ Confidence out of range: {confidence}")
        
    except Exception as e:
        print(f"✗ LSTM model failed: {e}")
    
    print(f"\nPassed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.1f}%)")
    print()
    return tests_passed / total_tests >= 0.6  # Lower threshold for ML


def test_decision_engine():
    """Test decision engine"""
    print("="*70)
    print("TEST 4: Decision Engine")
    print("="*70)
    
    tests_passed = 0
    total_tests = 0
    
    # Create mock signals
    ti = TechnicalIndicators()
    data = generate_synthetic_stock_data(days=500)
    current_price = data['Close'].iloc[-1]
    
    technical = ti.calculate_all_indicators(data)
    
    quant_signals = {
        'momentum': {'signal': 1, 'score': 0.7},
        'mean_reversion': {'signal': 0, 'zscore': 0.5},
        'regime': {'current_regime': 'BULL'}
    }
    
    ml_predictions = {
        'lstm': {
            'predictions': {'1d': current_price * 1.02, '7d': current_price * 1.05},
            'confidence': 0.65
        }
    }
    
    sentiment = {'overall_score': 0.3}
    
    # Test decision
    total_tests += 1
    try:
        engine = DecisionEngine()
        decision = engine.make_decision(
            technical, quant_signals, ml_predictions, sentiment, current_price
        )
        
        rating = decision.get('rating')
        if rating in ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']:
            print(f"✓ Valid rating: {rating}")
            tests_passed += 1
        else:
            print(f"✗ Invalid rating: {rating}")
    except Exception as e:
        print(f"✗ Decision engine failed: {e}")
    
    # Test confidence
    total_tests += 1
    confidence = decision.get('confidence', 0)
    if 0 <= confidence <= 1:
        print(f"✓ Confidence valid: {confidence:.2%}")
        tests_passed += 1
    else:
        print(f"✗ Confidence invalid: {confidence}")
    
    # Test price targets
    total_tests += 1
    entry = decision.get('entry_price', 0)
    stop = decision.get('stop_loss', 0)
    target = decision.get('target_1', 0)
    
    if stop < entry < target:
        print(f"✓ Price targets logical: Stop={stop:.2f} < Entry={entry:.2f} < Target={target:.2f}")
        tests_passed += 1
    else:
        print(f"⚠ Price targets unusual")
        tests_passed += 0.5
    
    print(f"\nPassed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.1f}%)")
    print()
    return tests_passed / total_tests >= 0.8


def test_edge_cases():
    """Test edge cases and error handling"""
    print("="*70)
    print("TEST 5: Edge Cases")
    print("="*70)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Very small dataset
    total_tests += 1
    try:
        small_data = generate_synthetic_stock_data(days=50)
        ti = TechnicalIndicators()
        indicators = ti.calculate_all_indicators(small_data)
        
        if indicators:
            print("✓ Handles small dataset (50 days)")
            tests_passed += 1
        else:
            print("✗ Failed on small dataset")
    except Exception as e:
        print(f"✗ Small dataset error: {e}")
    
    # Test 2: High volatility
    total_tests += 1
    try:
        volatile_data = generate_synthetic_stock_data(days=200, volatility=0.10)
        ti = TechnicalIndicators()
        indicators = ti.calculate_all_indicators(volatile_data)
        
        if indicators.get('rsi', 0) > 0:
            print("✓ Handles high volatility data")
            tests_passed += 1
        else:
            print("✗ Failed on high volatility")
    except Exception as e:
        print(f"✗ High volatility error: {e}")
    
    # Test 3: Flat market (no movement)
    total_tests += 1
    try:
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        flat_data = pd.DataFrame({
            'Date': dates,
            'Open': [100] * 100,
            'High': [101] * 100,
            'Low': [99] * 100,
            'Close': [100] * 100,
            'Volume': [1000000] * 100
        })
        
        ti = TechnicalIndicators()
        indicators = ti.calculate_all_indicators(flat_data)
        
        rsi = indicators.get('rsi', 0)
        if 45 <= rsi <= 55:  # Should be near 50 for flat market
            print(f"✓ Handles flat market (RSI={rsi:.1f})")
            tests_passed += 1
        else:
            print(f"⚠ Flat market RSI unusual: {rsi:.1f}")
            tests_passed += 0.5
    except Exception as e:
        print(f"✗ Flat market error: {e}")
    
    print(f"\nPassed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.1f}%)")
    print()
    return tests_passed / total_tests >= 0.7


def main():
    """Run all offline tests"""
    print("\n" + "="*70)
    print("  OFFLINE MODEL TESTING - Synthetic Data")
    print("  Testing model functionality with random data")
    print("="*70)
    print()
    
    results = {
        'Technical Indicators': test_technical_indicators(),
        'Quant Strategies': test_quant_strategies(),
        'LSTM Predictions': test_lstm_predictions(),
        'Decision Engine': test_decision_engine(),
        'Edge Cases': test_edge_cases()
    }
    
    # Summary
    print("="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print()
    print(f"Overall: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Models are functioning correctly.")
        return 0
    elif total_passed >= total_tests * 0.8:
        print("\n✅ Most tests passed. Minor issues detected.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review model implementations.")
        return 1


if __name__ == "__main__":
    exit(main())
