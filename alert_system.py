#!/usr/bin/env python3
"""
Alert System - Price alerts and technical signal notifications
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import yfinance as yf

ALERTS_FILE = "data/alerts.json"

class AlertSystem:
    def __init__(self):
        self.ensure_data_dir()
        self.alerts = self.load_alerts()
    
    def ensure_data_dir(self):
        os.makedirs("data", exist_ok=True)
    
    def load_alerts(self) -> List[Dict]:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_alerts(self):
        with open(ALERTS_FILE, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def add_price_alert(self, symbol: str, target_price: float, condition: str = "above"):
        """
        Add price alert
        condition: 'above' or 'below'
        """
        alert = {
            "id": len(self.alerts),
            "type": "price",
            "symbol": symbol,
            "target_price": target_price,
            "condition": condition,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggered": False
        }
        
        self.alerts.append(alert)
        self.save_alerts()
        print(f"✅ Alert set: {symbol} {condition} ₹{target_price:,.2f}")
        return alert
    
    def add_rsi_alert(self, symbol: str, rsi_threshold: float, condition: str = "above"):
        """
        Add RSI alert
        condition: 'above' (overbought) or 'below' (oversold)
        """
        alert = {
            "id": len(self.alerts),
            "type": "rsi",
            "symbol": symbol,
            "rsi_threshold": rsi_threshold,
            "condition": condition,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggered": False
        }
        
        self.alerts.append(alert)
        self.save_alerts()
        signal = "Overbought" if condition == "above" else "Oversold"
        print(f"✅ Alert set: {symbol} RSI {condition} {rsi_threshold} ({signal})")
        return alert
    
    def check_alerts(self) -> List[Dict]:
        """Check all active alerts and return triggered ones"""
        triggered = []
        
        for alert in self.alerts:
            if alert['status'] != 'active' or alert['triggered']:
                continue
            
            try:
                stock = yf.Ticker(alert['symbol'])
                hist = stock.history(period="1mo")
                
                if hist.empty:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                # Check price alerts
                if alert['type'] == 'price':
                    target = alert['target_price']
                    condition = alert['condition']
                    
                    if (condition == 'above' and current_price >= target) or \
                       (condition == 'below' and current_price <= target):
                        alert['triggered'] = True
                        alert['triggered_at'] = datetime.now().isoformat()
                        alert['triggered_price'] = float(current_price)
                        triggered.append(alert)
                
                # Check RSI alerts
                elif alert['type'] == 'rsi':
                    # Calculate RSI
                    delta = hist['Close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean()
                    loss = -delta.where(delta < 0, 0).rolling(14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    current_rsi = rsi.iloc[-1]
                    
                    if pd.isna(current_rsi):
                        continue
                    
                    threshold = alert['rsi_threshold']
                    condition = alert['condition']
                    
                    if (condition == 'above' and current_rsi >= threshold) or \
                       (condition == 'below' and current_rsi <= threshold):
                        alert['triggered'] = True
                        alert['triggered_at'] = datetime.now().isoformat()
                        alert['triggered_rsi'] = float(current_rsi)
                        alert['current_price'] = float(current_price)
                        triggered.append(alert)
            
            except Exception as e:
                print(f"Error checking {alert['symbol']}: {e}")
                continue
        
        if triggered:
            self.save_alerts()
        
        return triggered
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [a for a in self.alerts if a['status'] == 'active' and not a['triggered']]
    
    def remove_alert(self, alert_id: int):
        """Remove an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'removed'
                self.save_alerts()
                print(f"✅ Alert {alert_id} removed")
                return True
        return False
    
    def show_triggered_alerts(self):
        """Display triggered alerts"""
        triggered = [a for a in self.alerts if a.get('triggered')]
        
        if not triggered:
            print("No triggered alerts")
            return
        
        print("\n🔔 TRIGGERED ALERTS:")
        print("=" * 80)
        
        for alert in triggered:
            print(f"\n{alert['symbol']} - {alert['type'].upper()} Alert")
            print(f"  Created: {alert['created_at'][:10]}")
            print(f"  Triggered: {alert['triggered_at'][:10]}")
            
            if alert['type'] == 'price':
                print(f"  Target: ₹{alert['target_price']:,.2f} ({alert['condition']})")
                print(f"  Price when triggered: ₹{alert['triggered_price']:,.2f}")
            elif alert['type'] == 'rsi':
                print(f"  RSI Threshold: {alert['rsi_threshold']} ({alert['condition']})")
                print(f"  RSI when triggered: {alert['triggered_rsi']:.1f}")
                print(f"  Price: ₹{alert['current_price']:,.2f}")

import pandas as pd

if __name__ == "__main__":
    # Test
    alerts = AlertSystem()
    
    # Example: Add alerts
    alerts.add_price_alert("TCS.NS", 3200, "above")
    alerts.add_rsi_alert("RELIANCE.NS", 70, "above")
    
    print(f"\nActive alerts: {len(alerts.get_active_alerts())}")
    
    # Check alerts
    triggered = alerts.check_alerts()
    if triggered:
        print(f"\n🔔 {len(triggered)} alerts triggered!")
        alerts.show_triggered_alerts()
