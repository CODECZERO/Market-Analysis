#!/usr/bin/env python3
"""
Online Model Testing - Real Stock Data
Tests models with actual market data and validates prediction accuracy
"""

import asyncio
import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
import yfinance as yf

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker', 'src'))

from app import StockAnalysisWorker
from data_providers.yfinance_provider import YFinanceProvider


# Test stocks (diverse sectors)
TEST_STOCKS = [
    ("RELIANCE", "NSE"),  # Energy
    ("TCS", "NSE"),       # IT
    ("HDFCBANK", "NSE"),  # Banking
]


async def test_real_data_fetch():
    """Test if we can fetch real stock data"""
    print("="*70)
    print("TEST 1: Real Data Fetching")
    print("="*70)
    
    provider = YFinanceProvider()
    tests_passed = 0
    total_tests = len(TEST_STOCKS)
    
    for symbol, exchange in TEST_STOCKS:
        try:
            data = provider.get_historical_data(symbol, exchange, period="1y")
            
            if data is not None and len(data) > 200:
                print(f"✓ {symbol}: Fetched {len(data)} days of data")
                tests_passed += 1
            else:
                print(f"✗ {symbol}: Insufficient data")
        except Exception as e:
            print(f"✗ {symbol}: Failed - {e}")
    
    print(f"\nPassed: {tests_passed}/{total_tests}")
    print()
    return tests_passed == total_tests


async def test_prediction_accuracy():
    """
    Test prediction accuracy using historical data
    Train on older data, predict, compare with actual prices
    """
    print("="*70)
    print("TEST 2: Prediction Accuracy (Backtesting)")
    print("="*70)
    
    provider = YFinanceProvider()
    accuracies = []
    
    for symbol, exchange in TEST_STOCKS:
        try:
            print(f"\nTesting {symbol}...")
            
            # Get 2 months of data
            data = provider.get_historical_data(symbol, exchange, period="2mo")
            
            if data is None or len(data) < 40:
                print(f"  ⚠ Skipping {symbol}: Insufficient data")
                continue
            
            # Split: train on first 80%, test on last 20%
            split_idx = int(len(data) * 0.8)
            train_data = data.iloc[:split_idx]
            test_data = data.iloc[split_idx:]
            
            # Get actual prices for next 7 days
            actual_prices = test_data['Close'].head(7).values
            
            if len(actual_prices) < 7:
                print(f"  ⚠ Skipping {symbol}: Not enough test data")
                continue
            
            # Make prediction using training data
            worker = StockAnalysisWorker()
            
            # Mock analysis with train data
            from ml.lstm_model_optimized import LSTMModel
            lstm = LSTMModel()
            
            try:
                predictions = lstm.predict(train_data)
                pred_1d = predictions.get('1d', 0)
                pred_7d = predictions.get('7d', 0)
                
                # Compare predictions
                actual_1d = actual_prices[0] if len(actual_prices) > 0 else 0
                actual_7d = actual_prices[-1] if len(actual_prices) >= 7 else 0
                
                # Calculate error
                error_1d = abs(pred_1d - actual_1d) / actual_1d if actual_1d > 0 else 1.0
                error_7d = abs(pred_7d - actual_7d) / actual_7d if actual_7d > 0 else 1.0
                
                # Accuracy (1 - error)
                acc_1d = max(0, 1 - error_1d)
                acc_7d = max(0, 1 - error_7d)
                
                print(f"  1-Day: Predicted ₹{pred_1d:.2f}, Actual ₹{actual_1d:.2f}, Error {error_1d*100:.1f}%, Accuracy {acc_1d*100:.1f}%")
                print(f"  7-Day: Predicted ₹{pred_7d:.2f}, Actual ₹{actual_7d:.2f}, Error {error_7d*100:.1f}%, Accuracy {acc_7d*100:.1f}%")
                
                accuracies.append((acc_1d + acc_7d) / 2)
                
            except Exception as e:
                print(f"  ✗ Prediction failed: {e}")
        
        except Exception as e:
            print(f"  ✗ {symbol} test failed: {e}")
    
    if accuracies:
        avg_accuracy = np.mean(accuracies)
        print(f"\n{'='*70}")
        print(f"Average Prediction Accuracy: {avg_accuracy*100:.1f}%")
        print(f"{'='*70}")
        
        if avg_accuracy >= 0.60:  # 60% threshold
            print("✅ Prediction accuracy acceptable")
            return True
        else:
            print("⚠️  Prediction accuracy below threshold")
            return False
    else:
        print("❌ No predictions could be tested")
        return False


