#!/usr/bin/env python3
"""
Portfolio Backtester - Simulate trades and calculate returns
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class PortfolioBacktester:
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades = []
        self.holdings = {}
    
    def backtest_strategy(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """
        Backtest simple momentum strategy
        """
        print(f"\n📊 Backtesting {len(symbols)} stocks from {start_date} to {end_date}")
        print(f"Initial Capital: ₹{self.initial_capital:,.2f}\n")
        
        portfolio_value_history = []
        
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty:
                    continue
                
                # Simple RSI strategy
                close = hist['Close']
                
                # Calculate RSI
                delta = close.diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = -delta.where(delta < 0, 0).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # Buy when RSI < 30, Sell when RSI > 70
                for i in range(20, len(hist)):
                    date = hist.index[i]
                    price = hist['Close'].iloc[i]
                    rsi_val = rsi.iloc[i]
                    
                    if pd.isna(rsi_val):
                        continue
                    
                    # Buy signal
                    if rsi_val < 30 and symbol not in self.holdings:
                        shares = int(self.capital * 0.2 / price)  # 20% of capital per stock
                        if shares > 0:
                            cost = shares * price
                            self.capital -= cost
                            self.holdings[symbol] = {
                                "shares": shares,
                                "buy_price": price,
                                "buy_date": date
                            }
                            
                            trade = {
                                "symbol": symbol,
                                "action": "BUY",
                                "shares": shares,
                                "price": price,
                                "date": date,
                                "cost": cost
                            }
                            self.trades.append(trade)
                    
                    # Sell signal
                    elif rsi_val > 70 and symbol in self.holdings:
                        holding = self.holdings[symbol]
                        shares = holding["shares"]
                        proceeds = shares * price
                        self.capital += proceeds
                        
                        profit = proceeds - (shares * holding["buy_price"])
                        profit_pct = (profit / (shares * holding["buy_price"])) * 100
                        
                        trade = {
                            "symbol": symbol,
                            "action": "SELL",
                            "shares": shares,
                            "price": price,
                            "date": date,
                            "proceeds": proceeds,
                            "profit": profit,
                            "profit_pct": profit_pct,
                            "hold_days": (date - holding["buy_date"]).days
                        }
                        self.trades.append(trade)
                        del self.holdings[symbol]
                
            except Exception as e:
                print(f"Error backtesting {symbol}: {e}")
                continue
        
        # Calculate final portfolio value
        final_value = self.capital
        for symbol, holding in self.holdings.items():
            try:
                current_price = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
                final_value += holding["shares"] * current_price
            except:
                pass
        
        total_return = final_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Calculate trade statistics
        winning_trades = [t for t in self.trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('profit', 0) <= 0]
        
        results = {
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "total_trades": len([t for t in self.trades if t['action'] == 'SELL']),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": (len(winning_trades) / len(self.trades) * 100) if self.trades else 0,
            "avg_profit": sum(t.get('profit', 0) for t in self.trades) / len(self.trades) if self.trades else 0,
            "best_trade": max([t.get('profit_pct', 0) for t in self.trades], default=0),
            "worst_trade": min([t.get('profit_pct', 0) for t in self.trades], default=0),
            "still_holding": len(self.holdings)
        }
        
        return results
    
    def print_results(self, results: Dict):
        """Pretty print backtest results"""
        print("\n" + "="*80)
        print("BACKTEST RESULTS".center(80))
        print("="*80)
        
        print(f"\n💰 Capital:")
        print(f"  Initial:  ₹{results['initial_capital']:,.2f}")
        print(f"  Final:    ₹{results['final_value']:,.2f}")
        print(f"  Return:   ₹{results['total_return']:,.2f} ({results['total_return_pct']:+.2f}%)")
        
        print(f"\n📊 Trading Stats:")
        print(f"  Total Trades:    {results['total_trades']}")
        print(f"  Winning Trades:  {results['winning_trades']}")
        print(f"  Losing Trades:   {results['losing_trades']}")
        print(f"  Win Rate:        {results['win_rate']:.1f}%")
        print(f"  Avg Profit/Loss: ₹{results['avg_profit']:,.2f}")
        print(f"  Best Trade:      {results['best_trade']:+.2f}%")
        print(f"  Worst Trade:     {results['worst_trade']:+.2f}%")
        print(f"  Still Holding:   {results['still_holding']} positions")
        
        print("\n" + "="*80)
    
    def export_trades_to_csv(self, filename: str = "data/backtest_trades.csv"):
        """Export trade history to CSV"""
        if not self.trades:
            print("No trades to export")
            return
        
        df = pd.DataFrame(self.trades)
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(self.trades)} trades to {filename}")

if __name__ == "__main__":
    # Test backtest
    symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    
    # Backtest last 6 months
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    backtester = PortfolioBacktester(initial_capital=100000)
    results = backtester.backtest_strategy(symbols, start_date, end_date)
    backtester.print_results(results)
    
    # Export trades
    backtester.export_trades_to_csv()
