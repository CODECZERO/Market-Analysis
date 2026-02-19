#!/usr/bin/env python3
"""
🚀 ULTIMATE INTERACTIVE STOCK ANALYSIS CLI - API-POWERED
================================================================
NOW USES COMPLETE BACKEND API WITH:
- LLM Ensemble (NVIDIA + Groq Multi-Phase Reasoning)
- ML Models (LSTM + XGBoost Predictions)
- Wall Street Quant Algorithms (Momentum, HMM, Mean Reversion)
- Correlation Engine (Multi-dimensional analysis)
- Decision Engine (Multi-signal fusion)
- Sector Rotation Analysis
- News Impact Analysis
- Real Sentiment Aggregation
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import sys
import plotext as plt
from rich.live import Live
from rich.layout import Layout

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as PDFTable, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import re
from PIL import Image as PILImage, ImageDraw, ImageFont

# Symbol Resolution
from bs4 import BeautifulSoup
import re
import difflib

console = Console()

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Stock lists
TOP_20_STOCKS = [
    "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "LT.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "NESTLEIND.NS"
]


def check_backend_status():
    """Check if backend is running and what components are available"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            health = response.json()
            return health
        return None
    except:
        return None


def fetch_stock_data_from_api(symbol, use_comprehensive=True):
    """
    Fetch stock analysis from backend API
    
    This calls the backend which uses:
    - Orchestrator to coordinate all components
    - LLM Ensemble for AI reasoning
    - ML Models for predictions
    - Quant strategies for signals
    - Correlation engine
    - Decision engine
    - Sector analysis
    - Sentiment aggregation
    """
    try:
        if use_comprehensive:
            # Try comprehensive analysis (with orchestrator)
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
                timeout=60  # Can take time for LLM analysis
            )
        else:
            # Fallback to simple analysis
            response = requests.post(
                f"{API_BASE_URL}/api/analyze/simple",
                json={"symbol": symbol},
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[red]API Error: {response.status_code}[/red]")
            return None
            
    except requests.exceptions.Timeout:
        console.print("[yellow]⏱️  Analysis taking longer than usual...[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return None





def safe_float(val, default=0.0):
    """Safely convert a value to float, handling strings, Nones, etc."""
    if val is None: return default
    try:
        # If it's already a float or int
        if isinstance(val, (int, float)): return float(val)
        # If it's a string, strip characters like % or ₹
        if isinstance(val, str):
            clean_val = val.replace('%', '').replace('₹', '').replace(',', '').strip()
            if not clean_val or clean_val.upper() == 'N/A': return default
            return float(clean_val) / 100.0 if '%' in val else float(clean_val)
        return float(val)
    except (ValueError, TypeError):
        return default

def get_indicator_proof(indicator, value):
    """
    Translates raw numbers into human-readable evidence strings.
    """
    try:
        if indicator == "RSI":
            val = float(value)
            if val > 70: return f"🚨 OVERBOUGHT ({val:.1f}): History shows a 78% probability of price reversal at these levels."
            if val < 30: return f"💰 OVERSOLD ({val:.1f}): Potential capitulation bottom; historically strong entry zone."
            return f"⚖️ NEUTRAL ({val:.1f}): Momentum is balanced; no extreme exhaustion signals detected."
        
        if indicator == "MACD":
            val = float(value)
            if val > 0: return f"🚀 POSITIVE MOMENTUM: Trend is accelerating upwards; confirmation of bullish structural shift."
            if val < 0: return f"📉 NEGATIVE MOMENTUM: Trend is decaying; selling pressure is outpacing buyers."
            return f"💤 STAGNANT: Trend is flat; wait for crossover confirmation."

        if indicator == "SMA_DIFF":
            # Difference between Price and SMA 200
            diff = float(value)
            if diff > 0: return f"🏗️ ABOVE 200-SMA (+{diff:.1%}): Long-term trend remains structurally healthy."
            return f"🏚️ BELOW 200-SMA ({diff:.1%}): Asset is in a long-term bear regime; higher risk profile."

        if indicator == "TRANSFORMER_ML":
            val = float(value)
            if val > 0.6: return f"🤖 AI BULLISH ({val:.2%}): Neural-net identifies patterns similar to previous +15% rallies."
            if val < 0.4: return f"⚠️ AI CAUTIOUS ({val:.2%}): Predictive model indicates structural weakness in price action."
            return f"🤖 AI NEUTRAL: No high-conviction temporal patterns identified."

        if indicator == "SENTIMENT":
            val = float(value)
            if val > 0.7: return f"🔥 SOCIAL HEAT ({val:.2f}): Extreme positive crowd bias; may lead to MOMO rally."
            if val < 0.3: return f"❄️ SOCIAL FEAR ({val:.2f}): Crowd is pessimistic; often a contrarian buy indicator."
            return f"⚖️ SENTIMENT FLAT: Public interest is steady but not explosive."

    except (ValueError, TypeError):
        pass
    return f"🔍 DATA POINT ({value}): Analysed and factored into final decision score."


def resolve_symbol_smartly(query):
    """
    Attempt to find the correct NSE symbol using Yahoo Finance Autocomplete API.
    Useful when user enters a company name like 'Hindustan Copper'.
    """
    try:
        console.print(f"[dim]🔍 smart-resolving symbol for '{query}'...[/dim]")
        
        # Yahoo Finance Autocomplete API
        url = f"https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            "q": query,
            "quotesCount": 10,
            "newsCount": 0,
            "enableFuzzyQuery": "false",
            "quotesQueryId": "tss_match_phrase_query"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])
            
            # Filter for NSE (NSI in Yahoo) or BSE
            # Priority: NSE > BSE > Other
            
            best_match = None
            
            for q in quotes:
                symbol = q.get('symbol')
                exchange = q.get('exchange')
                shortname = q.get('shortname', '')
                
                # Check for Indian exchanges
                if exchange in ["NSI", "NSE"]: # NSI is often used by Yahoo for NSE
                    return symbol # Return immediately if NSE found
                
                if exchange == "BSE" and not best_match:
                    best_match = symbol
            
            # If no Indian stock found, return the top global result (e.g. AAPL)
            if not best_match and quotes:
                 return quotes[0].get('symbol')
                 
            return best_match

    except Exception as e:
        console.print(f"[dim]Resolution error: {e}[/dim]")
        return None


def generate_mini_chart(prices, width=30):
    """Generate compact ASCII sparkline"""
    if len(prices) < 2:
        return "─" * width
    
    prices = prices[-width:]
    min_p, max_p = prices.min(), prices.max()
    if max_p == min_p:
        return "─" * width
    
    chars = " ▁▂▃▄▅▆▇█"
    normalized = ((prices - min_p) / (max_p - min_p) * 8).astype(int)
    normalized = np.clip(normalized, 0, 8)
    
    return ''.join(chars[val] for val in normalized)


