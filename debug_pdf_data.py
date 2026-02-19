
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def debug_stock_data(symbol):
    print(f"Fetching data for {symbol}...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/analyze/comprehensive",
            json={
                "symbol": symbol,
                "use_llm": True,
                "use_ml": True,
                "use_quant": True,
                "use_ensemble": True,
                "use_scrapers": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("DATA KEYS:", list(data.keys()))
            
            # Check for decision
            print("\n--- DECISION ---")
            print(json.dumps(data.get('decision', {}), indent=2))
            
            # Check for quant_signals -> forecasts
            print("\n--- QUANT SIGNALS -> FORECASTS ---")
            quant = data.get('quant_signals', {})
            print("Quant Keys:", list(quant.keys()))
            print(json.dumps(quant.get('forecasts', {}), indent=2))
            
            # Check for technical_indicators
            print("\n--- TECHNICAL INDICATORS ---")
            print(json.dumps(data.get('technical_indicators', {}), indent=2))
            
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sym = sys.argv[1] if len(sys.argv) > 1 else "HINDCOPPER.NS"
    debug_stock_data(sym)
