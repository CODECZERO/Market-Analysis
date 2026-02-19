"""
Price Alerts System - Send notifications when price reaches target
"""

from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import yfinance as yf

class AlertType(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE = "percent_change"
    VOLUME_SPIKE = "volume_spike"

class Alert:
    """Price alert"""
    
    def __init__(self, alert_id: str, user_id: str, symbol: str, 
                 alert_type: AlertType, threshold: float, 
                 message: Optional[str] = None):
        self.id = alert_id
        self.user_id = user_id
        self.symbol = symbol
        self.alert_type = alert_type
        self.threshold = threshold
        self.message = message
        self.created_at = datetime.now()
        self.triggered = False
        self.triggered_at = None

class AlertsManager:
    """Manages price alerts"""
    
    def __init__(self, mongodb_client=None, redis_client=None):
        self.mongodb = mongodb_client
        self.redis = redis_client
        self.db = mongodb_client['brand_tracker'] if mongodb_client else None
        self.alerts_cache: Dict[str, Alert] = {}
    
    def create_alert(self, user_id: str, symbol: str, 
                    alert_type: str, threshold: float, 
                    message: Optional[str] = None) -> Dict:
        """Create a new price alert"""
        alert_doc = {
            'user_id': user_id,
            'symbol': symbol,
            'alert_type': alert_type,
            'threshold': threshold,
            'message': message,
            'created_at': datetime.now().isoformat(),
            'triggered': False,
            'active': True
        }
        
        if self.db:
            result = self.db.alerts.insert_one(alert_doc)
            alert_doc['id'] = str(result.inserted_id)
            del alert_doc['_id']
        
        return alert_doc
    
    def get_active_alerts(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get all active alerts"""
        if not self.db:
            return []
        
        query = {'active': True, 'triggered': False}
        if user_id:
            query['user_id'] = user_id
        
        alerts = list(self.db.alerts.find(query, {'_id': 0}))
        return alerts
    
    def check_alerts(self) -> List[Dict]:
        """Check all active alerts and trigger if conditions met"""
        active_alerts = self.get_active_alerts()
        triggered_alerts = []
        
        # Group by symbol for efficiency
        symbol_alerts = {}
        for alert in active_alerts:
            symbol = alert['symbol']
            if symbol not in symbol_alerts:
                symbol_alerts[symbol] = []
            symbol_alerts[symbol].append(alert)
        
        # Check each symbol
        for symbol, alerts in symbol_alerts.items():
            try:
                # Fetch current data
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='2d')
                
                if len(data) < 2:
                    continue
                
                current_price = float(data['Close'].iloc[-1])
                prev_price = float(data['Close'].iloc[-2])
                current_volume = int(data['Volume'].iloc[-1])
                avg_volume = int(data['Volume'].mean())
                
                percent_change = ((current_price - prev_price) / prev_price) * 100
                
                # Check each alert
                for alert in alerts:
                    alert_type = alert['alert_type']
                    threshold = alert['threshold']
                    triggered = False
                    
                    if alert_type == AlertType.PRICE_ABOVE.value:
                        triggered = current_price >= threshold
                    
                    elif alert_type == AlertType.PRICE_BELOW.value:
                        triggered = current_price <= threshold
                    
                    elif alert_type == AlertType.PERCENT_CHANGE.value:
                        triggered = abs(percent_change) >= threshold
                    
                    elif alert_type == AlertType.VOLUME_SPIKE.value:
                        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                        triggered = volume_ratio >= threshold
                    
                    if triggered:
                        # Mark as triggered
                        alert['triggered'] = True
                        alert['triggered_at'] = datetime.now().isoformat()
                        alert['trigger_price'] = current_price
                        alert['trigger_data'] = {
                            'price': current_price,
                            'percent_change': percent_change,
                            'volume': current_volume,
                            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0
                        }
                        
                        if self.db:
                            self.db.alerts.update_one(
                                {'_id': alert.get('_id')},
                                {'$set': {
                                    'triggered': True,
                                    'triggered_at': alert['triggered_at'],
                                    'trigger_price': current_price
                                }}
                            )
                        
                        triggered_alerts.append(alert)
            
            except Exception as e:
                print(f"Error checking alerts for {symbol}: {e}")
        
        return triggered_alerts
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        if not self.db:
            return False
        
        result = self.db.alerts.delete_one({'id': alert_id})
        return result.deleted_count > 0
    
    def deactivate_alert(self, alert_id: str) -> bool:
        """Deactivate an alert without deleting"""
        if not self.db:
            return False
        
        result = self.db.alerts.update_one(
            {'id': alert_id},
            {'$set': {'active': False}}
        )
        return result.modified_count > 0

def demo():
    """Demo alerts system"""
    manager = AlertsManager()
    
    print("Price Alerts Demo")
    print("="*60)
    
    # Create sample alerts
    alerts = [
        {
            'user_id': 'user1',
            'symbol': 'RELIANCE.NS',
            'alert_type': AlertType.PRICE_ABOVE.value,
            'threshold': 2500,
            'message': 'RELIANCE crossed ₹2500!'
        },
        {
            'user_id': 'user1',
            'symbol': 'TCS.NS',
            'alert_type': AlertType.PRICE_BELOW.value,
            'threshold': 3500,
            'message': 'TCS dropped below ₹3500'
        },
        {
            'user_id': 'user1',
            'symbol': 'INFY.NS',
            'alert_type': AlertType.PERCENT_CHANGE.value,
            'threshold': 5,
            'message': 'INFY moved more than 5%'
        }
    ]
    
    for alert in alerts:
        print(f"\nAlert: {alert['symbol']} - {alert['alert_type']}")
        print(f"Threshold: {alert['threshold']}")
        print(f"Message: {alert['message']}")

if __name__ == "__main__":
    demo()
