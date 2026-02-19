"""
Complete Stock Analysis Demo
Demonstrates the full analysis pipeline for a sample stock
Run this to test the integrated system
"""

import asyncio
import sys
sys.path.append('./worker/src')
sys.path.append('./orchestrator/src')

from data_providers import get_stock_data, get_nifty_data
from stock_analysis_orchestrator import orchestrate_stock_analysis
import json


async def mock_llm_chat(messages, temperature=0.7):
    """
    Mock LLM function for testing
    In production, this would be your actual Groq/NVIDIA chat function
    """
    # Simulate LLM response based on phase
    if 'Phase 1' in str(messages) or 'WHAT' in str(messages):
        response = {
            "what": "Reliance Industries is consolidating after Q3 earnings with price stabilizing around ₹2450-2500 range.",
            "why": "Primary driver is FUNDAMENTALS_SHIFT due to refining margin expansion and strong petrochemical demand.",
            "primary_cause": "FUNDAMENTALS_SHIFT",
            "evidence": [
                "Refining margins improved 15% QoQ",
                "Petrochemical segment revenue up 12%",
                "Free cash flow increased to ₹18,500 Cr"
            ],
            "confidence": 78
        }
    elif 'Phase 2' in str(messages) or 'WHEN' in str(messages):
        response = {
            "entry_window": "Next 5-7 trading days",
            "entry_trigger": "Price dips to ₹2440-2470 with RSI below 40",
            "horizon": "MEDIUM_TERM",
            "horizon_days": 90,
            "segment": "LARGE_CAP_STABILITY",
            "risk_events": ["RBI monetary policy on Feb 8", "Q4 earnings in April"],
            "justification": "Strong fundamentals support medium-term upside. Technical consolidation presents entry opportunity."
        }
    elif 'Phase 3' in str(messages) or 'HOW' in str(messages):
        response = {
            "rating": "BUY",
            "entry_price_range": {"min": 2440, "max": 2470},
            "stop_loss": 2380,
            "targets": {
                "t1_1week": 2550,
                "t2_30day": 2650,
                "t3_90day": 2800
            },
            "position_size_pct": 3.5,
            "risk_reward_ratio": 3.2,
            "reasoning": "Strong fundamentals (refining margin expansion) combined with oversold technical position (RSI 38) and positive ML forecast (LSTM predicts 8% upside in 90d). Decision engine composite score +62 indicates high-conviction BUY.",
            "key_catalysts": [
                "Refining margin sustainability",
                "Retail business growth acceleration",
                "Jio fiber subscriber additions"
            ],
            "risk_factors": [
                "Crude oil price volatility",
                "Delayed monetization of new energy vertical",
                "Regulatory changes in telecom sector"
            ]
        }
    else:
        response = {"text": "Mock response"}
    
    return {
        'text': json.dumps(response),
        'model': 'mock-llm',
        'provider': 'mock',
        'latencyMs': 500
    }


