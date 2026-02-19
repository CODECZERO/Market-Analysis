#!/usr/bin/env python3
"""
Advanced Stock Analysis Dashboard - Multi-Stock CLI
Features: Portfolio view, Stock screener, Table layouts, Smart recommendations
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from rich.prompt import Prompt

console = Console()

# Top Indian stocks to analyze
TOP_STOCKS = [
    "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS",
    "BAJFINANCE.NS", "WIPRO.NS", "HCLTECH.NS", "ULTRACEMCO.NS", "NESTLEIND.NS"
]

def calculate_hold_recommendation(symbol, hist):
    """Calculate how long to hold and when to sell"""
    close = hist['Close']
    current_price = close.iloc[-1]
    
    # Calculate technical indicators
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else current_price
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_val = rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50
    
    # Calculate trend strength
    trend = close.pct_change().mean()
    volatility = close.pct_change().std()
    
    # Determine action
    if current_price > sma_20 > sma_50 and rsi_val < 70:
        action = "BUY"
        hold_days = "14-30 days"
        target = current_price * 1.05
        stop_loss = current_price * 0.97
        reason = "Strong uptrend, good entry"
    elif current_price < sma_20 < sma_50 and rsi_val > 30:
        action = "SELL"
        hold_days = "Exit now"
        target = current_price * 0.95
        stop_loss = current_price * 0.98
        reason = "Downtrend detected"
    elif rsi_val > 70:
        action = "SELL"
        hold_days = "Take profit now"
        target = current_price
        stop_loss = current_price * 0.97
        reason = "Overbought - book profits"
    elif rsi_val < 30:
        action = "BUY"
        hold_days = "30-60 days"
        target = current_price * 1.08
        stop_loss = current_price * 0.95
        reason = "Oversold - value opportunity"
    else:
        action = "HOLD"
        hold_days = "7-14 days"
        target = current_price * 1.03
        stop_loss = current_price * 0.97
        reason = "Wait for clearer signal"
    
    return {
        "action": action,
        "hold_days": hold_days,
        "target": target,
        "stop_loss": stop_loss,
        "reason": reason,
        "rsi": rsi_val,
        "trend_strength": abs(trend) * 100
    }

def fetch_stock_data(symbol):
    """Fetch and analyze single stock"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        if pd.isna(current_price):
            return None
        
        prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
        day_change = ((current_price - prev_close) / prev_close * 100)
        
        # Get recommendation
        rec = calculate_hold_recommendation(symbol, hist)
        
        return {
            "symbol": symbol.replace('.NS', ''),
            "price": current_price,
            "change": day_change,
            "volume": hist['Volume'].iloc[-1],
            **rec
        }
    except:
        return None