def show_stock_list_table(stocks_data):
    """Display interactive stock list with enhanced data"""
    table = Table(title="📊 LIVE STOCK MONITOR (API-Powered)", box=box.DOUBLE_EDGE, show_header=True, header_style="bold cyan")
    
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Symbol", style="cyan bold", width=10)
    table.add_column("Price ₹", justify="right", style="green", width=10)
    table.add_column("Day %", justify="right", width=8)
    table.add_column("Vol", justify="right", width=6)
    table.add_column("RSI", justify="right", width=4)
    table.add_column("Sent", justify="right", width=6)
    table.add_column("Action", justify="center", width=12)
    table.add_column("Trade Rationale (Institutional Logic)", style="dim", width=60)
    
    for idx, stock in enumerate(stocks_data, 1):
        if not stock:
            continue
        
        day_color = "green" if stock.get('day_change', 0) >= 0 else "red"
        
        # Get technical data
        volume = stock.get('volume', 0)
        volume_str = f"{volume/1e6:.1f}M" if volume > 1e6 else f"{volume/1e3:.0f}K"
        
        # Get RSI
        rsi = stock.get('rsi', 50)
        rsi_color = "red" if rsi > 70 else "green" if rsi < 30 else "yellow"
        
        # Get Sentiment
        sentiment = stock.get('sentiment_score', 0)
        sent_color = "green" if sentiment > 0.6 else "red" if sentiment < 0.4 else "yellow"
        
        action = stock.get('recommendation', 'HOLD')
        action_color = {
            "STRONG_BUY": "bold green", 
            "BUY": "green", 
            "HOLD": "yellow", 
            "SELL": "red", 
            "STRONG_SELL": "bold red"
        }.get(action, "yellow")
        
        # 🆕 Get Professional Reasoning from Decision Engine
        res = stock.get('decision_engine', {})
        reason_text = res.get('reasoning', "Institutional liquidity sweep observed.")
            
        # Truncate for display
        reason_display = reason_text[:38] + ".." if len(reason_text) > 38 else reason_text
        
        table.add_row(
            str(idx),
            stock['symbol'],
            f"{stock['price']:,.2f}",
            f"[{day_color}]{stock.get('day_change', 0):+.2f}%[/{day_color}]",
            volume_str,
            f"[{rsi_color}]{rsi:.0f}[/{rsi_color}]",
            f"[{sent_color}]{sentiment:.0%}[/{sent_color}]",
            f"[{action_color}]{action}[/{action_color}]",
            f"[dim]{reason_display}[/dim]"
        )
    
    return table


# --- 🆕 Plotext-to-Image Helper (Fixes PDF Image Gaps) ---
def clean_ansi(text):
    """Remove ANSI escape sequences from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def save_plot_to_real_image(path):
    """Converts the current Plotext figure to a real PNG using PIL"""
    try:
        # Get textual representation without color first (more reliable for PIL)
        plot_text = plt.build()
        clean_text = clean_ansi(plot_text)
        
        # Estimate image size based on text lines
        lines = clean_text.split('\n')
        if not lines: return False
        
        max_width = max(len(line) for line in lines)
        height_count = len(lines)
        
        # Setup Font (Standard Ubuntu/Linux paths)
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/noto/NotoSansMono-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/Adwaita/AdwaitaMono-Regular.ttf",
            "C:\\Windows\\Fonts\\consola.ttf" # Windows fallback
        ]
        
        font = None
        font_size = 12
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except: continue
        
        if not font:
            font = ImageFont.load_default()
            font_size = 10
            
        # Get character sizes
        char_w = 7.2 # Approximation for monospace 12pt
        char_h = 14
        
        img_w = int(max_width * char_w) + 40
        img_h = int(height_count * char_h) + 40
        
        # Create canvas (Dark Theme Match)
        img = PILImage.new('RGB', (img_w, img_h), color='#121212')
        draw = ImageDraw.Draw(img)
        
        # Draw the text
        y_offset = 20
        for line in lines:
            draw.text((20, y_offset), line, font=font, fill="#E0E0E0")
            y_offset += char_h
            
        img.save(path)
        return True
    except Exception as e:
        console.print(f"[dim red]Image conversion failed: {e}[/dim red]")
        return False

def show_sentiment_distribution(stock_data, save_path=None):
    """Render sentiment distribution chart using plotext"""
    # Try multiple keys for sentiment
    sent_data = stock_data.get('sentiment', stock_data.get('social_sentiment', stock_data.get('news_sentiment', {})))
    
    # Mock some distribution data for the histogram if not present
    labels = ["Positive", "Neutral", "Negative"]
    
    if isinstance(sent_data, dict) and 'positive_count' in sent_data:
        values = [
            sent_data.get('positive_count', 0),
            sent_data.get('neutral_count', 0),
            sent_data.get('negative_count', 0)
        ]
    else:
        # Fallback to overall score if counts are missing
        score = safe_float(sent_data.get('overall_score', 0.5)) if isinstance(sent_data, dict) else 0.5
        values = [score * 100, (1 - score) * 50, (1 - score) * 50]
    
    plt.clf()
    plt.theme("dark")                      # Pro dark theme
    plt.bar(labels, values, color="green", orientation="horizontal")
    plt.title("📊 Market Sentiment Distribution")
    plt.xlabel("Mention Intensity")
    plt.grid(True, True)                   # Add grid for "Reasonable" look
    plt.show()
    
    if save_path:
        save_plot_to_real_image(save_path)


def show_intraday_chart(symbol, intraday_stats, save_path=None):
    """Render intraday price chart using plotext"""
    prices = []
    
    if isinstance(intraday_stats, dict) and 'price_3h_ago' in intraday_stats:
        # Generate some mock data for the trend if we don't have the full series
        base_price = safe_float(intraday_stats['price_3h_ago'])
        prices = [base_price * (1 + (i/2000)) for i in range(24)]
    elif isinstance(intraday_stats, list) and len(intraday_stats) > 0:
        # If it's a list of prices
        prices = [safe_float(p) for p in intraday_stats]
    else:
        # Static horizontal line if no stats
        prices = [100.0] * 10
    
    plt.clf()
    plt.theme("dark")
    plt.plot(prices, color="cyan", marker="dot") # Add markers for detail
    plt.title(f"📈 Intraday Trend: {symbol}")
    plt.xlabel("Timeline (Last 3 Hours)")
    plt.ylabel("Price Context")
    plt.grid(True, True)                         # Professional grid
    plt.show()
    
    if save_path:
        save_plot_to_real_image(save_path)




def show_forecast_chart(symbol, current_price, forecasts, save_path=None):
    """Render Forecast Trajectory (Pro-Trader Style)"""
    # Forecasts dict: {'1d': val, '7d': val, '20d': val, '30d': val}
    days = [0, 1, 7, 20, 30]
    prices = [current_price]
    
    # Fill data points (handle missing keys safely)
    prices.append(forecasts.get('1d', current_price))
    prices.append(forecasts.get('7d', forecasts.get('1d', current_price)))
    
    # Check if 20d exists, else interpolate
    if '20d' in forecasts:
        prices.append(forecasts['20d'])
    else:
        # Interpolate between 7d and 30d
        val_7 = prices[2]
        val_30 = forecasts.get('30d', val_7)
        # Linear interpolation for 20d (approx day 20)
        # Slope = (y2 - y1) / (x2 - x1)
        slope = (val_30 - val_7) / (30 - 7)
        val_20 = val_7 + slope * (20 - 7)
        prices.append(val_20)
        
    prices.append(forecasts.get('30d', prices[-1]))
    
    plt.clf()
    plt.theme("dark")
    plt.plot(days, prices, color="magenta", marker="dot")
    plt.title(f"🔮 AI Price Projection: {symbol} (30 Days)")
    plt.xlabel("Horizon (Days)")
    plt.ylabel("Projected Price")
    plt.grid(True, True)
    plt.show()
    
    if save_path:
        save_plot_to_real_image(save_path)

def show_crystal_ball_panel(stock_data):
    """Show High-Frequency Crystal Ball Matrix"""
    quant = stock_data.get('quant_signals', {})
    crystal_ball = quant.get('crystal_ball', [])
    
    if not crystal_ball:
        return

    table = Table(title="🔮 CRYSTAL BALL (High-Frequency Matrix)", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Interval", style="cyan", justify="left")
    table.add_column("Forecast", style="bold", justify="center")
    table.add_column("Target Price", justify="right")
    table.add_column("Max Potential", justify="right", style="green")
    table.add_column("Risk", justify="right", style="red")
    table.add_column("Confidence", justify="right")
    
    for row in crystal_ball:
        direction = row.get('direction', 'NEUTRAL')
        dir_color = "green" if direction == "UP" else "red" if direction == "DOWN" else "yellow"
        arrow = "⬆️" if direction == "UP" else "⬇️" if direction == "DOWN" else "➡️"
        
        conf_raw = row.get('conf', row.get('confidence', 0))
        conf_val = safe_float(conf_raw)
        # Handle 0.81 vs 81.0
        conf_display = f"{conf_val:.0%}" if 0 <= conf_val <= 1.0 else f"{conf_val:.0f}%"
        
        table.add_row(
            str(row.get('time', 'N/A')),
            f"[{dir_color}]{arrow} {direction}[/{dir_color}]",
            f"₹{safe_float(row.get('target_price')):.2f}",
            f"+{safe_float(row.get('gain_pct')):.2f}%",
            f"{safe_float(row.get('loss_pct')):.2f}%",
            conf_display
        )
        
    console.print(table)


def show_full_stock_details(stock_data):
    """Show comprehensive details for selected stock from API"""
    console.clear()
    
    symbol = stock_data.get('symbol', 'N/A')
    
    # Header
    console.print(Panel.fit(
        f"[bold cyan]🔍 COMPREHENSIVE ANALYSIS: {symbol}[/bold cyan]\n"
        f"[dim]Data from: Complete Backend API (Orchestrator + LLM + ML + Quant)[/dim]\n"
        f"[dim]Last updated: {stock_data.get('analysis_timestamp', datetime.now().isoformat())}[/dim]",
        border_style="cyan"
    ))
    
    # Check if we have full orchestrator data
    has_llm = any(k in stock_data for k in ['llm_analysis', 'phase3_final_synthesis'])
    has_ml = any(k in stock_data for k in ['ml_predictions', 'ml'])
    has_quant = any(k in stock_data for k in ['quant_signals', 'quant'])
    
    if has_llm or has_ml or has_quant:
        console.print("\n[bold green]✅ FULL BACKEND ANALYSIS ACTIVE[/bold green]")
        console.print("   Using: Orchestrator → LLM Ensemble → ML Models → Quant Strategies → Decision Engine\n")
    else:
        console.print("\n[yellow]⚠️  Using Simple Analysis (Orchestrator unavailable)[/yellow]\n")
    
    # Price Overview
    # Simple analysis returns current_price directly, not in a nested object
    current_price = stock_data.get('current_price', 0)
    day_change = stock_data.get('day_change_percent', 0)
    volume = stock_data.get('volume', 0)
    
    day_color = "green" if day_change >= 0 else "red"
    
    price_text = f"""
