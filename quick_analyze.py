#!/usr/bin/env python3
"""
Quick Stock Analysis Script
Analyze any stock with one command
"""

import asyncio
import sys
import os

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker/src'))

from orchestrator_enhanced import StockAnalysisOrchestrator


async def analyze(symbol: str):
    """Analyze a stock"""
    orchestrator = StockAnalysisOrchestrator()
    
    # Add .NS if needed
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        symbol = f"{symbol}.NS"
    
    result = await orchestrator.analyze_stock(
        symbol,
        use_llm=True,
        use_scrapers=True
    )
    
    print(orchestrator.format_recommendation(result))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_analyze.py <SYMBOL>")
        print("Example: python quick_analyze.py RELIANCE")
        sys.exit(1)
    
    symbol = sys.argv[1]
    asyncio.run(analyze(symbol))
