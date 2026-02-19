"""
Options & Futures Data Provider
Fetch options chain and futures data for stocks
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

class OptionsFuturesProvider:
    """Fetch options and futures data"""
    
    def __init__(self):
        pass
    
    def get_options_chain(self, symbol: str) -> Dict:
        """
        Get complete options chain for a symbol
        Returns: calls and puts data with greeks
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            
            if not expirations:
                print(f"⚠️  No options available for {symbol}")
                return self._mock_options(symbol)
            
            # Get nearest expiration
            nearest_exp = expirations[0]
            
            # Fetch options chain
            opt = ticker.option_chain(nearest_exp)
            
            calls = opt.calls
            puts = opt.puts
            
            # Process calls
            calls_data = []
            for _, row in calls.iterrows():
                calls_data.append({
                    'strike': float(row['strike']),
                    'lastPrice': float(row['lastPrice']),
                    'bid': float(row['bid']),
                    'ask': float(row['ask']),
                    'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
                    'openInterest': int(row['openInterest']) if pd.notna(row['openInterest']) else 0,
                    'impliedVolatility': float(row['impliedVolatility']) if pd.notna(row['impliedVolatility']) else 0,
                    'inTheMoney': bool(row['inTheMoney'])
                })
            
            # Process puts
            puts_data = []
            for _, row in puts.iterrows():
                puts_data.append({
                    'strike': float(row['strike']),
                    'lastPrice': float(row['lastPrice']),
                    'bid': float(row['bid']),
                    'ask': float(row['ask']),
                    'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
                    'openInterest': int(row['openInterest']) if pd.notna(row['openInterest']) else 0,
                    'impliedVolatility': float(row['impliedVolatility']) if pd.notna(row['impliedVolatility']) else 0,
                    'inTheMoney': bool(row['inTheMoney'])
                })
            
            # Calculate PCR (Put-Call Ratio)
            total_call_oi = sum(c['openInterest'] for c in calls_data)
            total_put_oi = sum(p['openInterest'] for p in puts_data)
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
            
            return {
                'symbol': symbol,
                'expiration': nearest_exp,
                'expirations': list(expirations),
                'calls': calls_data,
                'puts': puts_data,
                'metrics': {
                    'pcr': pcr,
                    'total_call_volume': sum(c['volume'] for c in calls_data),
                    'total_put_volume': sum(p['volume'] for p in puts_data),
                    'total_call_oi': total_call_oi,
                    'total_put_oi': total_put_oi
                }
            }
        
        except Exception as e:
            print(f"Error fetching options for {symbol}: {e}")
            return self._mock_options(symbol)
    
    def get_futures_data(self, symbol: str) -> Dict:
        """
        Get futures data for a symbol
        Note: yfinance has limited futures support, this is a placeholder
        """
        # For Indian stocks, futures would come from NSE/BSE APIs
        # This is a mock implementation
        return self._mock_futures(symbol)
    
    def calculate_greeks(self, option_type: str, spot: float, strike: float, 
                        time_to_expiry: float, volatility: float, 
                        risk_free_rate: float = 0.06) -> Dict:
        """
        Calculate option Greeks using Black-Scholes
        Simplified implementation
        """
        import math
        from scipy.stats import norm
        
        # Calculate d1 and d2
        d1 = (math.log(spot / strike) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)
        
        # Delta
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
        else:
            delta = -norm.cdf(-d1)
        
        # Gamma (same for calls and puts)
        gamma = norm.pdf(d1) / (spot * volatility * math.sqrt(time_to_expiry))
        
        # Vega (same for calls and puts, per 1% change in IV)
        vega = spot * norm.pdf(d1) * math.sqrt(time_to_expiry) / 100
        
        # Theta (time decay per day)
        if option_type.lower() == 'call':
            theta = (-spot * norm.pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry)) 
                    - risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)) / 365
        else:
            theta = (-spot * norm.pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry)) 
                    + risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)) / 365
        
        return {
            'delta': round(delta, 4),
            'gamma': round(gamma, 4),
            'vega': round(vega, 4),
            'theta': round(theta, 4)
        }
    
    def _mock_options(self, symbol: str) -> Dict:
        """Generate mock options data"""
        base_price = 2400
        
        calls = [
            {'strike': 2350, 'lastPrice': 95.50, 'volume': 1250, 'openInterest': 5600, 'impliedVolatility': 0.28, 'inTheMoney': True},
            {'strike': 2400, 'lastPrice': 62.30, 'volume': 3200, 'openInterest': 12500, 'impliedVolatility': 0.25, 'inTheMoney': False},
            {'strike': 2450, 'lastPrice': 38.75, 'volume': 2100, 'openInterest': 8900, 'impliedVolatility': 0.27, 'inTheMoney': False},
        ]
        
        puts = [
            {'strike': 2350, 'lastPrice': 28.50, 'volume': 980, 'openInterest': 4200, 'impliedVolatility': 0.26, 'inTheMoney': False},
            {'strike': 2400, 'lastPrice': 55.80, 'volume': 2800, 'openInterest': 11200, 'impliedVolatility': 0.24, 'inTheMoney': False},
            {'strike': 2450, 'lastPrice': 89.25, 'volume': 1650, 'openInterest': 6800, 'impliedVolatility': 0.29, 'inTheMoney': True},
        ]
        
        return {
            'symbol': symbol,
            'expiration': '2024-03-28',
            'expirations': ['2024-03-28', '2024-04-25', '2024-05-30'],
            'calls': calls,
            'puts': puts,
            'metrics': {
                'pcr': 0.85,
                'total_call_volume': 6550,
                'total_put_volume': 5430,
                'total_call_oi': 27000,
                'total_put_oi': 22200
            }
        }
    
    def _mock_futures(self, symbol: str) -> Dict:
        """Generate mock futures data"""
        return {
            'symbol': symbol,
            'expiry': '2024-03-28',
            'lastPrice': 2420,
            'change': 25.50,
            'changePercent': 1.06,
            'volume': 125000,
            'openInterest': 550000,
            'basis': 15.30  # Future premium over spot
        }

