#!/bin/bash
"""
Auto-Monitor - Live Stock Analysis Display
Runs comprehensive analysis every 2 minutes
"""

# Default symbol
SYMBOL=${1:-TCS.NS}
INTERVAL=${2:-120}  # 2 minutes default

echo "🧠 Starting Live Market Analysis Monitor"
echo "📊 Symbol: $SYMBOL"
echo "⏱️  Update Interval: ${INTERVAL}s ($(($INTERVAL / 60))m)"
echo "🔄 Press Ctrl+C to stop"
echo ""

# Activate virtual environment
source ./venv/bin/activate

# Continuous monitoring loop
while true; do
    clear
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "                    🔴 LIVE MARKET ANALYSIS - AUTO-REFRESH"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Run analysis
    python analyze_cli.py $SYMBOL
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "⏰ Next update in ${INTERVAL}s... (Monitoring $SYMBOL)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    # Wait for interval
    sleep $INTERVAL
done
