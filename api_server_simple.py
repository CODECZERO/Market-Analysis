"""
Simple API Server - Using only working components
No complex dependencies, just real Yahoo Finance data + analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Add path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker', 'src'))

# Import only the simple,working comprehensive analysis
from api.comprehensive_analysis import analyze_stock, AnalysisRequest

app = FastAPI(title="Stock Analysis API - Simple Version")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "simple-1.0"}

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    """Analyze stock with real Yahoo Finance data"""
    try:
        result = await analyze_stock(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/popular")
async def get_popular_stocks():
    """Get list of popular Indian stocks"""
    return {
        "stocks": [
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
            {"symbol": "INFY.NS", "name": "Infosys"},
            {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
            {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
            {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
            {"symbol": "ITC.NS", "name": "ITC Limited"},
            {"symbol": "SBIN.NS", "name": "State Bank of India"},
            {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
            {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