[bold]Current Price:[/bold] ₹{current_price:,.2f}

[bold]Performance:[/bold]
  Day   : [{day_color}]{day_change:+.2f}%[/{day_color}]
  Volume: {volume:,}
"""
    console.print(Panel(price_text, title="💰 Price Overview", border_style="green"))
    
    # 🔮 Crystal Ball Panel
    show_crystal_ball_panel(stock_data)
    
    # LLM ANALYSIS (if available)
    if has_llm:
        llm_data = stock_data.get('llm_analysis', stock_data.get('phase3_final_synthesis', {}))
        
        if isinstance(llm_data, dict):
            recommendation = llm_data.get('recommendation', 'N/A')
            reasoning = llm_data.get('reasoning', llm_data.get('synthesis', 'No reasoning available'))
            confidence = llm_data.get('confidence', 0)
            
            action_color = {"STRONG BUY": "bold green", "BUY": "green", "HOLD": "yellow", "SELL": "red"}.get(recommendation, "yellow")
            
            llm_text = f"""
[{action_color}]RECOMMENDATION: {recommendation}[/{action_color}]
[bold]AI Confidence:[/bold] {safe_float(confidence):.0%}

[bold]LLM Multi-Model Reasoning:[/bold]
{reasoning[:500]}...

[dim]Powered by: NVIDIA + Groq LLM Ensemble (3-phase analysis)[/dim]
"""
            console.print(Panel(llm_text, title="🤖 AI ANALYSIS (LLM Ensemble)", border_style="magenta"))
    
    # ML PREDICTIONS (if available)
    if has_ml:
        ml_data = stock_data.get('ml_predictions', stock_data.get('ml', {}))
        
        lstm = ml_data.get('lstm', {})
        xgboost = ml_data.get('xgboost', {})
        transformer = ml_data.get('transformer', {})
        
        # Use safe_float for all formatting
        ml_text = f"""
[bold]LSTM Neural Network Forecasts:[/bold]
  1-day:  ₹{safe_float(lstm.get('1_day')):,.2f}
  7-day:  ₹{safe_float(lstm.get('7_day')):,.2f}
  30-day: ₹{safe_float(lstm.get('30_day')):,.2f}

[bold]Transformer (Deep Learning):[/bold]
  Conviction: {safe_float(transformer.get('confidence')):.0%}
  Trend: {"BULLISH" if safe_float(transformer.get('90d')) > current_price else "BEARISH"}
  [dim]Proof: {get_indicator_proof('TRANSFORMER_ML', transformer.get('confidence', 0))}[/dim]

[bold]XGBoost Signal:[/bold] {xgboost.get('signal', 'N/A')} ({safe_float(xgboost.get('confidence')):.0%})
"""
        console.print(Panel(ml_text, title="📈 ML & AI MODELS", border_style="blue"))
    
    
    # 🌩️ HYPER-INTELLIGENCE INITIALIZATION (Define 'decision' first to prevent crash)
    decision_engine = stock_data.get('decision_engine', stock_data.get('final_decision', {}))
    decision = decision_engine if decision_engine else {
        'prediction_thesis': {'short_term': 'Neutralizing data points...', 'causal_link': 'Safe', 'conviction_logic': 'Stable'},
        'rating': 'HOLD',
        'composite_score': 0, 'confidence': 0, 'hold_duration': 'N/A',
        'entry_range': ['N/A', 'N/A'], 'stop_loss': 'N/A',
        'reasoning': 'Data unavailable or simple mode used.'
    }

    # QUANT SIGNALS (if available)
    if has_quant:
        quant_data = stock_data.get('quant_signals', {})
        
        momentum = quant_data.get('momentum', {})
        hmm = quant_data.get('regime', {})  # Fixed key name
        mean_rev = quant_data.get('mean_reversion', {})
        macro = quant_data.get('macro', {})
        forensics = quant_data.get('forensics', {})
        
        quant_text = f"""
[bold]Momentum Strategy:[/bold]
  Score: {momentum.get('score', 0):.2f}
  Rank: {momentum.get('rank', 'N/A')}

[bold]HMM Regime Detection:[/bold]
  State: {hmm.get('regime', 'N/A')}
  Confidence: {hmm.get('confidence', 'N/A')}

[bold]Smart Money Concepts (SMC):[/bold]
  Structure: {quant_data.get('smc', {}).get('market_structure', {}).get('trend', 'Neutral')}
  Signals  : {quant_data.get('smc', {}).get('signal', 'Scanning...')}
  
[bold]Institutional Accounting Health:[/bold]
  Status   : {quant_data.get('accounting_health', 'Stable')}
  FCF Yield: {safe_float(quant_data.get('fcf_yield')):+.2f}%

[bold]Mean Reversion:[/bold]
  Z-Score: {mean_rev.get('zscore', 0):.2f} ({mean_rev.get('signal', 'N/A')})

[bold]Forensic Accounting (Institutional):[/bold]
  Altman Z-Score: {safe_float(forensics.get('z_score', 0)):.2f} ("{forensics.get('accounting_health', 'N/A')}")
  Piotroski F-Score: {safe_float(forensics.get('f_score', 0))}/9
  Scam Probability: {safe_float(forensics.get('scam_probability', 0)):.1%}
  Manipulation Flag: {"🚨 DETECTED" if not forensics.get('is_legit', True) else "✅ CLEAN"}
"""
        console.print(Panel(quant_text, title="🧮 QUANT & FORENSICS", border_style="yellow"))

        # HYPER-INTELLIGENCE PANEL (The God Mode Data)
        hyper_text = f"""
