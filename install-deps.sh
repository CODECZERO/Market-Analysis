#!/bin/bash

# Install New Feature Dependencies
# Run this to install all required packages for new features

echo "📦 Installing dependencies for new features..."

# Try venv first
if [ -f "venv/bin/activate" ]; then
    echo "Using virtual environment..."
    source venv/bin/activate
    pip install requests beautifulsoup4 lxml praw
else
    echo "Installing to user directory..."
    python3 -m pip install --user requests beautifulsoup4 lxml praw
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Dependencies installed:"
echo "  - requests (HTTP client)"
echo "  - beautifulsoup4 (HTML parsing)"  
echo "  - lxml (XML/HTML parser)"
echo "  - praw (Reddit API)"
echo ""
echo "Next: python quick_analyze.py RELIANCE"
