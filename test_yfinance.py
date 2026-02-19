import yfinance as yf
import json

def test_financials(symbol):
    ticker = yf.Ticker(symbol)
    print(f"--- {symbol} Financials ---")
    try:
        cashflow = ticker.cashflow
        print("Cashflow columns:", cashflow.columns if not cashflow.empty else "Empty")
        print("Cashflow index:", cashflow.index.tolist() if not cashflow.empty else "Empty")
        
        balance_sheet = ticker.balance_sheet
        print("Balance Sheet index:", balance_sheet.index.tolist() if not balance_sheet.empty else "Empty")
        
        financials = ticker.financials
        print("Income Statement index:", financials.index.tolist() if not financials.empty else "Empty")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_financials("TCS.NS")
