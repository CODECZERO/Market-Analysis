
import requests
import json
import sys

API_URL = "http://localhost:8000/api/analyze/comprehensive"
SYMBOL = "HDFCBANK.NS"

print(f"🚀 TEST: Triggering COMPREHENSIVE ANALYSIS for {SYMBOL}...")
print(f"📡 Endpoint: {API_URL}")
print("⏳ Waiting for Orchestrator (approx 10-20s)...")

try:
    response = requests.post(API_URL, json={
        "symbol": SYMBOL,
        "use_llm": True,
        "use_ml": True, 
        "use_quant": True
    }, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Received Advanced Analysis Payload:")
        print(f"   • Symbol: {data.get('symbol')}")
        print(f"   • Price: {data.get('current_price')}")
        
        # Verify Advanced Components
        llm = data.get('llm_analysis', {})
        print(f"   • LLM Recommendation: {llm.get('recommendation')} (Confidence: {llm.get('confidence')})")
        
        ml = data.get('ml_predictions', {})
        print(f"   • ML Predictions Present: {list(ml.keys())}")
        
        quant = data.get('quant_signals', {})
        print(f"   • Quant Strategy Keys: {list(quant.keys())}")
        
        print("\n📝 Full analysis captured. The Orchestrator is ACTIVE.")
    else:
        print(f"❌ API Failed: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Connection Failed: {e}")
