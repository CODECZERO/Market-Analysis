"""
Regulatory Data Provider
Fetches specific regulatory, legal, and compliance news/filings.
Acts as the eyes for the Regulatory Neural Network.
"""

import yfinance as yf
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

class RegulatoryDataProvider:
    def __init__(self):
        # Keywords that trigger regulatory scrutiny
        self.risk_keywords = [
            'investigation', 'audit', 'fraud', 'lawsuit', 'indictment',
            'sec', 'fine', 'penalty', 'compliance', 'breach', 'illegal',
            'misconduct', 'sanctions', 'whistleblower', 'subpoena',
            'crypto', 'money laundering', 'racketeering', 'banned', 'recall',
            'environmental', 'emissions', 'dumping', 'gdpr', 'antitrust'
        ]
        
        # Positive regulatory keywords (cleared of wrongdoing)
        self.safe_keywords = [
            'cleared', 'dismissed', 'settlement', 'compliant', 'approved',
            'authorized', 'legal', 'exonerated', 'license granted', 'award'
        ]

    def fetch_regulatory_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch regulatory-specific news and filings.
        Returns a structured dictionary of findings.
        """
        findings = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "regulatory_events": [],
            "risk_score_raw": 0.0,
            "active_investigations": 0,
            "sentiment_bias": "NEUTRAL"
        }
        
        try:
            # 1. Fetch News via yfinance
            ticker = yf.Ticker(symbol)
            news_items = ticker.news
            
            for item in news_items:
                title = item.get('title', '').lower()
                link = item.get('link', '')
                publisher = item.get('publisher', 'Unknown')
                
                # Check for Risk Keywords
                risk_matches = [k for k in self.risk_keywords if k in title]
                if risk_matches:
                    findings["regulatory_events"].append({
                        "type": "RISK",
                        "title": item.get('title'),
                        "keywords": risk_matches,
                        "source": publisher,
                        "link": link
                    })
                    findings["active_investigations"] += 1
                    findings["risk_score_raw"] += 0.25 # Base risk penalty per article

                # Check for Safe Keywords (Mitigation)
                safe_matches = [k for k in self.safe_keywords if k in title]
                if safe_matches:
                    findings["regulatory_events"].append({
                        "type": "MITIGATION",
                        "title": item.get('title'),
                        "keywords": safe_matches,
                        "source": publisher,
                        "link": link
                    })
                    findings["risk_score_raw"] -= 0.15 # Mitigation bonus

            # 2. Institutional/Insider Flags (Proxy for regulatory leak)
            # If insider selling is huge + regulatory news = HIGH RISK
            # Try multiple attribute names as yfinance API changes often
            insider = getattr(ticker, 'insider_transactions', getattr(ticker, 'insidertransactions', None))
            
            if insider is not None and not insider.empty:
                # Basic check: recent selling
                # Columns vary: 'Text', 'Transaction', etc.
                txt_col = 'Text' if 'Text' in insider.columns else 'Transaction'
                if txt_col in insider.columns:
                    recent_sells = insider[insider[txt_col].str.contains('Sale', case=False, na=False)].head(5)
                    if not recent_sells.empty:
                        findings["insider_sell_detected"] = True
                        findings["risk_score_raw"] += 0.1
            
            # Clamp Score (0 to 1)
            findings["risk_score_raw"] = max(0.0, min(1.0, findings["risk_score_raw"]))
            
            return findings

        except Exception as e:
            print(f"⚠️ Regulatory Fetch Error for {symbol}: {e}")
            return findings

# Global instance
_reg_provider = None

def get_regulatory_provider() -> RegulatoryDataProvider:
    global _reg_provider
    if _reg_provider is None:
        _reg_provider = RegulatoryDataProvider()
    return _reg_provider