def demo():
    """Demo options & futures provider"""
    provider = OptionsFuturesProvider()
    
    print("Options & Futures Provider Demo")
    print("="*70)
    
    symbol = "RELIANCE.NS"
    
    # Get options chain
    print(f"\nOptions Chain for {symbol}:")
    options = provider.get_options_chain(symbol)
    
    print(f"\nExpiration: {options['expiration']}")
    print(f"PCR (Put/Call Ratio): {options['metrics']['pcr']:.2f}")
    
    print("\nCALLS (Top 3 Strikes):")
    for call in options['calls'][:3]:
        print(f"  Strike {call['strike']}: Last ₹{call['lastPrice']}, OI {call['openInterest']}, IV {call['impliedVolatility']*100:.1f}%")
    
    print("\nPUTS (Top 3 Strikes):")
    for put in options['puts'][:3]:
        print(f"  Strike {put['strike']}: Last ₹{put['lastPrice']}, OI {put['openInterest']}, IV {put['impliedVolatility']*100:.1f}%")
    
    # Calculate Greeks
    print("\n\nOption Greeks (ATM Call):")
    greeks = provider.calculate_greeks('call', 2400, 2400, 0.08, 0.25)  # ~1 month to expiry
    print(f"Delta: {greeks['delta']}")
    print(f"Gamma: {greeks['gamma']}")
    print(f"Vega: {greeks['vega']}")  
    print(f"Theta: {greeks['theta']}")
    
    # Futures
    print("\n\nFutures Data:")
    futures = provider.get_futures_data(symbol)
    print(f"Last Price: ₹{futures['lastPrice']}")
    print(f"Change: +₹{futures['change']} ({futures['changePercent']}%)")
    print(f"Open Interest: {futures['openInterest']:,}")
    print(f"Basis: ₹{futures['basis']}")

if __name__ == "__main__":
    demo()