def show_portfolio_view(symbols):
    """Display multiple stocks in table format"""
    console.print("\n[bold cyan]📊 PORTFOLIO DASHBOARD[/bold cyan]\n")
    
    table = Table(title="Multi-Stock Analysis", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    
    table.add_column("Symbol", style="cyan", width=12)
    table.add_column("Price (₹)", justify="right", style="green")
    table.add_column("Change %", justify="right")
    table.add_column("Action", justify="center", width=8)
    table.add_column("Hold For", width=12)
    table.add_column("Target ₹", justify="right", style="yellow")
    table.add_column("Stop Loss ₹", justify="right", style="red")
    table.add_column("Reason", width=25)
    
    for symbol in symbols:
        data = fetch_stock_data(symbol)
        if data:
            change_color = "green" if data['change'] >= 0 else "red"
            action_color = "green" if data['action'] == "BUY" else "red" if data['action'] == "SELL" else "yellow"
            
            table.add_row(
                data['symbol'],
                f"{data['price']:,.2f}",
                f"[{change_color}]{data['change']:+.2f}%[/{change_color}]",
                f"[{action_color}]{data['action']}[/{action_color}]",
                data['hold_days'],
                f"{data['target']:,.2f}",
                f"{data['stop_loss']:,.2f}",
                data['reason'][:25]
            )
    
    console.print(table)

def screen_top_stocks():
    """Find top 5 stocks from top 20"""
    console.print("\n[bold yellow]🔍 SCREENING TOP 20 STOCKS...[/bold yellow]\n")
    
    stocks_data = []
    
    with console.status("[bold green]Analyzing stocks...") as status:
        for symbol in TOP_STOCKS:
            data = fetch_stock_data(symbol)
            if data:
                # Calculate score based on multiple factors
                score = 0
                if data['action'] == 'BUY':
                    score += 3
                elif data['action'] == 'HOLD':
                    score += 1
                
                score += (data['change'] / 10)  # Price momentum
                score += ((100 - data['rsi']) / 20) if data['rsi'] > 50 else (data['rsi'] / 20)  # RSI score
                score += data['trend_strength'] * 10  # Trend strength
                
                data['score'] = score
                stocks_data.append(data)
    
    # Sort by score
    top_5 = sorted(stocks_data, key=lambda x: x['score'], reverse=True)[:5]
    
    # Display results
    table = Table(title="🏆 TOP 5 STOCK PICKS", box=box.DOUBLE_EDGE, show_header=True, header_style="bold green")
    
    table.add_column("Rank", justify="center", style="yellow", width=6)
    table.add_column("Symbol", style="cyan", width=12)
    table.add_column("Price ₹", justify="right", style="green")
    table.add_column("Action", justify="center")
    table.add_column("Hold Duration", width=15)
    table.add_column("Target ₹", justify="right")
    table.add_column("Why?", width=30)
    
    for idx, stock in enumerate(top_5, 1):
        action_emoji = "🟢" if stock['action'] == 'BUY' else "🔴" if stock['action'] == 'SELL' else "🟡"
        table.add_row(
            f"#{idx}",
            stock['symbol'],
            f"{stock['price']:,.2f}",
            f"{action_emoji} {stock['action']}",
            stock['hold_days'],
            f"{stock['target']:,.2f}",
            stock['reason']
        )
    
    console.print(table)
    
    # Summary panel
    buy_count = sum(1 for s in top_5 if s['action'] == 'BUY')
    sell_count = sum(1 for s in top_5 if s['action'] == 'SELL')
    hold_count = sum(1 for s in top_5 if s['action'] == 'HOLD')
    
    summary = f"""
[green]BUY signals:[/green] {buy_count}
[red]SELL signals:[/red] {sell_count}
[yellow]HOLD signals:[/yellow] {hold_count}

[bold]Market Sentiment:[/bold] {"Bullish 📈" if buy_count > sell_count else "Bearish 📉" if sell_count > buy_count else "Neutral 〰️"}
    """
    
    console.print(Panel(summary, title="📊 Summary", border_style="cyan"))

def detailed_analysis(symbol):
    """Show detailed single stock analysis"""
    console.print(f"\n[bold cyan]🔍 DETAILED ANALYSIS: {symbol}[/bold cyan]\n")
    
    data = fetch_stock_data(symbol)
    if not data:
        console.print("[red]❌ Unable to fetch data[/red]")
        return
    
    # Main info panel
    info_text = f"""
[bold]Current Price:[/bold] ₹{data['price']:,.2f}
[bold]Day Change:[/bold] {"[green]" if data['change'] >= 0 else "[red]"}{data['change']:+.2f}%{"[/green]" if data['change'] >= 0 else "[/red]"}
[bold]RSI:[/bold] {data['rsi']:.1f}
    """
    console.print(Panel(info_text, title=f"📊 {data['symbol']}", border_style="green"))
    
    # Recommendation table
    rec_table = Table(box=box.SIMPLE, show_header=False, show_edge=False)
    rec_table.add_column("", style="bold cyan")
    rec_table.add_column("", style="white")
    
    action_color = "green" if data['action'] == 'BUY' else "red" if data['action'] == 'SELL' else "yellow"
    
    rec_table.add_row("Action", f"[{action_color}]{data['action']}[/{action_color}]")
    rec_table.add_row("Hold Duration", data['hold_days'])
    rec_table.add_row("Target Price", f"₹{data['target']:,.2f}")
    rec_table.add_row("Stop Loss", f"₹{data['stop_loss']:,.2f}")
    rec_table.add_row("Reason", data['reason'])
    
    console.print(Panel(rec_table, title="💡 Trading Plan", border_style="yellow"))

def interactive_menu():
    """Interactive CLI menu"""
    while True:
        console.print("\n[bold cyan]═" * 40 + "[/bold cyan]")
        console.print("[bold green]📈 SMART STOCK ANALYSIS DASHBOARD[/bold green]")
        console.print("[bold cyan]═" * 40 + "[/bold cyan]\n")
        
        console.print("[1] 📊 Portfolio View (Multiple Stocks)")
        console.print("[2] 🏆 Top 5 Stock Picks (From Top 20)")
        console.print("[3] 🔍 Search & Analyze Single Stock")
        console.print("[4] 🔄 Auto-Refresh Monitor")
        console.print("[5] ❌ Exit\n")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="2")
        
        if choice == "1":
            symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
            show_portfolio_view(symbols)
        elif choice == "2":
            screen_top_stocks()
        elif choice == "3":
            symbol = Prompt.ask("Enter stock symbol (e.g., TCS.NS, RELIANCE.NS)")
            if not symbol.endswith('.NS'):
                symbol += '.NS'
            detailed_analysis(symbol)
        elif choice == "4":
            console.print("[yellow]Starting auto-refresh... (Ctrl+C to stop)[/yellow]")
            import time
            try:
                while True:
                    console.clear()
                    screen_top_stocks()
                    console.print(f"\n[dim]Refreshing in 120 seconds... ({datetime.now().strftime('%H:%M:%S')})[/dim]")
                    time.sleep(120)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped auto-refresh[/yellow]")
        else:
            console.print("[green]✅ Goodbye![/green]")
            break

def main():
    parser = argparse.ArgumentParser(description="Advanced Stock Analysis Dashboard")
    parser.add_argument('--mode', choices=['portfolio', 'screener', 'search', 'interactive'], 
                       default='interactive', help='Operation mode')
    parser.add_argument('--symbol', help='Stock symbol for search mode')
    
    args = parser.parse_args()
    
    if args.mode == 'portfolio':
        symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
        show_portfolio_view(symbols)
    elif args.mode == 'screener':
        screen_top_stocks()
    elif args.mode == 'search' and args.symbol:
        detailed_analysis(args.symbol)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