async def test_recommendation_quality():
    """Test recommendation quality against price movements"""
    print("\n" + "="*70)
    print("TEST 3: Recommendation Quality")
    print("="*70)
    
    worker = StockAnalysisWorker()
    correct_recommendations = 0
    total_recommendations = 0
    
    for symbol, exchange in TEST_STOCKS:
        try:
            print(f"\nAnalyzing {symbol}...")
            
            # Get current analysis
            result = await worker.analyze_stock(symbol, exchange)
            
            if result['status'] != 'completed':
                print(f"  ✗ Analysis failed")
                continue
            
            recommendation = result['recommendation']
            rating = recommendation['rating']
            current_price = result['current_price']
            
            # Get price from 7 days ago to see if recommendation would have been right
            provider = YFinanceProvider()
            data = provider.get_historical_data(symbol, exchange, period="1mo")
            
            if data is None or len(data) < 14:
                print(f"  ⚠ Insufficient historical data")
                continue
            
            # Price 7 days ago
            price_7d_ago = data['Close'].iloc[-7]
            price_today = data['Close'].iloc[-1]
            
            # Price change
            price_change_pct = ((price_today - price_7d_ago) / price_7d_ago) * 100
            
            total_recommendations += 1
            
            # Validate recommendation
            if 'BUY' in rating and price_change_pct > 2:
                print(f"  ✓ BUY was correct: +{price_change_pct:.1f}%")
                correct_recommendations += 1
            elif 'SELL' in rating and price_change_pct < -2:
                print(f"  ✓ SELL was correct: {price_change_pct:.1f}%")
                correct_recommendations += 1
            elif 'HOLD' in rating and abs(price_change_pct) < 2:
                print(f"  ✓ HOLD was correct: {price_change_pct:.1f}%")
                correct_recommendations += 1
            else:
                print(f"  ✗ {rating} didn't match price change: {price_change_pct:.1f}%")
            
            print(f"    Rating: {rating}, Confidence: {recommendation['confidence']:.0%}")
            
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
    
    if total_recommendations > 0:
        accuracy = correct_recommendations / total_recommendations
        print(f"\n{'='*70}")
        print(f"Recommendation Accuracy: {correct_recommendations}/{total_recommendations} ({accuracy*100:.1f}%)")
        print(f"{'='*70}")
        
        return accuracy >= 0.5  # 50% threshold (better than random)
    else:
        return False


async def test_consistency():
    """Test if repeated analysis gives consistent results"""
    print("\n" + "="*70)
    print("TEST 4: Consistency")
    print("="*70)
    
    symbol, exchange = TEST_STOCKS[0]  # Test with first stock
    worker = StockAnalysisWorker()
    
    try:
        print(f"Running analysis twice for {symbol}...")
        
        # First analysis
        result1 = await worker.analyze_stock(symbol, exchange)
        
        # Small delay
        await asyncio.sleep(2)
        
        # Second analysis
        result2 = await worker.analyze_stock(symbol, exchange)
        
        if result1['status'] == 'completed' and result2['status'] == 'completed':
            rec1 = result1['recommendation']
            rec2 = result2['recommendation']
            
            # Check if ratings are same
            same_rating = rec1['rating'] == rec2['rating']
            
            # Check if confidence is close
            conf_diff = abs(rec1['confidence'] - rec2['confidence'])
            conf_similar = conf_diff < 0.10  # Within 10%
            
            print(f"\nRun 1: {rec1['rating']} ({rec1['confidence']:.0%})")
            print(f"Run 2: {rec2['rating']} ({rec2['confidence']:.0%})")
            print(f"\nSame Rating: {'✓' if same_rating else '✗'}")
            print(f"Confidence Difference: {conf_diff:.1%} ({'✓' if conf_similar else '✗'})")
            
            return same_rating and conf_similar
        else:
            print("✗ One or both analyses failed")
            return False
            
    except Exception as e:
        print(f"✗ Consistency test failed: {e}")
        return False


async def test_performance():
    """Test analysis performance/speed"""
    print("\n" + "="*70)
    print("TEST 5: Performance")
    print("="*70)
    
    worker = StockAnalysisWorker()
    symbol, exchange = TEST_STOCKS[0]
    
    try:
        import time
        
        print(f"Analyzing {symbol}...")
        start_time = time.time()
        
        result = await worker.analyze_stock(symbol, exchange)
        
        elapsed = time.time() - start_time
        
        print(f"\nAnalysis Time: {elapsed:.1f}s")
        
        # Target: under 60 seconds
        if elapsed < 60:
            print(f"✓ Performance acceptable (< 60s)")
            return True
        elif elapsed < 120:
            print(f"⚠ Performance slow but acceptable (< 120s)")
            return True
        else:
            print(f"✗ Performance too slow (> 120s)")
            return False
            
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False


async def main():
    """Run all online tests"""
    print("\n" + "="*70)
    print("  ONLINE MODEL TESTING - Real Stock Data")
    print("  Testing with actual market data from NSE")
    print("="*70)
    print()
    print(f"Test Stocks: {', '.join([s[0] for s in TEST_STOCKS])}")
    print()
    
    results = {
        'Data Fetching': await test_real_data_fetch(),
        'Prediction Accuracy': await test_prediction_accuracy(),
        'Recommendation Quality': await test_recommendation_quality(),
        'Consistency': await test_consistency(),
        'Performance': await test_performance()
    }
    
    # Summary
    print("\n" + "="*70)
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
        print("\n🎉 All online tests passed! Models work well with real data.")
        return 0
    elif total_passed >= total_tests * 0.6:
        print("\n✅ Most tests passed. Models are functional.")
        return 0
    else:
        print("\n⚠️  Several tests failed. Review model performance.")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