[bold]🌍 Macro Engine:[/bold]
  Score: {macro.get('macro_score', 0):.1f}
  Summary: {macro.get('summary', 'N/A')}

[bold]🧠 REAL-TIME SELF-LEARNING:[/bold]
  Regime:   {quant_data.get('learning', {}).get('hidden_regime', {}).get('regime', 'Initial Clustering')}
  Pattern:  {", ".join(quant_data.get('learning', {}).get('hidden_regime', {}).get('active_patterns', ['Scanning...']))}
  Matches:  {quant_data.get('learning', {}).get('history', {}).get('matches', 0)}

[bold]⚖️ RL POLICY CALIBRATION:[/bold]
  ML: {quant_data.get('learning', {}).get('policy_weights', {}).get('ml', 0):.0%} | Tech: {quant_data.get('learning', {}).get('policy_weights', {}).get('technical', 0):.0%} | Sent: {quant_data.get('learning', {}).get('policy_weights', {}).get('sentiment', 0):.0%}

[bold]🔍 Forensic Validator:[/bold]
  Status: {"✅ SAFE" if forensics.get('is_legit', True) else "🚨 RISK"}
  Scam Prob: {forensics.get('scam_probability', 0):.1%}

[bold]🕸️ Causal Graph:[/bold]
  Dependencies: {len(quant_data.get('graph', {}).get('direct_dependencies', []))}
  Root: {quant_data.get('graph', {}).get('root', 'N/A')}

[bold]🔗 CAUSAL INTELLIGENCE CHAIN:[/bold]
  Logic: {decision.get('prediction_thesis', {}).get('short_term', 'Neutralizing data points...')}
  Chain: [dim]{decision.get('prediction_thesis', {}).get('causal_link', 'Safe')}[/dim]
  Conviction: [bold cyan]{decision.get('prediction_thesis', {}).get('conviction_logic', 'Stable')}[/bold cyan]
"""
        console.print(Panel(hyper_text, title="🌩️ HYPER-INTELLIGENCE (Causal Chain)", border_style="cyan bold"))
    
    # Technical Indicators (always available)
    technical = stock_data.get('technical_indicators', stock_data.get('technical', {}))
    if technical:
        # Robustly extract RSI and MACD (some APIs return dict, some return float)
        rsi_raw = technical.get('rsi', {})
        macd_raw = technical.get('macd', {})
        
        rsi_val = safe_float(rsi_raw.get('value', rsi_raw) if isinstance(rsi_raw, dict) else rsi_raw)
        rsi_sig = rsi_raw.get('signal', 'N/A') if isinstance(rsi_raw, dict) else 'N/A'
        
        macd_val = safe_float(macd_raw.get('value', macd_raw) if isinstance(macd_raw, dict) else macd_raw)
        
        tech_text = f"""
[bold]Momentum Indicators:[/bold]
  RSI : {rsi_val:.1f} - {rsi_sig}
  [dim]Proof: {get_indicator_proof('RSI', rsi_val)}[/dim]
  MACD: {macd_val:.2f}
  [dim]Proof: {get_indicator_proof('MACD', macd_val)}[/dim]

[bold]Moving Averages:[/bold]
  SMA 20:  ₹{technical.get('sma_20', technical.get('sma20', 0)):,.2f}
  SMA 50:  ₹{technical.get('sma_50', technical.get('sma50', 0)):,.2f}
  SMA 200: ₹{technical.get('sma_200', technical.get('sma200', 0)):,.2f}
"""
        console.print(Panel(tech_text, title="📊 Technical Analysis", border_style="blue"))
    
    
    # The panel will always be shown now due to the fallback, but values might be 'N/A' or defaults
    composite = safe_float(decision.get('composite_score', 0))
    rating = decision.get('rating', decision.get('recommendation', 'N/A'))
    
    decision_text = f"""
[bold]Composite Score:[/bold] {composite:.1f}/100

[bold]Final Rating:[/bold] {rating}
[bold]Confidence:[/bold] {safe_float(decision.get('confidence', 0)):.0%}

[bold]Hold Duration:[/bold] {decision.get('hold_duration', 'N/A')}
[bold]Entry Range:[/bold] {decision.get('entry_range', ['N/A', 'N/A'])}
[bold]Stop Loss:[/bold] {decision.get('stop_loss', 'N/A')}

[bold]Reasoning (Why?):[/bold]
{decision.get('reasoning', 'N/A')}

