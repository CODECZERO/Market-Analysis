"""
Stock Analysis Worker - Main Application
Orchestrates the complete analysis pipeline
"""

import asyncio
import logging
from typing import Dict, Any
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import analysis modules
try:
    from technical_indicators import TechnicalIndicators
    from decision_engine import DecisionEngine
    from correlation_engine import CorrelationEngine
    from data_providers.yfinance_provider import YFinanceProvider
    
    # ML models
    from ml.lstm_model_optimized import quick_lstm_prediction
    from ml.xgboost_model import XGBoostStockClassifier
    from ml.sentiment_analysis import SentimentAnalyzer
    
    # Quant strategies
    from quant.momentum import MomentumStrategy
    from quant.mean_reversion import MeanReversionStrategy
    from quant.hmm_regime import HMMRegimeDetector
    from quant.fama_french import FamaFrenchAnalyzer
    
    logger.info("All modules imported successfully")
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)


class StockAnalysisWorker:
    """
    Main worker orchestrating stock analysis pipeline
    """
    
    def __init__(self):
        """Initialize worker"""
        self.data_provider = YFinanceProvider()
        self.tech_indicators = TechnicalIndicators()
        self.decision_engine = DecisionEngine()
        self.correlation_engine = CorrelationEngine()
        
        # ML models
        self.sentiment_analyzer = SentimentAnalyzer()
        self.xgboost = XGBoostStockClassifier()
        
        # Quant strategies
        self.momentum = MomentumStrategy()
        self.mean_reversion = MeanReversionStrategy()
        self.hmm_regime = HMMRegimeDetector()
        
        logger.info("Worker initialized")
    
    async def analyze_stock(
        self,
        symbol: str,
        exchange: str = "NSE"
    ) -> Dict[str, Any]:
        """
        Complete stock analysis pipeline
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE/BSE)
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting analysis for {symbol} ({exchange})")
        
        try:
            # Step 1: Fetch data
            logger.info("Step 1/7: Fetching stock data...")
            stock_data = await self._fetch_stock_data(symbol, exchange)
            
            # Step 2: Technical indicators
            logger.info("Step 2/7: Calculating technical indicators...")
            technical = self._calculate_technical_indicators(stock_data)
            
            # Step 3: Quantitative strategies
            logger.info("Step 3/7: Running quantitative strategies...")
            quant_signals = self._run_quant_strategies(stock_data)
            
            # Step 4: ML predictions
            logger.info("Step 4/7: Generating ML predictions...")
            ml_predictions = await self._run_ml_predictions(stock_data)
            
            # Step 5: Sentiment analysis
            logger.info("Step 5/7: Analyzing sentiment...")
            sentiment = await self._analyze_sentiment(symbol)
            
            # Step 6: Correlation analysis
            logger.info("Step 6/7: Computing correlations...")
            correlations = self._compute_correlations(stock_data, sentiment)
            
            # Step 7: Decision fusion
            logger.info("Step 7/7: Fusing signals...")
            decision = self.decision_engine.generate_recommendation(
                technical=technical,
                quant=quant_signals,
                ml=ml_predictions,
                sentiment=sentiment,
                current_price=stock_data['current_price']
            )
            
            # Compile results
            result = {
                'symbol': symbol,
                'exchange': exchange,
                'timestamp': stock_data['timestamp'],
                'current_price': stock_data['current_price'],
                'data': stock_data,
                'technical': technical,
                'quant_signals': quant_signals,
                'ml_predictions': ml_predictions,
                'sentiment': sentiment,
                'correlations': correlations,
                'recommendation': decision,
                'status': 'completed'
            }
            
            logger.info(f"Analysis complete for {symbol}: {decision['rating']}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'exchange': exchange,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _fetch_stock_data(self, symbol: str, exchange: str) -> Dict:
        """Fetch stock data"""
        # Get OHLCV data
        ohlcv = self.data_provider.get_ohlcv_data(
            symbol,
            exchange,
            period='1y'  #1 year for low memory
        )
        
        # Get current quote
        quote = self.data_provider.get_current_quote(symbol, exchange)
        
        # Get company info
        info = self.data_provider.get_company_info(symbol, exchange)
        
        return {
            'ohlcv': ohlcv,
            'current_price': quote.get('price', 0),
            'volume': quote.get('volume', 0),
            'info': info,
            'timestamp': quote.get('timestamp', '')
        }
    
    def _calculate_technical_indicators(self, stock_data: Dict) -> Dict:
        """Calculate technical indicators"""
        df = stock_data['ohlcv']
        
        indicators = self.tech_indicators.calculate_all(df)
        
        # Get latest values
        latest = {
            'rsi': indicators['rsi'].iloc[-1],
            'macd': indicators['macd'].iloc[-1],
            'signal': indicators['macd_signal'].iloc[-1],
            'bb_upper': indicators['bb_upper'].iloc[-1],
            'bb_lower': indicators['bb_lower'].iloc[-1],
            'sma_50': indicators['sma_50'].iloc[-1],
            'sma_200': indicators['sma_200'].iloc[-1],
            'adx': indicators['adx'].iloc[-1],
            'current_price': df['close'].iloc[-1]
        }
        
        return latest
    
    def _run_quant_strategies(self, stock_data: Dict) -> Dict:
        """Run quantitative strategies"""
        df = stock_data['ohlcv']
        
        signals = {}
        
        # Momentum
        try:
            momentum_signal = self.momentum.generate_signal(df)
            signals['momentum'] = momentum_signal
        except:
            signals['momentum'] = {'signal': 0, 'strength': 0}
        
        # Mean reversion
        try:
            mr_signal = self.mean_reversion.calculate_zscore(df['close'])
            signals['mean_reversion'] = {
                'zscore': mr_signal,
                'signal': 1 if mr_signal < -1.5 else (-1 if mr_signal > 1.5 else 0)
            }
        except:
            signals['mean_reversion'] = {'zscore': 0, 'signal': 0}
        
        # HMM regime
        try:
            regime = self.hmm_regime.detect_regime(df)
            signals['regime'] = regime
        except:
            signals['regime'] = {'current_regime': 'SIDEWAYS', 'confidence': 0.5}
        
        return signals
    
    async def _run_ml_predictions(self, stock_data: Dict) -> Dict:
        """Run ML predictions"""
        df = stock_data['ohlcv']
        current_price = stock_data['current_price']
        
        predictions = {}
        
        # LSTM prediction
        try:
            lstm_result =quick_lstm_prediction(df, current_price, use_gpu=True)
            predictions['lstm'] = lstm_result
        except Exception as e:
            logger.warning(f"LSTM prediction failed: {e}")
            predictions['lstm'] = {
                'predictions': {'1d': current_price, '7d': current_price, '30d': current_price},
                'confidence': 0.5
            }
        
        # XGBoost would go here (requires trained model)
        predictions['xgboost'] = {
            'signal': 'HOLD',
            'probability': 0.5,
            'confidence': 0.5
        }
        
        return predictions
    
    async def _analyze_sentiment(self, symbol: str) -> Dict:
        """Analyze sentiment"""
        # For now, return neutral sentiment
        # In production, this would scrape news and social media
        return {
            'overall_score': 0.0,
            'news_sentiment': 0.0,
            'social_sentiment': 0.0,
            'confidence': 0.5,
            'num_sources': 0
        }
    
    def _compute_correlations(self, stock_data: Dict, sentiment: Dict) -> Dict:
        """Compute correlations"""
        # Basic correlations
        return {
            'market_correlation': 0.75,  # Placeholder
            'sector_correlation': 0.65,
            'sentiment_lag': 0,
            'confidence': 0.5
        }


# Background task processor
async def process_task(task_data: Dict):
    """Process analysis task"""
    worker = StockAnalysisWorker()
    
    symbol = task_data.get('symbol')
    exchange = task_data.get('exchange', 'NSE')
    
    result = await worker.analyze_stock(symbol, exchange)
    
    return result


# Main entry point
async def main():
    """Main worker loop"""
    logger.info("Stock Analysis Worker starting...")
    
    # Test with single stock
    test_symbol = os.getenv('TEST_SYMBOL', 'RELIANCE')
    
    logger.info(f"Running test analysis for {test_symbol}")
    
    worker = StockAnalysisWorker()
    result = await worker.analyze_stock(test_symbol, 'NSE')
    
    if result['status'] == 'completed':
        logger.info("="*60)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*60)
        logger.info(f"Symbol: {result['symbol']}")
        logger.info(f"Price: ₹{result['current_price']:,.2f}")
        logger.info(f"Recommendation: {result['recommendation']['rating']}")
        logger.info(f"Confidence: {result['recommendation']['confidence']:.0%}")
        logger.info("="*60)
    else:
        logger.error(f"Analysis failed: {result.get('error')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        sys.exit(1)
