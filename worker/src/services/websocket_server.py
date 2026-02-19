"""
Real-time Stock Price WebSocket Server
Provides live price updates to frontend
"""

import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import yfinance as yf
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
    
    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
    
    async def broadcast(self, symbol: str, data: dict):
        """Broadcast data to all clients watching this symbol"""
        if symbol in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(data)
                except:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[symbol].discard(conn)

manager = ConnectionManager()

async def fetch_live_price(symbol: str):
    """Fetch current price for symbol"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d', interval='1m')
        if len(data) > 0:
            latest = data.iloc[-1]
            return {
                'symbol': symbol,
                'price': float(latest['Close']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().isoformat(),
                'change': float(latest['Close'] - data.iloc[0]['Open']),
                'change_percent': float((latest['Close'] / data.iloc[0]['Open'] - 1) * 100)
            }
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
    return None

async def price_updater():
    """Background task to update prices every 5 seconds"""
    while True:
        symbols = list(manager.active_connections.keys())
        
        for symbol in symbols:
            price_data = await fetch_live_price(symbol)
            if price_data:
                await manager.broadcast(symbol, {
                    'type': 'price_update',
                    'data': price_data
                })
        
        await asyncio.sleep(5)  # Update every 5 seconds

# Add to FastAPI app
def setup_websocket(app):
    """Setup WebSocket endpoint on FastAPI app"""
    
    @app.websocket("/ws/stock/{symbol}")
    async def websocket_endpoint(websocket: WebSocket, symbol: str):
        await manager.connect(websocket, symbol)
        try:
            # Send initial price
            initial_price = await fetch_live_price(symbol)
            if initial_price:
                await websocket.send_json({
                    'type': 'initial',
                    'data': initial_price
                })
            
            # Keep connection alive
            while True:
                # Wait for client messages (ping/pong)
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, symbol)
    
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(price_updater())

if __name__ == "__main__":
    # Demo
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI()
    setup_websocket(app)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
