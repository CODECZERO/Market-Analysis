"""
Simple FastAPI Server (Alternative to TypeScript API Gateway)
Provides REST API for stock analysis with Redis queue integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker', 'src'))

from utils.redis_queue import RedisQueueManager, enqueue_analysis
from utils.mongodb_manager import MongoDBManager

app = FastAPI(
    title="Market Analysis API",
    description="AI-powered Indian stock market analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Managers
redis_manager = RedisQueueManager()
db_manager = MongoDBManager()

# Models
class AnalyzeRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    refresh: bool = False

class WatchlistItem(BaseModel):
    symbol: str
    exchange: str = "NSE"


@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Market Analysis API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/stocks/analyze",
            "result": "GET /api/stocks/analyze/{analysis_id}",
            "progress": "GET /api/stocks/analyze/{analysis_id}/progress",
            "watchlist": "GET /api/stocks/watchlist",
            "add_watchlist": "POST /api/stocks/watchlist",
            "remove_watchlist": "DELETE /api/stocks/watchlist/{symbol}"
        }
    }


@app.post("/api/stocks/analyze")
async def analyze_stock(request: AnalyzeRequest):
    """
    Trigger stock analysis
    
    Returns analysis_id to track progress
    """
    try:
        # Check cache if not refresh
        if not request.refresh:
            cache_key = f"analysis_result:{request.exchange}:{request.symbol}"
            cached = redis_manager.cache_get(cache_key)
            
            if cached:
                return {
                    "success": True,
                    "cached": True,
                    "data": cached
                }
        
        # Enqueue analysis job
        analysis_id = enqueue_analysis(request.symbol, request.exchange)
        
        return {
            "success": True,
            "data": {
                "analysisId": analysis_id,
                "symbol": request.symbol,
                "exchange": request.exchange,
                "status": "queued",
                "message": "Analysis job queued successfully"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/analyze/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID"""
    try:
        result = redis_manager.cache_get(f"analysis_result:{analysis_id}")
        
        if result:
            return {
                "success": True,
                "data": result
            }
        
        # Check if still processing
        progress = redis_manager.cache_get(f"analysis_progress:{analysis_id}")
        if progress:
            return {
                "success": False,
                "error": "Analysis still in progress",
                "progress": progress
            }
        
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/analyze/{analysis_id}/progress")
async def get_analysis_progress(analysis_id: str):
    """Get analysis progress"""
    try:
        progress = redis_manager.cache_get(f"analysis_progress:{analysis_id}")
        
        if progress:
            return {
                "success": True,
                "data": progress
            }
        
        # Check if completed
        result = redis_manager.cache_get(f"analysis_result:{analysis_id}")
        if result:
            return {
                "success": True,
                "data": {
                    "analysisId": analysis_id,
                    "status": "completed",
                    "progress": 100
                }
            }
        
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/watchlist")
async def get_watchlist(user_id: str = "default_user"):
    """Get user's watchlist"""
    try:
        watchlist = db_manager.get_watchlist(user_id)
        
        return {
            "success": True,
            "data": watchlist,
            "count": len(watchlist)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stocks/watchlist")
async def add_to_watchlist(item: WatchlistItem, user_id: str = "default_user"):
    """Add stock to watchlist"""
    try:
        success = db_manager.add_to_watchlist(user_id, item.symbol, item.exchange)
        
        if success:
            return {
                "success": True,
                "data": {
                    "symbol": item.symbol,
                    "exchange": item.exchange
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add to watchlist")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/stocks/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str, exchange: str = "NSE", user_id: str = "default_user"):
    """Remove stock from watchlist"""
    try:
        success = db_manager.remove_from_watchlist(user_id, symbol, exchange)
        
        if success:
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "exchange": exchange,
                    "removed": True
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Stock not in watchlist")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/quote/{symbol}")
async def get_quote(symbol: str, exchange: str = "NSE"):
    """Get current stock quote (placeholder)"""
    # This would fetch from yfinance in production
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "exchange": exchange,
            "message": "Real-time quotes not implemented yet"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis
        redis_ok = redis_manager.redis_client.ping()
        
        # Check MongoDB
        mongo_ok = db_manager.db is not None
        
        # Check queue stats
        queue_stats = redis_manager.get_all_queue_stats()
        
        return {
            "status": "healthy" if (redis_ok and mongo_ok) else "degraded",
            "redis": "ok" if redis_ok else "error",
            "mongodb": "ok" if mongo_ok else "error",
            "queues": queue_stats
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("  FastAPI Market Analysis Server")
    print("="*60)
    print()
    print("Starting on http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
