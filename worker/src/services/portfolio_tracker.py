"""
Portfolio Tracker - Track user's stock holdings and performance
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import yfinance as yf

class Position(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float
    buy_date: str
    notes: Optional[str] = None

class Portfolio:
    """Manages stock portfolio"""
    
    def __init__(self, mongodb_client=None):
        self.mongodb = mongodb_client
        self.db = mongodb_client['brand_tracker'] if mongodb_client else None
    
    def add_position(self, user_id: str, position: Position) -> Dict:
        """Add a new position to portfolio"""
        doc = {
            'user_id': user_id,
            'symbol': position.symbol,
            'quantity': position.quantity,
            'avg_buy_price': position.avg_buy_price,
            'buy_date': position.buy_date,
            'notes': position.notes,
            'added_at': datetime.now().isoformat()
        }
        
        if self.db:
            result = self.db.portfolio.insert_one(doc)
            doc['id'] = str(result.inserted_id)
        
        return doc
    
    def get_positions(self, user_id: str) -> List[Dict]:
        """Get all positions for user"""
        if not self.db:
            return []
        
        positions = list(self.db.portfolio.find(
            {'user_id': user_id},
            {'_id': 0}
        ))
        
        return positions
    
    def calculate_portfolio_value(self, user_id: str) -> Dict:
        """Calculate current portfolio value and P&L"""
        positions = self.get_positions(user_id)
        
        if not positions:
            return {
                'total_value': 0,
                'total_invested': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0,
                'positions': []
            }
        
        total_value = 0
        total_invested = 0
        enriched_positions = []
        
        for pos in positions:
            try:
                # Fetch current price
                ticker = yf.Ticker(pos['symbol'])
                current_price = ticker.history(period='1d')['Close'].iloc[-1]
                
                # Calculate values
                invested = pos['quantity'] * pos['avg_buy_price']
                current_value = pos['quantity'] * current_price
                pnl = current_value - invested
                pnl_percent = (pnl / invested) * 100 if invested > 0 else 0
                
                total_value += current_value
                total_invested += invested
                
                enriched_positions.append({
                    **pos,
                    'current_price': float(current_price),
                    'current_value': float(current_value),
                    'invested': float(invested),
                    'pnl': float(pnl),
                    'pnl_percent': float(pnl_percent)
                })
            
            except Exception as e:
                print(f"Error calculating value for {pos['symbol']}: {e}")
                enriched_positions.append({
                    **pos,
                    'error': str(e)
                })
        
        total_pnl = total_value - total_invested
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'total_value': total_value,
            'total_invested': total_invested,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'positions': enriched_positions,
            'updated_at': datetime.now().isoformat()
        }
    
    def remove_position(self, user_id: str, symbol: str) -> bool:
        """Remove a position from portfolio"""
        if not self.db:
            return False
        
        result = self.db.portfolio.delete_one({
            'user_id': user_id,
            'symbol': symbol
        })
        
        return result.deleted_count > 0
    
    def update_position(self, user_id: str, symbol: str, updates: Dict) -> bool:
        """Update position details"""
        if not self.db:
            return False
        
        result = self.db.portfolio.update_one(
            {'user_id': user_id, 'symbol': symbol},
            {'$set': updates}
        )
        
        return result.modified_count > 0

def demo():
    """Demo portfolio tracker"""
    portfolio = Portfolio()
    
    # Add positions
    pos1 = Position(
        symbol="RELIANCE.NS",
        quantity=10,
        avg_buy_price=2400,
        buy_date="2024-01-15"
    )
    
    pos2 = Position(
        symbol="TCS.NS",
        quantity=5,
        avg_buy_price=3600,
        buy_date="2024-01-20"
    )
    
    print("Portfolio Performance:")
    print("="*60)
    
    # Calculate (would use real MongoDB in production)
    mock_positions = [
        {
            'symbol': 'RELIANCE.NS',
            'quantity': 10,
            'avg_buy_price': 2400,
            'buy_date': '2024-01-15'
        },
        {
            'symbol': 'TCS.NS',
            'quantity': 5,
            'avg_buy_price': 3600,
            'buy_date': '2024-01-20'
        }
    ]
    
    for pos in mock_positions:
        ticker = yf.Ticker(pos['symbol'])
        current_price = ticker.history(period='1d')['Close'].iloc[-1]
        
        invested = pos['quantity'] * pos['avg_buy_price']
        current_value = pos['quantity'] * current_price
        pnl = current_value - invested
        pnl_percent = (pnl / invested) * 100
        
        print(f"\n{pos['symbol']}:")
        print(f"  Quantity: {pos['quantity']}")
        print(f"  Avg Price: ₹{pos['avg_buy_price']}")
        print(f"  Current Price: ₹{current_price:.2f}")
        print(f"  Invested: ₹{invested:,.2f}")
        print(f"  Current Value: ₹{current_value:,.2f}")
        print(f"  P&L: ₹{pnl:,.2f} ({pnl_percent:+.2f}%)")

if __name__ == "__main__":
    demo()
