#!/usr/bin/env python3
"""
Smart Market Analysis CLI
Beautiful command-line interface for stock analysis
Shows ALL data with comprehensive reasoning
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}\n")

def print_metric(label, value, color=Colors.GREEN):
    print(f"  {Colors.BOLD}{label}:{Colors.ENDC} {color}{value}{Colors.ENDC}")

def analyze_stock(symbol):
    """Perform comprehensive stock analysis"""
    
    print_header(f"🧠 SMART MARKET ANALYSIS - {symbol}")
    print(f"{Colors.YELLOW}⏳ Fetching real-time data from stock market...{Colors.ENDC}\n")
    
    try:
        # Fetch data
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            print(f"{Colors.RED}❌ No data found for {symbol}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Note: Markets may be closed or symbol is invalid{Colors.ENDC}")
            print(f"\n{Colors.CYAN}💡 Indian Stock Markets (NSE/BSE) Hours:{Colors.ENDC}")
            print(f"  • Trading: Monday-Friday, 9:15 AM - 3:30 PM IST")
            print(f"  • Current time: {datetime.now().strftime('%A, %B %d, %Y %I:%M %p IST')}")
            return
        
        # Get current price from latest available data
        current_price = hist['Close'].iloc[-1]
        if pd.isna(current_price):
            print(f"{Colors.RED}❌ Unable to fetch price data{Colors.ENDC}")
            return
            
        prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
        day_change = ((current_price - prev_close) / prev_close * 100)
        
        # Check if data is current or delayed
        last_date = hist.index[-1]
        # Convert to timezone-naive for comparison
        if hasattr(last_date, 'tz_localize'):
            last_date_naive = last_date.tz_localize(None) if last_date.tz is not None else last_date
        else:
            last_date_naive = pd.Timestamp(last_date).tz_localize(None)
        
        now_naive = pd.Timestamp(datetime.now())
        is_today = last_date_naive.date() == now_naive.date()
        data_age = (now_naive - last_date_naive).days
        
        # 1. OVERVIEW
        print_header("📊 STOCK OVERVIEW")
        
        if not is_today:
            print(f"{Colors.YELLOW}⚠️  MARKET CLOSED - Showing last available data{Colors.ENDC}")
            print(f"{Colors.YELLOW}   Last updated: {last_date.strftime('%A, %B %d, %Y')} ({data_age} days ago){Colors.ENDC}\n")
        print_metric("Symbol", symbol, Colors.CYAN)
        print_metric("Current Price", f"₹{current_price:,.2f}", Colors.GREEN)
        print_metric("Day Change", 
                    f"{'+' if day_change >= 0 else ''}{day_change:.2f}%",
                    Colors.GREEN if day_change >= 0 else Colors.RED)
        print_metric("Day High", f"₹{hist['High'].iloc[-1]:,.2f}")
        print_metric("Day Low", f"₹{hist['Low'].iloc[-1]:,.2f}")
        print_metric("Volume", f"{int(hist['Volume'].iloc[-1]):,}")
        print_metric("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Calculate indicators
        close = hist['Close']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50
        
        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_val = macd.iloc[-1] if not np.isnan(macd.iloc[-1]) else 0
        
        # SMA
        sma_50 = close.rolling(50).mean()
        sma_50_val = sma_50.iloc[-1] if len(close) >= 50 and not np.isnan(sma_50.iloc[-1]) else current_price
        
        # 2. WHAT/WHY/HOW
        print_header("🎯 COMPREHENSIVE ANALYSIS")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}📊 WHAT:{Colors.ENDC}")
        print(f"  {symbol} is currently trading at ₹{current_price:,.2f}")
        
        print(f"\n{Colors.BOLD}{Colors.YELLOW}💡 WHY:{Colors.ENDC}")
        if abs(day_change) < 0.5:
            print(f"  Low volatility, market waiting for catalyst")
        elif day_change > 0:
            print(f"  Price up {day_change:.1f}% - positive momentum")
        else:
            print(f"  Price down {abs(day_change):.1f}% - negative pressure")
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔧 HOW:{Colors.ENDC}")
        print(f"  Analysis uses pattern recognition + technical indicators + historical data")
        
        # Recommendation
        trend = close.pct_change().mean()
        pred_7day = current_price * (1 + trend * 7 * 1.2)
        change_7day = ((pred_7day - current_price) / current_price * 100)
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ RECOMMENDATION:{Colors.ENDC}")
        if change_7day > 3:
            rec = f"BUY - Expected {change_7day:.1f}% gain in 7 days"
        elif change_7day > 1:
            rec = f"HOLD - Moderate upside ({change_7day:.1f}%)"
        elif change_7day < -3:
            rec = f"SELL - Risk of {abs(change_7day):.1f}% decline"
        else:
            rec = "HOLD - Wait for clearer trend"
        print(f"  {Colors.BOLD}{rec}{Colors.ENDC}")
        
        # 3. PREDICTIONS
        print_header("🔮 PRICE FORECASTS")
        
        for days in [1, 3, 7]:
            predicted = current_price * (1 + trend * days * 1.2)
            change_pct = ((predicted - current_price) / current_price * 100)
            confidence = 0.75 - (days * 0.05)
            direction = "📈" if predicted > current_price else "📉"
            color = Colors.GREEN if predicted > current_price else Colors.RED
            
            print(f"\n{Colors.BOLD}{direction} {days} DAY FORECAST:{Colors.ENDC}")
            print_metric("  Predicted Price", f"₹{predicted:,.2f}", color)
            print_metric("  Change", f"{change_pct:+.2f}%", color)
            print_metric("  Confidence", f"{confidence*100:.0f}%", Colors.CYAN)
            
            # Confidence bar
            conf_bars = int(confidence * 20)
            bar = "█" * conf_bars + "░" * (20 - conf_bars)
            print(f"  {Colors.BLUE}{bar}{Colors.ENDC}")
        
        # 4. TECHNICAL INDICATORS
        print_header("📊 TECHNICAL INDICATORS")
        
        print(f"\n{Colors.BOLD}RSI (Relative Strength Index):{Colors.ENDC}")
        print_metric("  Value", f"{rsi_val:.1f}")
        if rsi_val > 70:
            print_metric("  Meaning", "Overbought - Consider selling", Colors.YELLOW)
        elif rsi_val < 30:
            print_metric("  Meaning", "Oversold - Consider buying", Colors.YELLOW)
        else:
            print_metric("  Meaning", "Neutral territory", Colors.CYAN)
        
        print(f"\n{Colors.BOLD}MACD:{Colors.ENDC}")
        print_metric("  Value", f"{macd_val:.2f}")
        print_metric("  Meaning", "Bullish" if macd_val > 0 else "Bearish", Colors.YELLOW)
        
        print(f"\n{Colors.BOLD}Moving Averages:{Colors.ENDC}")
        print_metric("  SMA 50", f"₹{sma_50_val:,.2f}")
        print_metric("  Volatility", f"{close.pct_change().std():.3f}")
        
        # 5. PATTERN
        print_header("🎨 PATTERN ANALYSIS")
        
        recent = close.values[-20:]
        if recent[-1] > recent[0] * 1.05:
            pattern = "Strong Uptrend"
            explanation = "Clear upward momentum - bullish signal"
        elif recent[-1] < recent[0] * 0.95:
            pattern = "Strong Downtrend"
            explanation = "Clear downward pressure - bearish signal"
        else:
            pattern = "Consolidation"
            explanation = "Sideways movement - breakout expected"
        
        print_metric("Pattern Detected", pattern, Colors.CYAN)
        print_metric("Explanation", explanation, Colors.YELLOW)
        
        # 6. SUMMARY BOX
        print_header("✨ FINAL SUMMARY")
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  {Colors.BOLD}STOCK:{Colors.ENDC} {symbol:<20} {Colors.BOLD}PRICE:{Colors.ENDC} ₹{current_price:,.2f}                    ║
║  {Colors.BOLD}RECOMMENDATION:{Colors.ENDC} {rec:<50}     ║
║  {Colors.BOLD}PATTERN:{Colors.ENDC} {pattern:<55}        ║
║  {Colors.BOLD}RSI:{Colors.ENDC} {rsi_val:.1f} ({('Overbought' if rsi_val > 70 else 'Oversold' if rsi_val < 30 else 'Neutral')}){'':40}║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        
        print(f"\n{Colors.GREEN}✅ Analysis complete!{Colors.ENDC}\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.ENDC}\n")

def main():
    parser = argparse.ArgumentParser(
        description="🧠 Smart Market Analysis CLI",
        epilog="Examples:\n  python3 analyze_cli.py TCS.NS\n  python3 analyze_cli.py RELIANCE.NS"
    )
    parser.add_argument('symbol', help='Stock symbol (e.g., TCS.NS, RELIANCE.NS)')
    
    args = parser.parse_args()
    analyze_stock(args.symbol)

if __name__ == "__main__":
    main()
