#!/usr/bin/env python3
"""
Quick Watchlist Analyzer
Analyze your stocks quickly without the full system
"""

import asyncio
import sys
import os

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker', 'src'))

from app import StockAnalysisWorker

# Your watchlist
WATCHLIST = [
    ("RELIANCE", "NSE"),
    ("TCS", "NSE"),
    ("INFY", "NSE"),
    ("HDFCBANK", "NSE"),
    ("ICICIBANK", "NSE"),
]


async def analyze_watchlist():
    """Analyze entire watchlist"""
    print("="*70)
    print("  📊 Watchlist Analysis")
    print("="*70)
    print()
    
    worker = StockAnalysisWorker()
    results = []
    
    for i, (symbol, exchange) in enumerate(WATCHLIST, 1):
        print(f"[{i}/{len(WATCHLIST)}] Analyzing {symbol}...")
        
        result = await worker.analyze_stock(symbol, exchange)
        
        if result['status'] == 'completed':
            rec = result['recommendation']
            results.append({
                'symbol': symbol,
                'price': result['current_price'],
                'rating': rec['rating'],
                'confidence': rec['confidence'],
                'entry': rec.get('entry_price', 0),
                'target': rec.get('target_1', 0),
                'stop': rec.get('stop_loss', 0)
            })
            
            print(f"  ✓ {rec['rating']} (Confidence: {rec['confidence']:.0%})")
        else:
            print(f"  ✗ Failed: {result.get('error')}")
        
        print()
        
        # Small delay between stocks
        if i < len(WATCHLIST):
            await asyncio.sleep(2)
    
    # Summary
    print("="*70)
    print("  📊 SUMMARY")
    print("="*70)
    print()
    print(f"{'Symbol':<12} {'Price':>10} {'Rating':<12} {'Conf':>6} {'Entry':>10} {'Target':>10}")
    print("-"*70)
    
    for r in results:
        print(f"{r['symbol']:<12} ₹{r['price']:>9,.2f} {r['rating']:<12} {r['confidence']:>5.0%} "
              f"₹{r['entry']:>9,.2f} ₹{r['target']:>9,.2f}")
    
    print()
    
    # Stats
    buy_count = sum(1 for r in results if 'BUY' in r['rating'])
    hold_count = sum(1 for r in results if 'HOLD' in r['rating'])
    sell_count = sum(1 for r in results if 'SELL' in r['rating'])
    
    print(f"BUY: {buy_count}  │  HOLD: {hold_count}  │  SELL: {sell_count}")
    print("="*70)


if __name__ == "__main__":
    print("\n🚀 Starting watchlist analysis...")
    print("   This will take ~2-3 minutes\n")
    
    try:
        asyncio.run(analyze_watchlist())
        print("\n✅ Analysis complete!\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
