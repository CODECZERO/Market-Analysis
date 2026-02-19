"""
Sector Correlation Analysis
Analyze correlations between stocks and sectors
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import List, Dict
from datetime import datetime, timedelta

class SectorAnalyzer:
    """Analyze sector correlations and sector rotation"""
    
    # Indian stock sectors
    SECTORS = {
        'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HDFCBANK.NS'],
        'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS'],
        'Energy': ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS'],
        'Auto': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS'],
        'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS']
    }
    
    def __init__(self):
        self.sector_data = {}
    
    def fetch_sector_data(self, period='6mo'):
        """Fetch historical data for all sector stocks"""
        for sector, symbols in self.SECTORS.items():
            sector_prices = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period)
                    if len(data) > 0:
                        sector_prices.append(data['Close'])
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
            
            if sector_prices:
                # Calculate sector index (average of stocks)
                self.sector_data[sector] = pd.concat(sector_prices, axis=1).mean(axis=1)
    
    def calculate_sector_correlations(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between sectors"""
        if not self.sector_data:
            self.fetch_sector_data()
        
        df = pd.DataFrame(self.sector_data)
        correlation_matrix = df.corr()
        
        return correlation_matrix.to_dict()
    
    def calculate_stock_sector_correlation(self, symbol: str) -> Dict[str, float]:
        """Calculate correlation of a stock with each sector"""
        if not self.sector_data:
            self.fetch_sector_data()
        
        # Fetch stock data
        ticker = yf.Ticker(symbol)
        stock_data = ticker.history(period='6mo')['Close']
        
        correlations = {}
        for sector, sector_index in self.sector_data.items():
            # Align dates
            common_dates = stock_data.index.intersection(sector_index.index)
            if len(common_dates) > 30:  # Need enough data points
                stock_aligned = stock_data.loc[common_dates]
                sector_aligned = sector_index.loc[common_dates]
                
                corr = stock_aligned.corr(sector_aligned)
                correlations[sector] = float(corr)
        
        return correlations
    
    def identify_sector_leaders_laggards(self, period='1mo') -> Dict:
        """Identify top performing and lagging sectors"""
        if not self.sector_data:
            self.fetch_sector_data()
        
        performance = {}
        for sector, data in self.sector_data.items():
            # Calculate returns over period
            if len(data) > 0:
                returns = (data.iloc[-1] / data.iloc[0] - 1) * 100
                performance[sector] = float(returns)
        
        # Sort sectors
        sorted_sectors = sorted(performance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'leaders': sorted_sectors[:2],  # Top 2
            'laggards': sorted_sectors[-2:],  # Bottom 2
            'all_performance': performance
        }
    
    def analyze_sector_rotation(self) -> Dict:
        """Analyze sector rotation trends"""
        if not self.sector_data:
            self.fetch_sector_data()
        
        rotation_signals = {}
        
        for sector, data in self.sector_data.items():
            if len(data) < 50:
                continue
            
            # Calculate short-term (20d) and long-term (50d) momentum
            short_momentum = (data.iloc[-1] / data.iloc[-20] - 1) * 100 if len(data) >= 20 else 0
            long_momentum = (data.iloc[-1] / data.iloc[-50] - 1) * 100 if len(data) >= 50 else 0
            
            # Rotation signal
            if short_momentum > long_momentum and short_momentum > 5:
                signal = 'ROTATING_IN'  # Money flowing into sector
            elif short_momentum < long_momentum and short_momentum < -5:
                signal = 'ROTATING_OUT'  # Money flowing out
            else:
                signal = 'STABLE'
            
            rotation_signals[sector] = {
                'signal': signal,
                'short_momentum': float(short_momentum),
                'long_momentum': float(long_momentum),
                'trend_strength': abs(short_momentum - long_momentum)
            }
        
        return rotation_signals
    
    def get_sector_for_stock(self, symbol: str) -> str:
        """Identify which sector a stock belongs to"""
        for sector, symbols in self.SECTORS.items():
            if symbol in symbols:
                return sector
        return 'OTHER'

def demo():
    """Demo sector analysis"""
    analyzer = SectorAnalyzer()
    
    print("Sector Correlation Analysis")
    print("="*70)
    
    # Fetch data
    print("\nFetching sector data...")
    analyzer.fetch_sector_data()
    
    # Sector correlations
    print("\nSector Correlation Matrix:")
    correlations = analyzer.calculate_sector_correlations()
    for sector1, corrs in correlations.items():
        print(f"\n{sector1}:")
        for sector2, corr in corrs.items():
            if sector1 != sector2:
                print(f"  vs {sector2}: {corr:.3f}")
    
    # Leaders/Laggards
    print("\n\nSector Performance:")
    performance = analyzer.identify_sector_leaders_laggards()
    print("\nLeaders:")
    for sector, perf in performance['leaders']:
        print(f"  {sector}: +{perf:.2f}%")
    print("\nLaggards:")
    for sector, perf in performance['laggards']:
        print(f"  {sector}: {perf:.2f}%")
    
    # Rotation
    print("\n\nSector Rotation Signals:")
    rotation = analyzer.analyze_sector_rotation()
    for sector, data in rotation.items():
        print(f"\n{sector}: {data['signal']}")
        print(f"  Short-term: {data['short_momentum']:+.2f}%")
        print(f"  Long-term: {data['long_momentum']:+.2f}%")
    
    # Stock correlation
    print("\n\nRELIANCE.NS Sector Correlations:")
    stock_corrs = analyzer.calculate_stock_sector_correlation('RELIANCE.NS')
    for sector, corr in stock_corrs.items():
        print(f"  {sector}: {corr:.3f}")

if __name__ == "__main__":
    demo()