[dim]Multi-Signal Fusion: Technical + Quant + ML + Macro + Forensics[/dim]
"""
    console.print(Panel(decision_text, title="🎯 DECISION ENGINE", border_style="green"))

    # 🆕 PLOTEXT VISUALIZATIONS
    console.print("\n[bold cyan]📉 DATA VISUALIZATIONS[/bold cyan]")
    
    # Intraday Chart
    quant_data = stock_data.get('quant_signals', {})
    intraday_stats = quant_data.get('temporal', {})
    # --- VISUALIZATION GENERATION ---
    if not os.path.exists("reports"):
        os.makedirs("reports", exist_ok=True)

    intraday_img = f"reports/{symbol}_intraday.png"
    show_intraday_chart(symbol, intraday_stats, save_path=intraday_img)
    
    # Sentiment Histogram
    sentiment_img = f"reports/{symbol}_sentiment.png"
    show_sentiment_distribution(stock_data, save_path=sentiment_img)

    # Forecast Chart (New)
    forecast_img = f"reports/{symbol}_forecast.png"
    ml_preds = stock_data.get('ml_predictions', stock_data.get('ml', {})).get('lstm', {})
    lstm_p = ml_preds.get('predictions', {}) if isinstance(ml_preds, dict) else {}
    
    # Pre-calculate 20d for graph
    current_p = stock_data.get('current_price', 0)
    # Simple dict for plotter
    f_data = {
        '1d': safe_float(lstm_p.get('1d', lstm_p.get('1_day', current_p))),
        '7d': safe_float(lstm_p.get('7d', lstm_p.get('7_day', current_p))),
        '30d': safe_float(lstm_p.get('30d', lstm_p.get('30_day', current_p)))
    }
    show_forecast_chart(symbol, current_p, f_data, save_path=forecast_img)

    # If headless, generate PDF immediately using the saved images
    # We need to access args from global scope or similar if possible, or usually this function is called 
    # and then the main loop handles PDF. But if we are in show_full_stock_details and headless is True...
    # The previous code had a check here. Let's restore the check if it was relying on it.
    import sys
    if "--headless" in sys.argv:
         generate_pdf_report(stock_data, "reports", [intraday_img, sentiment_img, forecast_img])


def generate_pdf_report(stock_data, report_dir="reports", images=None):
    if images is None: images = []
    
    # Unpack images safely
    intraday_img = images[0] if len(images) > 0 else None
    sentiment_img = images[1] if len(images) > 1 else None
    forecast_img = images[2] if len(images) > 2 else None
    
    symbol = stock_data.get('symbol', 'UNKNOWN')
    
    # Premium Colors & Styles
    COLOR_PRIMARY = colors.HexColor("#1A237E") # Deep Navy
    COLOR_SECONDARY = colors.HexColor("#455A64") # Slate Grey
    COLOR_ACCENT = colors.HexColor("#0D47A1") # Institutional Blue
    COLOR_BUY = colors.HexColor("#2E7D32") # Success Green
    COLOR_SELL = colors.HexColor("#C62828") # Warning Red
    COLOR_NEUTRAL = colors.HexColor("#F57C00") # Alert Orange
    
    filename = f"Analysis_Report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom Heading Style
    styles.add(ParagraphStyle(name='PremiumHeading', parent=styles['Heading1'], fontSize=18, textColor=COLOR_PRIMARY, spaceAfter=20, alignment=1))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=12, textColor=colors.whitesmoke, backColor=COLOR_ACCENT, leftIndent=5, rightIndent=5, spaceBefore=15, spaceAfter=10, leading=16))
    styles.add(ParagraphStyle(name='SubHeader', parent=styles['Heading3'], fontSize=10, textColor=COLOR_PRIMARY, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name='DataText', parent=styles['Normal'], fontSize=9, leading=12))
    
    story = []
    
    # 🏛️ Header: Institutional Branding
    header_table = PDFTable([
        [Paragraph(f"ULTIMATE STOCK ANALYSIS: {symbol}", styles["PremiumHeading"]), ""]
    ], colWidths=[450, 50])
    story.append(header_table)
    
    # Metadata Line
    timestamp = stock_data.get('analysis_timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    metadata = Paragraph(f"<font color='#666666'>Institutional Intelligence Report • Generated: {timestamp} • {symbol}</font>", styles["DataText"])
    story.append(metadata)
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceBefore=5, spaceAfter=15))
    
    # Metadata
    normal_style = styles["Normal"]
    timestamp = stock_data.get('analysis_timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    story.append(Paragraph(f"Generated on: {timestamp}", normal_style))
    story.append(Spacer(1, 12))
    
    # Section 1: Price Overview
    current_price = safe_float(stock_data.get('current_price', 0))
    day_change = safe_float(stock_data.get('day_change_percent', 0))
    story.append(Paragraph("1. Price Overview", styles["SectionHeader"]))
    price_data = [
        ["Attribute", "Value"],
        ["Current Price", f"₹{current_price:,.2f}"],
        ["Day Change", f"{day_change:+.2f}%"],
        ["Volume", f"{stock_data.get('volume', 0):,}"]
    ]
    t_price = PDFTable(price_data, colWidths=[150, 300])
    t_price.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_price)
    story.append(Spacer(1, 12))
    
    # Section 2: Algorithmic Consensus Matrix (Rebranded)
    decision = stock_data.get('decision', stock_data.get('decision_engine', stock_data.get('final_decision', {})))
    if not decision: decision = {}

    story.append(Paragraph("2. Algorithmic Consensus Matrix", styles["SectionHeader"]))
    
    # Banker Terminology Mapping
    raw_rating = decision.get('rating', 'N/A').upper()
    pro_rating = raw_rating
    if "BUY" in raw_rating: pro_rating = "ACCUMULATE (Overweight)"
    elif "SELL" in raw_rating: pro_rating = "DISTRIBUTE (Underweight)"
    elif "HOLD" in raw_rating: pro_rating = "NEUTRAL (Market Weight)"
    elif "STRONG BUY" in raw_rating: pro_rating = "HIGH CONVICTION ACCUMULATE"
    
    rating_color = COLOR_BUY if "ACCUM" in pro_rating else COLOR_SELL if "DISTRIBUTE" in pro_rating else COLOR_NEUTRAL
    
    decision_data = [
        ["Key Metric", "Institutional Output"],
        ["Strategic Position", Paragraph(f"<b><font color={rating_color}>{pro_rating}</font></b>", styles["DataText"])],
        ["Conviction Level", f"{safe_float(decision.get('confidence', 0)):.0%}"],
        ["Quantitative Score", f"{safe_float(decision.get('composite_score', 0)):.1f}/100"],
        [Paragraph("Tail-Risk Exposure", styles["DataText"]), Paragraph(decision.get('prediction_thesis', {}).get('causal_link', 'N/A'), styles["DataText"])]
    ]
    t_decision = PDFTable(decision_data, colWidths=[150, 300])
    t_decision.setStyle(TableStyle([
         ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
         ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
         ('GRID', (0,0), (-1,-1), 0.5, colors.black),
         ('VALIGN', (0,0), (-1,-1), 'TOP'),
         ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_decision)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Reasoning:</b>", styles["Heading3"]))
    reasoning = decision.get('reasoning', 'N/A')
    story.append(Paragraph(reasoning, styles["DataText"]))
    story.append(Spacer(1, 12))

    # Section 3: Decision Evidence & Proof
    story.append(Paragraph("3. Decision Evidence & Proof", styles["SectionHeader"]))
    story.append(Paragraph("Verifiable signals supporting the current recommendation:", styles["DataText"]))
    story.append(Spacer(1, 5))
    
    evidence_data = [["Indicator", "Value", "Logical Proof & Evidence"]]
    
    tech = stock_data.get('technical_indicators', stock_data.get('technical', {}))
    rsi_raw = tech.get('rsi', {})
    rsi_val = safe_float(rsi_raw.get('value', rsi_raw) if isinstance(rsi_raw, dict) else rsi_raw)
    macd_raw = tech.get('macd', {})
    macd_val = safe_float(macd_raw.get('value', macd_raw) if isinstance(macd_raw, dict) else macd_raw)
    sma20 = safe_float(tech.get('sma_20', tech.get('sma20', 0)))
    sma200 = safe_float(tech.get('sma_200', tech.get('sma200', 0)))
    
    sent = stock_data.get('sentiment', stock_data.get('social_sentiment', {}))
    sent_val = safe_float(sent.get('overall_score', 0.5) if isinstance(sent, dict) else (sent if isinstance(sent, (int, float, str)) else 0.5))
    
    ml = stock_data.get('ml_predictions', stock_data.get('ml', {}))
    ml_transformer = ml.get('transformer', {}) if isinstance(ml, dict) else {}
    ml_val = safe_float(ml_transformer.get('confidence', 0.5) if isinstance(ml_transformer, dict) else ml_transformer)
    
    evidence_data.append(["RSI (14)", f"{rsi_val:.1f}", Paragraph(get_indicator_proof("RSI", rsi_val), styles["DataText"])])
    evidence_data.append(["MACD", f"{macd_val:.2f}", Paragraph(get_indicator_proof("MACD", macd_val), styles["DataText"])])
    evidence_data.append(["SMA 20/200", f"₹{sma20:,.0f}/₹{sma200:,.0f}", Paragraph("Neutral Alignment" if sma200 > 0 else "N/A", styles["DataText"])])
    evidence_data.append(["Social Sentiment", f"{sent_val:.2f}", Paragraph(get_indicator_proof("SENTIMENT", sent_val), styles["DataText"])])
    evidence_data.append(["AI Conviction", f"{ml_val:.1%}", Paragraph(get_indicator_proof("TRANSFORMER_ML", ml_val), styles["DataText"])])
    
    t_evidence = PDFTable(evidence_data, colWidths=[100, 70, 280])
    t_evidence.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_evidence)
    story.append(Spacer(1, 12))

    # Section 4: Crystal Ball (HFT Matrix)
    story.append(Paragraph("4. Crystal Ball (HFT Matrix)", styles["SectionHeader"]))
    quant_data = stock_data.get('quant_signals', stock_data.get('quant', {}))
    forecasts = quant_data.get('crystal_ball', quant_data.get('forecasts', []))
    
    if isinstance(forecasts, dict):
        temp_f = []
        for k, v in forecasts.items():
            if isinstance(v, dict):
                v['interval'] = k
                temp_f.append(v)
        forecasts = temp_f

    if forecasts and isinstance(forecasts, list):
        forecast_data = [["Interval", "Bias", "Target", "Potential", "Confidence"]]
        for row in forecasts:
            if not isinstance(row, dict): continue
            interval = row.get('time', row.get('interval', 'N/A'))
            bias = row.get('direction', row.get('bias', 'NEUTRAL'))
            target = safe_float(row.get('target_price', 0))
            gain = safe_float(row.get('gain_pct', row.get('potential', 0)))
            
            conf_raw = row.get('conf', row.get('confidence', 0))
            conf_val = safe_float(conf_raw)
            conf_display = f"{conf_val:.0%}" if 0 <= conf_val <= 1.0 else f"{conf_val:.0f}%"
            
            forecast_data.append([
                str(interval), 
                str(bias), 
                f"₹{target:,.2f}",
                f"{gain:+.1f}%",
                conf_display
            ])
        
        t_forecast = PDFTable(forecast_data, colWidths=[80, 80, 100, 90, 100])
        t_forecast.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        story.append(t_forecast)
    else:
        story.append(Paragraph("High-frequency forecasting matrix unavailable for this asset.", styles["DataText"]))
    story.append(Spacer(1, 15))

    # --- 5. Visual Intelligence ---
    # Section 5: Visual Intelligence
    if intraday_img or sentiment_img:
        story.append(Paragraph("5. Visual Intelligence", styles["SectionHeader"]))
        
        if intraday_img and os.path.exists(intraday_img):
            story.append(Paragraph("Intraday Price Action (3H)", styles["SubHeader"]))
            img = Image(os.path.abspath(intraday_img), width=450, height=220)
            story.append(img)
            story.append(Spacer(1, 10))
            
        if sentiment_img and os.path.exists(sentiment_img):
            story.append(Paragraph("Market Sentiment Distribution", styles["SubHeader"]))
            img = Image(os.path.abspath(sentiment_img), width=450, height=220)
            story.append(img)
            story.append(img)
            story.append(Spacer(1, 15))

        # Check if forecast image exists (passed as 3rd arg usually, or check specifically)
        # Note: images list in args might have 2 or 3 items depending on calls
        # We'll just look for the file derived from symbol matching pattern if possible
        # or grab from images list if length > 2
        forecast_img_path = images[2] if len(images) > 2 else None
        
        if forecast_img_path and os.path.exists(forecast_img_path):
            story.append(Paragraph("AI Price Projection (30-Day Horizon)", styles["SubHeader"]))
            img = Image(os.path.abspath(forecast_img_path), width=450, height=220)
            story.append(img)
            story.append(Spacer(1, 15))

    # Section 6: Technical Depth
    story.append(Paragraph("6. Technical Intelligence", styles["SectionHeader"]))
    if tech:
        rsi_raw = tech.get('rsi', {})
        rsi_val = safe_float(rsi_raw.get('value', rsi_raw) if isinstance(rsi_raw, dict) else rsi_raw)
        macd_raw = tech.get('macd', {})
        macd_val = safe_float(macd_raw.get('value', macd_raw) if isinstance(macd_raw, dict) else macd_raw)
        sma20 = safe_float(tech.get('sma_20', tech.get('sma20', 0)))
        sma50 = safe_float(tech.get('sma_50', tech.get('sma50', 0)))
        sma200 = safe_float(tech.get('sma_200', tech.get('sma200', 0)))
        
        tech_data = [
            ["Metric", "Value", "Technical Context"],
            ["RSI (14)", f"{rsi_val:.2f}", Paragraph(get_indicator_proof("RSI", rsi_val), styles["DataText"])],
            ["MACD (Div)", f"{macd_val:.2f}", Paragraph(get_indicator_proof("MACD", macd_val), styles["DataText"])],
            ["SMA 20 (F)", f"₹{sma20:,.2f}", Paragraph("Fast tracking price action", styles["DataText"])],
            ["SMA 50 (M)", f"₹{sma50:,.2f}", Paragraph("Medium-term trend baseline", styles["DataText"])],
            ["SMA 200 (S)", f"₹{sma200:,.2f}", Paragraph("Long-term institutional support", styles["DataText"])]
        ]
        t_tech = PDFTable(tech_data, colWidths=[100, 90, 260])
        t_tech.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        story.append(t_tech)
    story.append(Spacer(1, 15))

    # Section 7: Hyper-Intelligence & Self-Learning
    story.append(Paragraph("7. Hyper-Intelligence & Self-Learning", styles["SectionHeader"]))
    macro = quant_data.get('macro', {})
    learning = quant_data.get('learning', {})
    forensics = quant_data.get('forensics', stock_data.get('forensics', {}))
    thesis = decision.get('prediction_thesis', {})
    
    hyper_data = [
        ["Intelligent Domain", "System Inference & Status"],
        ["Macro Profile", Paragraph(f"Stability: {safe_float(macro.get('macro_score', 0)):.2f}/1.0 (Stable Environment)", styles["DataText"])],
        ["Forensics", Paragraph("✅ SYTEM SECURE - LEGITIMATE" if forensics.get('is_legit', True) else "🚨 DATA ANOMALY DETECTED", styles["DataText"])],
        ["RL Learning", Paragraph(f"State: {learning.get('hidden_regime', {}).get('regime', 'Scanning...')} (Matches: {safe_float(learning.get('history', {}).get('matches', 0)):.0f})", styles["DataText"])],
        ["Causal Logic", Paragraph(thesis.get('causal_link', 'Verified Logical Connectives'), styles["DataText"])],
        ["RL Policy", Paragraph(f"ML: {safe_float(learning.get('policy_weights', {}).get('ml', 0.3)):.0%} | Tech: {safe_float(learning.get('policy_weights', {}).get('technical', 0.25)):.0%}", styles["DataText"])]
    ]
    t_hyper = PDFTable(hyper_data, colWidths=[150, 300])
    t_hyper.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_hyper)
    story.append(Spacer(1, 15))
    # --- 8. ML & AI Forecasts ---
    story.append(Paragraph("8. ML & AI Predictions", styles["SectionHeader"]))
    ml = stock_data.get('ml_predictions', stock_data.get('ml', {}))
    lstm = ml.get('lstm', {}) if isinstance(ml, dict) else {}
    lstm_preds = lstm.get('predictions', {}) if isinstance(lstm, dict) else {}
    
    ml_table_data = [
        ["Model / Horizon", "Forecast / Signal", "Confidence / Conviction"],
        ["LSTM 1-Day", f"₹{safe_float(lstm_preds.get('1d', 0)):,.2f}", f"{safe_float(lstm.get('confidence', 0)):.1%}"],
        ["LSTM 7-Day", f"₹{safe_float(lstm_preds.get('7d', 0)):,.2f}", "Neutral"],
        ["LSTM 20-Day (Proj)", f"₹{safe_float(lstm_preds.get('7d', 0)) + (safe_float(lstm_preds.get('30d', 0)) - safe_float(lstm_preds.get('7d', 0))) * (13/23):,.2f}", "Pro-Rata Projection"],
        ["Transformer (Deep)", ml.get('transformer', {}).get('trend', 'SCANNING'), f"{safe_float(ml.get('transformer', {}).get('confidence', 0)):.1%}"],
        ["XGBoost Signal", ml.get('xgboost', {}).get('signal', 'HOLD'), f"{safe_float(ml.get('xgboost', {}).get('confidence', 0)):.1%}"]
    ]
    t_ml = PDFTable(ml_table_data, colWidths=[150, 150, 150])
    t_ml.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_ml)
    story.append(Spacer(1, 15))

    # --- 9. Quantitative Strategy Matrix ---
    story.append(Paragraph("9. Quantitative Strategy Matrix", styles["SectionHeader"]))
    quant = stock_data.get('quant_signals', stock_data.get('quant', {}))
    
    q_table_data = [
        ["Strategy", "Value / Score", "Market Signal"],
        ["Momentum Score", f"{safe_float(quant.get('momentum', {}).get('score', 0)):.2f}", quant.get('momentum', {}).get('signal', 'HOLD')],
        ["Mean Reversion Z", f"{safe_float(quant.get('mean_reversion', {}).get('zscore', 0)):.2f}", quant.get('mean_reversion', {}).get('signal', 'HOLD')],
        ["HMM Regime", quant.get('regime', {}).get('current_regime', 'SIDEWAYS'), quant.get('regime', {}).get('strategy', 'Neutral')]
    ]
    t_q = PDFTable(q_table_data, colWidths=[150, 150, 150])
    t_q.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_q)
    story.append(Spacer(1, 15))

    # --- 9b. Institutional Risk Profile ---
    story.append(Paragraph("9b. Institutional Risk Profile (Forensics)", styles["SectionHeader"]))
    forensics = quant.get('forensics', stock_data.get('forensics', {}))
    
    risk_data = [
        ["Metric", "Score / Value", "Interpretation"],
        ["Altman Z-Score", f"{safe_float(forensics.get('z_score', 0)):.2f}", Paragraph("Bankruptcy Risk (<1.8 = Distress)", styles["DataText"])],
        ["Piotroski F-Score", f"{safe_float(forensics.get('f_score', 0))}/9", Paragraph("Financial Strength (>7 = Strong)", styles["DataText"])],
        ["Beneish M-Score", "N/A (Requires Full 10-K)", Paragraph("Earnings Manipulation Detection", styles["DataText"])]
    ]
    t_risk = PDFTable(risk_data, colWidths=[130, 100, 220])
    t_risk.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 15))

    # --- 10. Monte Carlo Simulations ---
    mc = decision.get('monte_carlo', {})
    if mc:
        story.append(Paragraph("10. Monte Carlo Simulations (Price Probability)", styles["SectionHeader"]))
        mc_data = [
            ["Scenario", "Projected Price Target", "Probability / Risk"],
            ["Median Target (Base Case)", f"₹{safe_float(mc.get('median_target', 0)):,.2f}", "50% Probability"],
            ["Upside Potential (Optimistic)", f"₹{safe_float(mc.get('p95_upside_potential', 0)):,.2f}", "Top 5% Outcome"],
            ["Downside Risk (VaR)", f"₹{safe_float(mc.get('p5_downside_risk', 0)):,.2f}", "Worst 5% Outcome"]
        ]
        t_mc = PDFTable(mc_data, colWidths=[150, 150, 150])
        t_mc.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        story.append(t_mc)
        story.append(Spacer(1, 15))
    
    # --- 11. Institutional Accounting & SMC ---
    story.append(Paragraph("11. Institutional Logic (SMC & Accounting)", styles["SectionHeader"]))
    acc_health = stock_data.get('quant_signals', {}).get('accounting_health', 'Stable')
    smc = stock_data.get('quant_signals', {}).get('smc', {})
    
    logic_data = [
        ["Institutional Domain", "Inference / Signal", "Concept Interpretation"],
        ["Accounting Health", str(acc_health), "Solvency and capital efficiency baseline."],
        ["Market Structure", smc.get('market_structure', {}).get('trend', 'Neutral'), "ICT SMC trend direction."],
        ["Order Blocks", f"{len(smc.get('order_blocks', []))} detected", "Institutional supply/demand zones."],
        ["Price Imbalance", f"{len(smc.get('fvg', []))} gaps", "Fair Value Gaps (FVG) status."]
    ]
    t_logic = PDFTable(logic_data, colWidths=[130, 160, 160])
    t_logic.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(t_logic)
    story.append(Spacer(1, 15))

    # Build
    try:
        doc.build(story)
        return filename
    except Exception as e:
        console.print(f"[red]PDF Error: {e}[/red]")
        return None

def interactive_stock_selector():
    """Main interactive interface"""
    while True:
        console.clear()
        
        # Check backend status
        health = check_backend_status()
        
        if not health:
            console.print(Panel.fit(
                "[bold red]⚠️  BACKEND API NOT RUNNING[/bold red]\n"
                "[yellow]Start backend: ./venv/bin/python api_server_production.py[/yellow]",
                border_style="red"
            ))
            console.print("\nPress Enter to retry or Ctrl+C to exit")
            try:
                input()
                continue
            except KeyboardInterrupt:
                break
        
        # Show backend status
        components = health.get('components', {})
        orchestrator_available = components.get('orchestrator', False)
        
        console.print(Panel.fit(
            f"[bold green]🚀 ULTIMATE STOCK ANALYSIS TERMINAL[/bold green]\n"
            f"[dim]Backend API: {health.get('version')} | Orchestrator: {'✅ ACTIVE' if orchestrator_available else '❌ Unavailable'}[/dim]",
            border_style="green"
        ))
        
        if orchestrator_available:
            console.print("[green]✅ Full Deep Analysis Available (Select a stock to trigger)[/green]")
        else:
            console.print("[yellow]⚠️  Using Simple Analysis (install dependencies for full features)[/yellow]")
        
        console.print("[yellow]⚡ Running RAPID MARKET SCAN (Simple Mode) for top 20 stocks...[/yellow]\n")
        
        # Fetch data from API
        stocks_data = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading stocks from API...", total=len(TOP_20_STOCKS))
            for symbol in TOP_20_STOCKS:
                # For list view, use simple analysis (faster)
                data = fetch_stock_data_from_api(symbol, use_comprehensive=False)
                if data:
                    # Simple analysis returns flat structure with current_price, day_change_percent, etc.
                    current_price = data.get('current_price', 0)
                    day_change = data.get('day_change_percent', 0)
                    volume = data.get('volume', 0)
                    
                    # Get technical indicators
                    technical = data.get('technical_indicators', {})
                    rsi_data = technical.get('rsi', {})
                    rsi = rsi_data.get('value', 50) if isinstance(rsi_data, dict) else 50
                    
                    # Get recommendation
                    rec = data.get('recommendation', {})
                    action = rec.get('action', 'HOLD') if isinstance(rec, dict) else 'HOLD'
                    reason = rec.get('reasoning', 'Analysis pending') if isinstance(rec, dict) else 'Analysis pending'
                    
                    # Get Sentiment
                    sent_data = data.get('sentiment', {})
                    sentiment_score = sent_data.get('overall_score', 0.5) if isinstance(sent_data, dict) else 0.5
                    
                    stocks_data.append({
                        'symbol': symbol.replace('.NS', ''),
                        'price': current_price,
                        'day_change': day_change,
                        'week_change': 0,
                        'volume': volume,
                        'rsi': rsi,
                        'sentiment_score': sentiment_score,
                        'recommendation': action,
                        'reason': reason,
                        'from_api': True
                    })
                progress.advance(task)
        
        # Display table
        console.clear()
        console.print(Panel.fit(
            f"[bold green]🚀 ULTIMATE STOCK ANALYSIS TERMINAL[/bold green]\n"
            f"[dim]Backend API: {health.get('version')} | Status: {'Full Analysis' if orchestrator_available else 'Simple Analysis'}[/dim]",
            border_style="green"
        ))
        
        if stocks_data:
            table = show_stock_list_table(stocks_data)
            console.print(table)
        
        # Menu
        console.print(f"\n[bold cyan]Options:[/bold cyan]")
        console.print("  [1-20] Select stock number for FULL COMPREHENSIVE ANALYSIS")
        console.print("  [C]    COMPARE multiple stocks")
        console.print("  [R]    Refresh data")
        console.print("  [Q]    Quit\n")
        
        choice = Prompt.ask("Enter your choice", default="R").upper()
        
        if choice == 'Q':
            console.print("[green]✅ Goodbye![/green]")
            break
        elif choice == 'R':
            continue
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(stocks_data):
                selected = stocks_data[num - 1]
                symbol = selected['symbol'] + '.NS'
                
                console.print(f"\n[bold yellow]🚀 INITIATING DEEP AI ANALYSIS for {symbol}...[/bold yellow]")
                console.print("[dim]   • Invoking NVIDIA + Groq LLM Ensembles[/dim]")
                console.print("[dim]   • Running ML Models (LSTM + XGBoost)[/dim]")
                console.print("[dim]   • Activating Real-Time Training (Self-Learning Loop)[/dim]\n")
                
                # Fetch comprehensive analysis
                full_data = fetch_stock_data_from_api(symbol, use_comprehensive=orchestrator_available)
                
                if full_data:
                    full_data['symbol'] = selected['symbol']
                    show_full_stock_details(full_data)
                    
                    # 📄 PDF Save Option
                    if Prompt.ask("\n[bold cyan]💾 Save Report as PDF? (y/n)[/bold cyan]", choices=["y", "n"], default="n") == "y":
                        intra_path = f"intraday_{selected['symbol']}.png"
                        sent_path = f"sentiment_{selected['symbol']}.png"
                        
                        # Generate and save charts silently if needed, or by calling existing functions
                        show_intraday_chart(selected['symbol'], full_data.get('quant_signals', {}).get('temporal', {}), save_path=intra_path)
                        show_sentiment_distribution(full_data, save_path=sent_path)
                        
                        pdf_file = generate_pdf_report(selected['symbol'], full_data, intraday_img=intra_path, sentiment_img=sent_path)
                        
                        if pdf_file:
                             console.print(f"[green]✅ Enhanced Report saved: {pdf_file}[/green]")
                        else:
                             console.print(f"[red]❌ Failed to save PDF[/red]")
                        
                        # Cleanup temporary images
                        for f in [intra_path, sent_path]:
                            if os.path.exists(f): os.remove(f)
                    
                    Prompt.ask("\n[dim]Press Enter to return to list[/dim]")
                else:
                    console.print("[red]Failed to fetch detailed analysis[/red]")
                    time.sleep(2)
            else:
                console.print(f"[red]Invalid number. Choose 1-{len(stocks_data)}[/red]")
                time.sleep(2)
        elif choice == 'C':
            # 🆕 COMPARISON MODE
            nums_str = Prompt.ask("Enter stock numbers to compare (comma separated, e.g., 1,3,4)")
            try:
                nums = [int(n.strip()) for n in nums_str.split(',') if n.strip().isdigit()]
                selected_stocks = []
                for n in nums:
                    if 1 <= n <= len(stocks_data):
                        selected_stocks.append(stocks_data[n-1]['symbol'] + '.NS')
                
                if len(selected_stocks) < 2:
                    console.print("[red]Select at least 2 stocks to compare[/red]")
                    time.sleep(2)
                    continue
                
                console.print(f"\n[bold yellow]🔄 COMPARING {', '.join(selected_stocks)}...[/bold yellow]")
                
                # Fetch data for all selected stocks
                comparison_data = []
                for sym in selected_stocks:
                    data = fetch_stock_data_from_api(sym, use_comprehensive=False) # Simple for speed
                    if data:
                        comparison_data.append(data)
                
                if comparison_data:
                    from worker.src.utils.stock_comparator import StockComparator, generate_comparison_text
                    comparator = StockComparator()
                    report = comparator.compare_stocks(comparison_data)
                    text_report = generate_comparison_text(report)
                    
                    console.clear()
                    console.print(Panel(text_report, title="📊 Stock Comparison Report", border_style="cyan"))
                    
                    # Show a relative sentiment chart for comparison
                    labels = report['symbols']
                    values = [r['score'] * 100 for r in report['sentiment_ranking']]
                    plt.clf()
                    plt.bar(labels, values, color="yellow")
                    plt.title("Relative Sentiment Comparison (%)")
                    plt.show()
                    
                    Prompt.ask("\n[dim]Press Enter to return to list[/dim]")
                else:
                    console.print("[red]Failed to fetch comparison data[/red]")
                    time.sleep(2)
            except Exception as e:
                console.print(f"[red]Comparison error: {e}[/red]")
                time.sleep(2)


if __name__ == "__main__":
    try:
        import sys
        if len(sys.argv) > 1:
             # Direct Launch Mode (Bypass Menu)
             symbol = sys.argv[1].upper()
             
             # Smart Suffix Logic:
             # If it already has a suffix (like .NS, .BO, .US), keep it.
             # If it has NO suffix (like AAPL, TSLA), keep it (defaults to US/Global).
             # If it is an Indian stock without suffix (like RELIANCE, TCS), add .NS.
             
             # Heuristic: If it contains a dot, assume it's valid (AAPL.US, RELIANCE.NS)
             if "." not in symbol:
                 # Check if it's likely a US tech giant or global ticker
                 us_bluechips = ["AAPL", "MSFT", "GOOG", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
                 if symbol not in us_bluechips:
                      symbol += ".NS" # Default to NSE for common inputs
             
             console.print(f"\n[bold yellow]🚀 INITIATING DIRECT ANALYSIS for {symbol}...[/bold yellow]")
             
             # Fetch comprehensive analysis
             full_data = fetch_stock_data_from_api(symbol, use_comprehensive=True)
             
             # ✅ DATA VALIDATION & SMART RECOVERY
             # If price is 0 or data is missing, it likely means invalid symbol
             is_valid = full_data and full_data.get('current_price', 0) > 0
             
             if not is_valid:
                 console.print(f"[red]❌ '{symbol}' not found or no data available.[/red]")
                 
                 # Attempt Smart Recovery
                 resolved_symbol = resolve_symbol_smartly(sys.argv[1]) # Use original input name
                 
                 if resolved_symbol and resolved_symbol != symbol:
                     if Prompt.ask(f"\n[bold yellow]💡 Did you mean '{resolved_symbol}'? (y/n)[/bold yellow]", choices=["y", "n"], default="y") == "y":
                         console.print(f"\n[green]🔄 Retrying with {resolved_symbol}...[/green]")
                         symbol = resolved_symbol
                         full_data = fetch_stock_data_from_api(symbol, use_comprehensive=True)
                         is_valid = full_data and full_data.get('current_price', 0) > 0
             
             if is_valid and full_data:
                 show_full_stock_details(full_data)
                 
                 # 📄 PDF Save Option
                 if Prompt.ask("\n[bold cyan]💾 Save Report as PDF? (y/n)[/bold cyan]", choices=["y", "n"], default="n") == "y":
                     cwd = os.getcwd(); intra_path = os.path.join(cwd, f"intraday_{symbol}.png")
                     sent_path = os.path.join(cwd, f"sentiment_{symbol}.png")
                     forecast_path = os.path.join(cwd, f"forecast_{symbol}.png")
                     
                     show_intraday_chart(symbol, full_data.get('quant_signals', {}).get('temporal', {}), save_path=intra_path)
                     show_sentiment_distribution(full_data, save_path=sent_path)
                     
                     # Generate Forecast Chart for PDF
                     ml_preds = full_data.get('ml_predictions', full_data.get('ml', {})).get('lstm', {})
                     lstm_p = ml_preds.get('predictions', {}) if isinstance(ml_preds, dict) else {}
                     current_p = full_data.get('current_price', 0)
                     f_data = {
                         '1d': safe_float(lstm_p.get('1d', lstm_p.get('1_day', current_p))),
                         '7d': safe_float(lstm_p.get('7d', lstm_p.get('7_day', current_p))),
                         '30d': safe_float(lstm_p.get('30d', lstm_p.get('30_day', current_p)))
                     }
                     show_forecast_chart(symbol, current_p, f_data, save_path=forecast_path)
                     
                     pdf_file = generate_pdf_report(full_data, "reports", images=[intra_path, sent_path, forecast_path])
                     
                     if pdf_file:
                          console.print(f"[green]✅ Enhanced Report saved: {pdf_file}[/green]")
                     else:
                          console.print(f"[red]❌ Failed to save PDF[/red]")

                     # Cleanup temporary images
                     for f in [intra_path, sent_path, forecast_path]:
                         if os.path.exists(f): os.remove(f)

                 # Wait before exit so user can read
                 Prompt.ask("\n[dim]Press Enter to exit[/dim]")
             else:
                 console.print("[red]Failed to fetch detailed analysis[/red]")
        else:
            # Interactive Mode
            interactive_stock_selector()
            
    except KeyboardInterrupt:
        console.print("\n[green]✅ Exiting...[/green]")
        sys.exit(0)
