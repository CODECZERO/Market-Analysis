"""
PRODUCTION API SERVER - COMPLETE INTEGRATION
Uses full orchestrator with all components:
- LLM Ensemble (NVIDIA + Groq)
- ML Models (LSTM + XGBoost)
- Wall Street Quant Algorithms
- Correlation Engine
- Decision Engine
- Sector Analysis
- News Impact Analysis
- Sentiment Aggregation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
import asyncio
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker', 'src'))

app = FastAPI(
    title="Stock Analysis API - Production",
    description="Complete stock analysis with LLM, ML, and Quant strategies",
    version="2.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import components
try:
    from orchestrator_enhanced import StockAnalysisOrchestrator
    print("✅ Orchestrator loaded")
    ORCHESTRATOR_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Orchestrator unavailable: {e}")
    ORCHESTRATOR_AVAILABLE = False

try:
    from services.stock_screener import StockScreener, get_top_stocks
    print("✅ Stock Screener loaded")
    SCREENER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Screener unavailable: {e}")
    SCREENER_AVAILABLE = False

try:
    from services.portfolio_tracker import Portfolio
    PORTFOLIO_AVAILABLE = True
except:
    PORTFOLIO_AVAILABLE = False

try:
    from services.alerts_manager import AlertsManager
    ALERTS_AVAILABLE = True
except:
    ALERTS_AVAILABLE = False

# Fallback simple analysis
try:
    from api.comprehensive_analysis import analyze_stock as simple_analyze
    SIMPLE_ANALYSIS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Simple analysis unavailable: {e}")
    SIMPLE_ANALYSIS_AVAILABLE = False

# Request Models
class ComprehensiveAnalysisRequest(BaseModel):
    symbol: str
    use_llm: bool = True
    use_ml: bool = True
    use_quant: bool = True
    use_ensemble: bool = True
    use_scrapers: bool = True

class SimpleAnalysisRequest(BaseModel):
    symbol: str

# Global orchestrator instance
_orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None and ORCHESTRATOR_AVAILABLE:
        _orchestrator = StockAnalysisOrchestrator()
    return _orchestrator


@app.get("/api/health")
async def health_check():
    """Health check with component status"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "orchestrator": ORCHESTRATOR_AVAILABLE,
            "stock_screener": SCREENER_AVAILABLE,
            "portfolio_tracker": PORTFOLIO_AVAILABLE,
            "alerts_manager": ALERTS_AVAILABLE,
            "simple_analysis": SIMPLE_ANALYSIS_AVAILABLE
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze/comprehensive")
async def analyze_comprehensive(request: ComprehensiveAnalysisRequest):
    """
    COMPLETE STOCK ANALYSIS
    
    Uses orchestrator to coordinate:
    - LLM Ensemble (NVIDIA + Groq multi-phase reasoning)
    - ML Models (LSTM price predictions, XGBoost signals)
    - Quant Strategies (Momentum, Mean Reversion, HMM)
    - Correlation Analysis (price, sentiment, volume, news)
    - Sector Analysis (rotation detection)
    - News Impact Analysis
    - Decision Engine (multi-signal fusion)
    - Sentiment Aggregation (Twitter, Reddit, News)
    """
    try:
        if not ORCHESTRATOR_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not available. Install missing dependencies."
            )
        
        orchestrator = get_orchestrator()
        
        # Run complete analysis
        result = await orchestrator.analyze_stock(
            symbol=request.symbol,
            use_llm=request.use_llm,
            use_scrapers=request.use_scrapers,
            use_ensemble=request.use_ensemble
        )
        
        # Add metadata
        result['api_version'] = '2.0.0'
        result['analysis_timestamp'] = datetime.now().isoformat()
        result['components_used'] = {
            'llm_ensemble': request.use_llm and request.use_ensemble,
            'ml_models': request.use_ml,
            'quant_strategies': request.use_quant,
            'sentiment_aggregation': request.use_scrapers
        }
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR in comprehensive analysis: {e}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/simple")
async def analyze_simple(request: SimpleAnalysisRequest):
    """
    SIMPLE STOCK ANALYSIS
    
    Uses basic comprehensive_analysis module (no orchestrator)
    - Yahoo Finance data
    - Technical indicators
    - Basic recommendations
    """
    try:
        if not SIMPLE_ANALYSIS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Simple analysis not available"
            )
        
        # Use simple analysis
        from api.comprehensive_analysis import AnalysisRequest
        simple_req = AnalysisRequest(symbol=request.symbol)
        result = await simple_analyze(simple_req)
        
        result['api_version'] = '2.0.0-simple'
        result['analysis_timestamp'] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/stocks/screen")
async def screen_stocks(timeframe: str = "long", limit: int = 10):
    """
    AUTO STOCK SCREENING
    
    Analyzes all Nifty 50 stocks and returns top recommendations
    """
    try:
        if not SCREENER_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Stock screener not available"
            )
        
        results = get_top_stocks(timeframe=timeframe)
        
        return {
            "timeframe": timeframe,
            "top_stocks": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")


@app.get("/api/stocks/popular")
async def get_popular_stocks():
    """Get list of popular Indian stocks"""
    return {
        "stocks": [
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT"},
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy"},
            {"symbol": "INFY.NS", "name": "Infosys", "sector": "IT"},
            {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
            {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"},
            {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG"},
            {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "FMCG"},
            {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking"},
            {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom"},
            {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking"},
            {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure"},
            {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "IT"},
            {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Auto"},
            {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "sector": "Pharma"},
            {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer"},
            {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "IT"},
            {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "sector": "Cement"},
            {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Paints"},
            {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "FMCG"},
            {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking"}
        ]
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    print("\n" + "="*70)
    print("  STOCK ANALYSIS API - PRODUCTION v2.0.0")
    print("="*70)
    print("\nComponent Status:")
    print(f"  Orchestrator: {'✅' if ORCHESTRATOR_AVAILABLE else '❌'}")
    print(f"  Stock Screener: {'✅' if SCREENER_AVAILABLE else '❌'}")
    print(f"  Portfolio Tracker: {'✅' if PORTFOLIO_AVAILABLE else '❌'}")
    print(f"  Alerts Manager: {'✅' if ALERTS_AVAILABLE else '❌'}")
    print(f"  Simple Analysis: {'✅' if SIMPLE_ANALYSIS_AVAILABLE else '❌'}")
    
    if ORCHESTRATOR_AVAILABLE:
        print("\n✅ Full orchestrator pipeline available!")
        print("   - LLM Ensemble (NVIDIA + Groq)")
        print("   - ML Models (LSTM + XGBoost)")
        print("   - Quant Strategies (Momentum, HMM, Mean Reversion)")
        print("   - Correlation Engine")
        print("   - Decision Engine")
        print("   - Sector Analysis")
    else:
        print("\n⚠️  Orchestrator unavailable - using simple analysis")
    
    print("\n" + "="*70)
    print("API Endpoints:")
    print("  POST /api/analyze/comprehensive - Full analysis with all components")
    print("  POST /api/analyze/simple - Basic analysis")
    print("  GET  /api/stocks/screen - Auto stock screening")
    print("  GET  /api/stocks/popular - Popular stocks list")
    print("  GET  /api/health - Health check")
    print("="*70 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