async def demo_analysis():
    """Run a complete stock analysis demo"""
    
    print("=" * 80)
    print(" MARKET ANALYSIS SYSTEM - COMPLETE DEMO")
    print("=" * 80)
    print()
    
    # Sample stock
    symbol = "RELIANCE"
    exchange = "NSE"
    
    print(f"📊 Analyzing {symbol} ({exchange})...")
    print()
    
    try:
        # Initialize data provider
        from data_providers.yfinance_provider import YFinanceProvider
        data_provider = YFinanceProvider()
        
        # Run orchestrated analysis
        result = await orchestrate_stock_analysis(
            symbol=symbol,
            exchange=exchange,
            llm_chat_function=mock_llm_chat,
            data_provider=data_provider
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Display results
        print("\n" + "="*80)
        print("📈 ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\n💰 Current Price: ₹{result['current_price']:,.2f}")
        
        print(f"\n📊 Technical Indicators:")
        tech = result.get('technical_indicators', {})
        print(f"  - RSI(14): {tech.get('rsi_14', 'N/A')}")
        print(f"  - MACD: {'Bullish' if tech.get('macd_bullish') else 'Bearish'}")
        print(f"  - Price vs SMA50: {tech.get('price_vs_sma50', 0):+.2f}%")
        print(f"  - ADX: {tech.get('adx_14', 'N/A')} ({tech.get('trend_strength', 'N/A')})")
        
        print(f"\n🔬 Quantitative Signals:")
        quant = result.get('quant_signals', {})
        print(f"  - Mean Reversion: {quant.get('mean_reversion', {}).get('signal', 'N/A')}")
        print(f"  - Market Regime: {quant.get('regime', {}).get('regime', 'N/A')}")
        
        print(f"\n🤖 ML Predictions:")
        ml = result.get('ml_predictions', {})
        if 'lstm' in ml and ml['lstm']:
            print(f"  - 30-day forecast: ₹{ml['lstm'].get('30d', 0):,.2f}")
            print(f"  - 90-day forecast: ₹{ml['lstm'].get('90d', 0):,.2f}")
        print(f"  - XGBoost: {ml.get('xgboost', {}).get('signal', 'N/A')}")
        
        print(f"\n💭 Sentiment Analysis:")
        sentiment = result.get('sentiment', {})
        print(f"  - Fused Score: {sentiment.get('fused_sentiment', 0):.2f}")
        print(f"  - Signal: {sentiment.get('signal', 'N/A')}")
        
        print(f"\n🎯 LLM Phase 1 (What/Why):")
        phase1 = result.get('phase1_what_why', {})
        print(f"  - {phase1.get('what', 'N/A')}")
        print(f"  - Primary Cause: {phase1.get('primary_cause', 'N/A')}")
        print(f"  - Confidence: {phase1.get('confidence', 0)}%")
        
        print(f"\n⏰ LLM Phase 2 (When/Where):")
        phase2 = result.get('phase2_when_where', {})
        print(f"  - Entry Window: {phase2.get('entry_window', 'N/A')}")
        print(f"  - Entry Trigger: {phase2.get('entry_trigger', 'N/A')}")
        print(f"  - Horizon: {phase2.get('horizon', 'N/A')} ({phase2.get('horizon_days', 0)} days)")
        
        print(f"\n🎯 Decision Engine:")
        decision = result.get('decision', {})
        print(f"  - Recommendation: {decision.get('recommendation', 'N/A')}")
        print(f"  - Composite Score: {decision.get('composite_score', 0):.1f}/100")
        print(f"  - Confidence: {decision.get('confidence', 0):.1f}%")
        
        print(f"\n💼 LLM Phase 3 (Final Recommendation):")
        phase3 = result.get('phase3_recommendation', {})
        print(f"  - Rating: {phase3.get('rating', 'N/A')}")
        entry = phase3.get('entry_price_range', {})
        print(f"  - Entry Range: ₹{entry.get('min', 0):,.2f} - ₹{entry.get('max', 0):,.2f}")
        print(f"  - Stop Loss: ₹{phase3.get('stop_loss', 0):,.2f}")
        targets = phase3.get('targets', {})
        print(f"  - Target 1 (1w): ₹{targets.get('t1_1week', 0):,.2f}")
        print(f"  - Target 2 (30d): ₹{targets.get('t2_30day', 0):,.2f}")
        print(f"  - Target 3 (90d): ₹{targets.get('t3_90day', 0):,.2f}")
        print(f"  - Position Size: {phase3.get('position_size_pct', 0):.1f}%")
        print(f"  - Risk/Reward: 1:{phase3.get('risk_reward_ratio', 0):.1f}")
        
        print("\n" + "="*80)
        print("✅ Analysis Complete!")
        print(f"   Analysis ID: {result.get('analysis_id', 'N/A')}")
        print("="*80)
        
        # Show markdown report if available
        if 'markdown_report' in phase3:
            print("\n\n📄 PROFESSIONAL RECOMMENDATION REPORT:")
            print("="*80)
            print(phase3['markdown_report'])
            print("="*80)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Market Analysis System Demo...\n")
    asyncio.run(demo_analysis())
