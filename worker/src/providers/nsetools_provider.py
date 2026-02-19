"""
NSETools Integration
Real-time quotes for Indian stocks from NSE
"""

try:
    from nsetools import Nse
    NSE_AVAILABLE = True
except ImportError:
    NSE_AVAILABLE = False
    print("⚠️  nsetools not installed. Install with: pip install nsetools")

import yfinance as yf
from typing import Dict, List
from datetime import datetime

class NSEToolsProvider:
    """NSETools provider for real-time Indian stock quotes"""
    
    def __init__(self):
        if NSE_AVAILABLE:
            try:
                self.nse = Nse()
                print("✅ NSETools initialized")
            except Exception as e:
                print(f"⚠️  NSETools init error: {e}")
                self.nse = None
        else:
            self.nse = None
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote from NSE"""
        # Clean symbol (remove .NS suffix)
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        if self.nse:
            try:
                quote = self.nse.get_quote(clean_symbol)
                
                if quote:
                    return {
                        'symbol': symbol,
                        'company_name': quote.get('companyName', ''),
                        'last_price': float(quote.get('lastPrice', 0)),
                        'change': float(quote.get('change', 0)),
                        'change_percent': float(quote.get('pChange', 0)),
                        'open': float(quote.get('open', 0)),
                        'high': float(quote.get('dayHigh', 0)),
                        'low': float(quote.get('dayLow', 0)),
                        'previous_close': float(quote.get('previousClose', 0)),
                        'volume': int(quote.get('totalTradedVolume', 0)),
                        'value': float(quote.get('totalTradedValue', 0)),
                        '52week_high': float(quote.get('high52', 0)),
                        '52week_low': float(quote.get('low52', 0)),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'NSETools'
                    }
            
            except Exception as e:
                print(f"Error getting NSE quote for {symbol}: {e}")
        
        # Fallback to yfinance
        return self._fallback_quote(symbol)
    
    def get_top_gainers(self) -> List[Dict]:
        """Get top gainers from NSE"""
        if self.nse:
            try:
                gainers = self.nse.get_top_gainers()
                
                result = []
                for stock in gainers[:10]:
                    result.append({
                        'symbol': stock.get('symbol', ''),
                        'company': stock.get('series', ''),
                        'last_price': float(stock.get('ltp', 0)),
                        'change': float(stock.get('netPrice', 0)),
                        'change_percent': float(stock.get('tradedQuantity', 0))
                    })
                
                return result
            
            except Exception as e:
                print(f"Error getting top gainers: {e}")
        
        return []
    
    def get_top_losers(self) -> List[Dict]:
        """Get top losers from NSE"""
        if self.nse:
            try:
                losers = self.nse.get_top_losers()
                
                result = []
                for stock in losers[:10]:
                    result.append({
                        'symbol': stock.get('symbol', ''),
                        'company': stock.get('series', ''),
                        'last_price': float(stock.get('ltp', 0)),
                        'change': float(stock.get('netPrice', 0)),
                        'change_percent': float(stock.get('tradedQuantity', 0))
                    })
                
                return result
            
            except Exception as e:
                print(f"Error getting top losers: {e}")
        
        return []
    
    def is_valid_code(self, symbol: str) -> bool:
        """Check if stock code is valid"""
        if self.nse:
            try:
                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                return self.nse.is_valid_code(clean_symbol)
            except:
                pass
        
        return False
    
    def get_stock_codes(self) -> List[str]:
        """Get all available stock codes"""
        if self.nse:
            try:
                return self.nse.get_stock_codes()
            except:
                pass
        
        return []
    
    def _fallback_quote(self, symbol: str) -> Dict:
        """Fallback to yfinance for quote"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='2d')
            
            if len(data) >= 1:
                latest = data.iloc[-1]
                prev = data.iloc[-2] if len(data) > 1 else latest
                
                current_price = float(latest['Close'])
                prev_close = float(prev['Close'])
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                
                return {
                    'symbol': symbol,
                    'last_price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'volume': int(latest['Volume']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'YFinance (Fallback)'
                }
        
        except Exception as e:
            print(f"Fallback quote error: {e}")
        
        return {}

def demo():
    """Demo NSETools provider"""
    provider = NSEToolsProvider()
    
    print("NSETools Provider Demo")
    print("="*70)
    
    # Get quote
    symbol = "RELIANCE"
    print(f"\nReal-time Quote for {symbol}:")
    quote = provider.get_quote(symbol)
    
    if quote:
        print(f"Company: {quote.get('company_name', 'N/A')}")
        print(f"Last Price: ₹{quote.get('last_price', 0):,.2f}")
        print(f"Change: ₹{quote.get('change', 0):+,.2f} ({quote.get('change_percent', 0):+.2f}%)")
        print(f"Volume: {quote.get('volume', 0):,}")
        print(f"52W High/Low: ₹{quote.get('52week_high', 0):,.2f} / ₹{quote.get('52week_low', 0):,.2f}")
    
    # Top gainers
    print("\n\nTop Gainers:")
    print("="*70)
    gainers = provider.get_top_gainers()
    for i, stock in enumerate(gainers[:5], 1):
        print(f"{i}. {stock['symbol']}: ₹{stock['last_price']} ({stock['change_percent']:+.2f}%)")
    
    # Top losers  
    print("\n\nTop Losers:")
    print("="*70)
    losers = provider.get_top_losers()
    for i, stock in enumerate(losers[:5], 1):
        print(f"{i}. {stock['symbol']}: ₹{stock['last_price']} ({stock['change_percent']:+.2f}%)")

if __name__ == "__main__":
    demo()
