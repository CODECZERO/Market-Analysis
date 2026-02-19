#!/bin/bash

# Quick launcher for advanced CLI dashboard

echo "🚀 Starting Advanced Stock Analysis Dashboard..."
echo ""

cd "$(dirname "$0")"
source ./venv/bin/activate

# Run the advanced CLI
python advanced_cli.py

deactivate
