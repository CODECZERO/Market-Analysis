#!/usr/bin/env python3
"""
Complete Integration Demo
Shows the full working pipeline from data fetch to recommendation
"""

import sys
import os
import asyncio
import logging

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker', 'src'))

from app import StockAnalysisWorker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_single_stock_analysis(symbol: str = "RELIANCE", exchange: str = "NSE"):
    """Demo: Analyze a single stock end-to-end"""
    print("="*80)
    print(f"  DEMO: Complete Stock Analysis Pipeline")
    print(f"  Symbol: {symbol} ({exchange})")
    print("="*80)
    print()
    
    # Initialize worker
    worker = StockAnalysisWorker()
    
    # Run analysis
    result = await worker.analyze_stock(symbol, exchange)
    
    if result['status'] == 'completed':
        print("\n" + "="*80)
        print("  ✅ ANALYSIS COMPLETE")
        print("="*80)
        
        # Display results
        print(f"\n📊 Stock: {result['symbol']}")
        print(f"💰 Current Price: ₹{result['current_price']:,.2f}")
        print(f"📅 Timestamp: {result['timestamp']}")
        
        # Technical indicators
        print("\n📈 Technical Indicators:")
        tech = result['technical']
        print(f"  RSI: {tech.get('rsi', 0):.2f}")
        print(f"  MACD: {tech.get('macd', 0):.2f}")
        print(f"  SMA 50: ₹{tech.get('sma_50', 0):,.2f}")
        print(f"  SMA 200: ₹{tech.get('sma_200', 0):,.2f}")
        
        # Quant signals
        print("\n🎯 Quantitative Signals:")
        quant = result['quant_signals']
        print(f"  Momentum: {quant.get('momentum', {}).get('signal', 0)}")
        print(f"  Mean Reversion Z-Score: {quant.get('mean_reversion', {}).get('zscore', 0):.2f}")
        print(f"  Market Regime: {quant.get('regime', {}).get('current_regime', 'UNKNOWN')}")
        
        # ML Predictions
        print("\n🤖 ML Predictions:")
        ml = result['ml_predictions']
        lstm = ml.get('lstm', {})
        predictions = lstm.get('predictions', {})
        print(f"  1-Day: ₹{predictions.get('1d', 0):,.2f}")
        print(f"  7-Day: ₹{predictions.get('7d', 0):,.2f}")
        print(f"  30-Day: ₹{predictions.get('30d', 0):,.2f}")
        print(f"  Confidence: {lstm.get('confidence', 0):.0%}")
        
        # Final Recommendation
        print("\n🎯 RECOMMENDATION:")
        rec = result['recommendation']
        print(f"  Rating: {rec['rating']}")
        print(f"  Confidence: {rec['confidence']:.0%}")
        print(f"  Entry Price: ₹{rec.get('entry_price', 0):,.2f}")
        print(f"  Stop Loss: ₹{rec.get('stop_loss', 0):,.2f}")
        print(f"  Target 1: ₹{rec.get('target_1', 0):,.2f}")
        print(f"  Target 2: ₹{rec.get('target_2', 0):,.2f}")
        
        print("\n" + "="*80)
        print("✅ Demo completed successfully!")
        print("="*80)
        
        return result
    else:
        print(f"\n❌ Analysis failed: {result.get('error')}")
        return None


async def main():
    """Run demo"""
    print("\n" + "="*80)
    print("  MARKET ANALYSIS SYSTEM - INTEGRATION DEMO")
    print("  Complete End-to-End Pipeline Demonstration")
    print("="*80)
    
    await demo_single_stock_analysis("RELIANCE", "NSE")
    
    print("\n" + "="*80)
    print("  🎉 DEMO COMPLETE!")
    print("="*80)
    print("\n📚 The core analysis engine works!")
    print("   See STATUS_REPORT.md for what's next\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)
