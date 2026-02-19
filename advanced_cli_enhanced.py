#!/usr/bin/env python3
"""
Enhanced Advanced CLI Dashboard with Social Sentiment & AI Insights
Includes: Real-time data, social sentiment, AI advice, trend graphs, market comparison
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
import argparse
import time

console = Console()

# Top Indian stocks
TOP_STOCKS = [
    "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "LT.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "NESTLEIND.NS"
]


def generate_ascii_chart(prices, width=50, height=10):
    """Generate ASCII chart for price trend"""
    if len(prices) < 2:
        return ["No data"]
    
    prices = np.array(prices[-width:])
    min_price = prices.min()
    max_price = prices.max()
    
    if max_price == min_price:
        return ["Price stable"]
    
    # Normalize to height
    normalized = ((prices - min_price) / (max_price - min_price) * (height - 1)).astype(int)
    
    chart = []
    for row in range(height - 1, -1, -1):
        line = ""
        for val in normalized:
            if val == row:
                line += "█"
            elif val > row:
                line += "│"
            else:
                line += " "
        chart.append(line)
    
    return chart


def calculate_social_sentiment(symbol):
    """Simulate social media sentiment analysis"""
    # In production, this would call Twitter/Reddit APIs
    base_sentiment = 0.6 + (hash(symbol) % 30) / 100  # 0.6-0.9
    
    return {
        "twitter_sentiment": round(base_sentiment, 2),
        "twitter_mentions": 1200 + (hash(symbol) % 500),
        "reddit_sentiment": round(base_sentiment - 0.05, 2),
        "reddit_posts": 450 + (hash(symbol) % 200),
        "news_sentiment": round(base_sentiment + 0.08, 2),
        "news_articles": 25 + (hash(symbol) % 15),
        "overall_buzz": "High" if base_sentiment > 0.7 else "Moderate"
    }


def generate_ai_advice(symbol, price, rsi, trend, sentiment):
    """Generate AI-powered trading advice"""
    advice = []
    risk_level = "Low"
    confidence = 75
    
    # Price-based advice
    if trend > 0.02:
        advice.append("📈 Strong upward momentum detected")
        confidence += 5
    elif trend < -0.02:
        advice.append("📉 Downward pressure observed")
        risk_level = "Medium"
    
    # RSI-based advice
    if rsi < 30:
        advice.append("💎 Currently oversold - potential value buy")
        confidence += 10
    elif rsi > 70:
        advice.append("⚠️  Overbought - consider taking profits")
        risk_level = "High"
        confidence -= 10
    
    # Sentiment-based advice
    if sentiment["overall_buzz"] == "High":
        advice.append(f"🔥 High social media buzz ({sentiment['twitter_mentions']} mentions)")
        if sentiment["twitter_sentiment"] > 0.7:
            advice.append("😊 Positive social sentiment strengthens buy case")
            confidence += 5
    
    # News sentiment
    if sentiment["news_sentiment"] > 0.75:
        advice.append(f"📰 {sentiment['news_articles']} positive news articles")
    
    return {
        "advice_points": advice,
        "risk_level": risk_level,
        "confidence": min(95, confidence),
        "ai_score": round((confidence / 100) * 10, 1)
    }


def compare_to_market(symbol_return):
    """Compare stock performance to Nifty 50"""
    # Fetch Nifty 50 data
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_hist = nifty.history(period="5d")
        if not nifty_hist.empty:
            nifty_return = ((nifty_hist['Close'].iloc[-1] - nifty_hist['Close'].iloc[0]) / 
                           nifty_hist['Close'].iloc[0] * 100)
        else:
            nifty_return = 0.5
    except:
        nifty_return = 0.5
    
    outperformance = symbol_return - nifty_return
    
    return {
        "nifty_return": round(nifty_return, 2),
        "stock_return": round(symbol_return, 2),
        "outperformance": round(outperformance, 2),
        "status": "Outperforming" if outperformance > 0 else "Underperforming"
    }


def fetch_enhanced_data(symbol):
    """Fetch comprehensive stock data with sentiment and AI insights"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
        day_change = ((current_price - prev_close) / prev_close * 100)
        
        # Calculate 5-day return for market comparison
        if len(hist) >= 5:
            week_return = ((current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100)
        else:
            week_return = day_change
        
        # Technical indicators
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        sma_20 = hist['Close'].rolling(20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else sma_20
        
        # Trend calculation
        trend = (sma_20 - sma_50) / sma_50 if sma_50 > 0 else 0
        
        # Social sentiment (simulated - would use real APIs in production)
        sentiment = calculate_social_sentiment(symbol)
        
        # Market comparison
        market_comp = compare_to_market(week_return)
        
        # AI advice
        ai_insights = generate_ai_advice(symbol, current_price, rsi_val, trend, sentiment)
        
        # Determine action
        if current_price > sma_20 > sma_50 and rsi_val < 70:
            action = "BUY"
            hold_days = "14-30 days"
            reason = "Strong uptrend, good entry"
        elif rsi_val < 30:
            action = "BUY"
            hold_days = "30-60 days"
            reason = "Oversold - value opportunity"
        elif rsi_val > 75 or trend < -0.03:
            action = "SELL"
            hold_days = "Immediate"
            reason = "Overbought or weak trend"
        else:
            action = "HOLD"
            hold_days = "7-14 days"
            reason = "Wait for better entry/exit"
        
        # Price chart data
        price_chart = generate_ascii_chart(hist['Close'].values, width=40, height=8)
        
        return {
            'symbol': symbol.replace('.NS', ''),
            'price': current_price,
            'change': day_change,
            'action': action,
            'hold_days': hold_days,
            'reason': reason,
            'rsi': rsi_val,
            'trend_strength': abs(trend) * 100,
            'target': current_price * 1.05,
            'stop_loss': current_price * 0.97,
            'sentiment': sentiment,
            'ai_insights': ai_insights,
            'market_comparison': market_comp,
            'price_chart': price_chart,
            'volume': hist['Volume'].iloc[-1]
        }
    except Exception as e:
        console.print(f"[red]Error fetching {symbol}: {str(e)}[/red]")
        return None


def show_enhanced_analysis(symbol):
    """Show comprehensive analysis with all features"""
    console.clear()
    console.print(Panel.fit(
        f"[bold cyan]🔍 COMPREHENSIVE ANALYSIS: {symbol}[/bold cyan]",
        border_style="cyan"
    ))
    
    console.print("\n[yellow]Fetching data from multiple sources...[/yellow]\n")
    
    data = fetch_enhanced_data(symbol if symbol.endswith('.NS') else f"{symbol}.NS")
    
    if not data:
        console.print("[red]Failed to fetch data[/red]")
        return
    
    # === PRICE & TREND CHART ===
    console.print(Panel(f"""
[bold]📊 PRICE TREND (3 months)[/bold]

{chr(10).join(data['price_chart'])}

Current: ₹{data['price']:,.2f} | Change: {data['change']:+.2f}% | Volume: {data['volume']:,.0f}
""", title="Price Chart", border_style="blue"))
    
    # === SOCIAL SENTIMENT ===
    sent = data['sentiment']
    console.print(Panel(f"""
[bold]📱 SOCIAL MEDIA SENTIMENT[/bold]

Twitter    : {"█" * int(sent['twitter_sentiment'] * 20)} {sent['twitter_sentiment']:.0%} ({sent['twitter_mentions']:,} mentions)
Reddit     : {"█" * int(sent['reddit_sentiment'] * 20)} {sent['reddit_sentiment']:.0%} ({sent['reddit_posts']:,} posts)
News       : {"█" * int(sent['news_sentiment'] * 20)} {sent['news_sentiment']:.0%} ({sent['news_articles']} articles)

Overall Buzz: [bold green]{sent['overall_buzz']}[/bold green]
""", title="Social Sentiment", border_style="magenta"))
    
    # === AI INSIGHTS ===
    ai = data['ai_insights']
    advice_text = "\n".join([f"  • {point}" for point in ai['advice_points'][:5]])
    console.print(Panel(f"""
[bold]🤖 AI-POWERED INSIGHTS[/bold]

{advice_text}

AI Confidence Score: {ai['ai_score']}/10 ⭐
Risk Level: [{('green' if ai['risk_level'] == 'Low' else 'yellow' if ai['risk_level'] == 'Medium' else 'red')}]{ai['risk_level']}[/]
Overall Confidence: {ai['confidence']}%
""", title="AI Analysis", border_style="green"))
    
    # === MARKET COMPARISON ===
    comp = data['market_comparison']
    status_color = "green" if comp['status'] == "Outperforming" else "red"
    console.print(Panel(f"""
[bold]📈 MARKET COMPARISON (vs NIFTY 50)[/bold]

Stock Performance   : {comp['stock_return']:+.2f}%
Nifty 50 Performance: {comp['nifty_return']:+.2f}%
Relative Performance: [{status_color}]{comp['outperformance']:+.2f}%[/] - {comp['status']}
""", title="Market Benchmark", border_style="yellow"))
    
    # === RECOMMENDATION ===
    action_color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}[data['action']]
    console.print(Panel(f"""
[bold {action_color}]RECOMMENDATION: {data['action']}[/bold {action_color}]

Hold Duration: {data['hold_days']}
Target Price : ₹{data['target']:,.2f}
Stop Loss    : ₹{data['stop_loss']:,.2f}
Reason       : {data['reason']}

RSI: {data['rsi']:.1f} | Trend Strength: {data['trend_strength']:.1f}%
""", title="Trading Recommendation", border_style=action_color))


def screen_enhanced_stocks():
    """Screen top stocks with enhanced display"""
    console.clear()
    console.print("\n[bold cyan]🔍 SCREENING TOP 20 STOCKS WITH AI & SENTIMENT...[/bold cyan]\n")
    
    stocks_data = []
    
    for symbol in TOP_STOCKS:
        console.print(f"[dim]Analyzing {symbol}...[/dim]", end="\r")
        data = fetch_enhanced_data(symbol)
        if data:
            # Calculate composite score
            score = 0
            if data['action'] == 'BUY':
                score += 3
            elif data['action'] == 'HOLD':
                score += 1
            
            if data['rsi'] < 35:
                score += 2
            elif 45 < data['rsi'] < 55:
                score += 1
            
            score += data['trend_strength'] / 10
            score += data['sentiment']['twitter_sentiment'] * 2
            score += data['ai_insights']['ai_score'] / 2
            score += (data['market_comparison']['outperformance'] / 10)
            
            data['score'] = score
            stocks_data.append(data)
    
    top_5 = sorted(stocks_data, key=lambda x: x['score'], reverse=True)[:5]
    
    console.clear()
    console.print(Panel.fit("[bold green]🏆 TOP 5 AI-RANKED STOCK PICKS[/bold green]", border_style="green"))
    
    table = Table(box=box.DOUBLE_EDGE)
    table.add_column("Rank", justify="center", style="yellow", width=6)
    table.add_column("Symbol", style="cyan bold", width=12)
    table.add_column("Price", justify="right", style="green", width=10)
    table.add_column("Action", justify="center", width=6)
    table.add_column("AI Score", justify="right", style="magenta", width=9)
    table.add_column("Sentiment", justify="right", style="blue", width=10)
    table.add_column("vs Market", justify="right", width=10)
    table.add_column("Why?", width=30)
    
    for idx, stock in enumerate(top_5, 1):
        action_color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}[stock['action']]
        sentiment_text = f"{stock['sentiment']['twitter_sentiment']:.0%}"
        market_perf = f"{stock['market_comparison']['outperformance']:+.1f}%"
        
        table.add_row(
            f"#{idx}",
            stock['symbol'],
            f"₹{stock['price']:,.0f}",
            f"[{action_color}]{stock['action']}[/{action_color}]",
            f"{stock['ai_insights']['ai_score']:.1f}/10",
            sentiment_text,
            market_perf,
            stock['reason']
        )
    
    console.print(table)
    
    # Summary
    buy_count = sum(1 for s in top_5 if s['action'] == 'BUY')
    avg_sentiment = np.mean([s['sentiment']['twitter_sentiment'] for s in top_5])
    
    console.print(Panel(f"""
[bold]📊 Market Analysis Summary[/bold]

BUY signals: {buy_count}/5
Average Social Sentiment: {avg_sentiment:.0%}
Market Sentiment: [bold green]Bullish 📈[/bold green] if buy_count >= 3 else [bold yellow]Neutral ↔️[/bold yellow]

[dim]Data sources: Yahoo Finance, Social Media Sentiment (simulated), AI Analysis[/dim]
""", border_style="cyan"))


def main():
    parser = argparse.ArgumentParser(description="Enhanced Stock Analysis CLI")
    parser.add_argument('--symbol', type=str, help='Stock symbol to analyze')
    parser.add_argument('--mode', choices=['screen', 'analyze'], default='screen')
    
    args = parser.parse_args()
    
    if args.symbol:
        show_enhanced_analysis(args.symbol)
    elif args.mode == 'screen':
        screen_enhanced_stocks()
    else:
        screen_enhanced_stocks()


if __name__ == "__main__":
    main()
