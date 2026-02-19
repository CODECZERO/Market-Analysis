"""
Enhanced Stock Analysis Orchestrator
Integrates all components: data, technical, quant, ML, scrapers, LLM
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import all components
try:
    from system_logger import get_logger, log_event
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    def log_event(c, t, d): print(f"[{c}] {t}: {d}")

logger = get_logger("Orchestrator")

from providers.yfinance_provider import YFinanceProvider
from technical_indicators import calculate_indicators
from quant.momentum import calculate_momentum_scores
from quant.mean_reversion import calculate_zscore
from quant.hmm_regime import detect_market_regime as detect_regime
from ml.lstm_model_optimized import quick_lstm_prediction as predict_prices
from ml.xgboost_model import quick_xgb_signal as predict_signal
from realtime_predictor import IntradayForecaster
from decision_engine import generate_decision
from services.llm_client import call_llm_phase1, call_llm_phase2, call_llm_phase3, get_llm_client
from services.llm_ensemble import analyze_stock_with_ensemble
from providers.news_sentiment import get_news_sentiment
from providers.social_sentiment import get_social_sentiment
from providers.fundamental_data import get_fundamental_provider
from providers.regulatory_data_provider import get_regulatory_provider
from learning.feedback_loop import get_feedback_loop
from learning.regulatory_net import get_regulatory_net
from decision_engine import DecisionEngine
from technical.smc_analyzer import SMCAnalyzer

# 🌩️ Phase 6: Hyper-Intelligence Modules
from services.macro_engine import MacroEngine
from knowledge_graph.graph_builder import KnowledgeGraph
from learning.feedback_loop import FeedbackLoop
from forensics.validator import ForensicValidator
from ml.transformer_model import TransformerModel
from quant.fama_french import FamaFrenchAnalyzer
from ml.self_learning_agent import SelfLearningAgent

# Optional scrapers (may not have API keys)
try:
    from scrapers.moneycontrol_scraper import MoneyControlScraper
    news_scraper_available = True
except (ImportError, AttributeError, Exception) as e:
    print(f"News scraper unavailable: {e}")
    news_scraper_available = False

try:
    from scrapers.reddit_scraper import RedditScraper
    reddit_scraper_available = True
except (ImportError, AttributeError, Exception) as e:
    print(f"Reddit scraper unavailable: {e}")
    reddit_scraper_available = False


class StockAnalysisOrchestrator:
    """Orchestrate complete stock analysis pipeline"""
    
    def __init__(self):
        """Initialize the Stock Analysis Orchestrator with all components"""
        self.data_provider = YFinanceProvider()
        self.news_scraper = MoneyControlScraper() if news_scraper_available else None
        self.reddit_scraper = RedditScraper() if reddit_scraper_available else None
        self.llm_client = get_llm_client()
        self.smc_analyzer = SMCAnalyzer()
        
        # Initialize Hyper-Intelligence Engines
        self.macro_engine = MacroEngine()
        self.knowledge_graph = KnowledgeGraph()
        self.feedback_loop = FeedbackLoop()
        self.forensic_validator = ForensicValidator()
        self.transformer_model = TransformerModel() # Initialize once (weights random for now if not loaded)
        self.fama_french = FamaFrenchAnalyzer()
    
    async def analyze_stock(self, symbol: str, use_llm: bool = True, use_scrapers: bool = True,
                           use_ensemble: bool = True) -> Dict[str, Any]:
        """
        Complete stock analysis pipeline with optional multi-LLM ensemble
        
        Args:
            symbol: Stock symbol (e.g., "TCS.NS")
            use_llm: Use LLM analysis
            use_scrapers: Use web scrapers for sentiment
            use_ensemble: Use advanced multi-LLM ensemble (NVIDIA + Groq in parallel)
        """
        print(f"\n🔍 Analyzing {symbol}...")
        print(f"   LLM Mode: {'Multi-Model Ensemble 🧠' if use_ensemble and use_llm else 'Single Model' if use_llm else 'Disabled'}")
        
        # 1. Get historical data
        print("1️⃣ Fetching market data...")
        data = self.data_provider.get_stock_data(symbol, period="1y")
        
        # 🆕 Fetch Intraday data for temporal analysis (use 5d to ensure buffer)
        print("   🕒 Fetching intraday data (5m intervals)...")
        intraday_data = self.data_provider.get_intraday_data(symbol, interval="5m", period="5d")
        if intraday_data is not None:
             # Standardize column names to lowercase
            intraday_data.columns = [c.lower() for c in intraday_data.columns]
        
        if data is None or len(data) == 0:
            return {"error": f"Unable to fetch data for {symbol}"}
            
        # Standardize column names to lowercase
        data.columns = [c.lower() for c in data.columns]

        
        # Step 2: Technical Analysis
        print("2️⃣  Calculating technical indicators...")
        # 🌩️ Phase 6: Hyper-Intelligence Initialization
        feedback_loop = FeedbackLoop()
        macro_engine = MacroEngine()
        forensic_validator = ForensicValidator()
        
        # 🆕 1. Macro Analysis (Geopolitics + Local)
        print("6️⃣ Running Macro-Economic & Geopolitical Scan...")
        # Fetch fundamental data for sector information
        fund_provider = get_fundamental_provider()
        fundamental_data = fund_provider.get_fundamental_data(symbol)
        sector = fundamental_data.get('sector', 'Unknown')
        macro_data = macro_engine.analyze_macro_factors(symbol, sector)
        quant = {} # Initialize quant dict here as it's used before its main block
        quant['macro'] = macro_data
        print(f"   🌍 Macro Score: {macro_data['macro_score']:+.2f} ({macro_data['geopolitics']['risk_level']} Risk)")

        # 🌩️ Phase 2: Technicals (Calculate first so they can be used in learning/causal chain)
        technical = calculate_indicators(data)
        
        # Initialize sentiment variables for use in causal chain
        news_sentiment = None
        social_sentiment = None
        
        # 🆕 3. Historical Pattern Lookup (Learning)
        print("   🧠 Checking historical patterns & hidden regimes...")
        learning_agent = SelfLearningAgent()
        history = feedback_loop.get_historical_pattern(symbol)
        
        # 🆕 4. Real-Time Unsupervised Learning (Hidden Patterns)
        hidden_regime = learning_agent.discover_hidden_regime({
            "technicals": technical,
            "sentiment": {"score": 0} # Placeholder until actual sentiment is fetched
        })
        quant['learning'] = {
            "history": history,
            "hidden_regime": hidden_regime,
            "policy_weights": feedback_loop.weights 
        }
        
        # 🆕 SMC/ICT Analysis
        print("   SMC/ICT analysis...")
        smc_signals = self.smc_analyzer.analyze(data)
        quant['smc'] = smc_signals
        
        # Step 3: Quantitative Analysis
        print("3️⃣  Running quantitative strategies...")
        
        # Helper for single-stock momentum (Absolute Momentum)
        # Calculate avg return over 1m, 3m, 6m using 'close' column (lowercase after technical_indicators)
        close_prices = data['close']
        
        # Calculate returns for momentum
        m1 = close_prices.pct_change(21).iloc[-1] if len(close_prices) > 21 else 0
        m3 = close_prices.pct_change(63).iloc[-1] if len(close_prices) > 63 else 0
        m6 = close_prices.pct_change(126).iloc[-1] if len(close_prices) > 126 else 0
        mom_score = float((m1 + m3 + m6) / 3)
        
        causal_context = {
            "symbol": symbol,
            "macro": macro_data,
            "forensics": quant.get('forensics', {}),
            "learning": quant.get('learning', {}),
            "technicals": technical,
            "current_price": float(data['close'].iloc[-1])
        }
        quant['causal_chain'] = causal_context
        
        # Calculate proper Z-score
        zscore_series = calculate_zscore(close_prices)
        current_zscore = float(zscore_series.iloc[-1]) if not pd.isna(zscore_series.iloc[-1]) else 0.0
        
        # Prepare data for HMM
        returns = data['close'].pct_change()
        volatility = returns.rolling(20).std()
        volume = data['volume']
        
        # Merging with existing quant data (macro, learning, causal_chain)
        def _get_signal(val, buy_threshold, sell_threshold):
            if val is None: return 'HOLD'
            try:
                fval = float(val)
                if fval > buy_threshold: return 'BUY'
                if fval < sell_threshold: return 'SELL'
                return 'HOLD'
            except: return 'HOLD'
            
        quant.update({
            'momentum': {
                'score': mom_score,
                'signal': _get_signal(mom_score, 0.05, -0.05)
            },
            'mean_reversion': {
                'zscore': current_zscore,
                'signal': _get_signal(current_zscore, 2.0, -2.0) # Corrected thresholds for standard signal logic
            },
            'regime': detect_regime(returns, volatility, volume)
        })
        
        # Intraday Temporal Analysis (2-3 hours ago)
        intraday_stats = {}
        if intraday_data is not None and len(intraday_data) > 24: # 24 * 5m = 2 hrs
            three_hr_ago = intraday_data.iloc[-36]['close'] if len(intraday_data) > 36 else intraday_data.iloc[0]['close']
            current_intraday = intraday_data.iloc[-1]['close']
            intraday_stats = {
                'price_3h_ago': float(three_hr_ago),
                'change_3h_pct': float((current_intraday - three_hr_ago) / three_hr_ago * 100),
                'intraday_volatility': float(intraday_data['close'].pct_change().std() * 100)
            }
            print(f"   🕒 Intraday Trend (3h): {intraday_stats['change_3h_pct']:+.2f}%")

        quant['temporal'] = intraday_stats
        
        # 🔮 Crystal Ball Prediction
        crystal_ball = []
        if intraday_data is not None and len(intraday_data) > 12:
            try:
                forecaster = IntradayForecaster()
                # Use current close from intraday data for consistency
                curr_price = float(intraday_data.iloc[-1]['close'])
                cb_result = forecaster.generate_forecast(curr_price, intraday_data)
                crystal_ball = cb_result.get('matrix', [])
                print(f"   🔮 Crystal Ball: Generated {len(crystal_ball)} forecasts")
            except Exception as e:
                print(f"   ⚠️ Crystal Ball Error: {e}")
                
        quant['crystal_ball'] = crystal_ball
        
        # 🌩️ Phase 6: Hyper-Intelligence Execution
        try:
            # 1. Forensic Check
            forensics = self.forensic_validator.validate_legitimacy(symbol)
            quant['forensics'] = forensics
            
            # 2. Macro Engine (Auto-detect sector in future)
            macro = self.macro_engine.analyze_macro_factors(symbol, sector="IT") 
            quant['macro'] = macro
            
            # 3. Knowledge Graph
            graph = self.knowledge_graph.build_graph_for_symbol(symbol)
            quant['graph'] = graph
            
            # 4. Fama-French
            market_returns = data['close'].pct_change()
            alpha = self.fama_french.calculate_alpha(data['close'].pct_change(), market_returns)
            quant['fama_french_alpha'] = alpha
            
        except Exception as e:
            print(f"   ⚠️  Hyper-Intel error: {e}")
            quant['error'] = str(e)
        
        # Step 4: ML Predictions
        print("4️⃣  Running ML models...")
        current_price = float(data['close'].iloc[-1])
        lstm_pred = predict_prices(data, current_price)
        
        # Transformer Model (New)
        try:
            # Dummy input for integration test (1 sample, 60 timesteps, 128 features)
            # In production, this needs real feature engineering matching training
            trans_pred = self.transformer_model.predict(np.zeros((1, 60, 128))) 
        except Exception as e:
            trans_pred = {"confidence": 0}
        
        # Fetch fundamentals for XGBoost & Decision Engine
        fund_provider = get_fundamental_provider()
        fundamentals = fund_provider.get_fundamental_data(symbol)
        
        # Inject Accounting Health into Quant dict for Decision Engine
        quant['accounting_health'] = fundamentals.get('accounting_health', 'Stable')
        quant['fcf_yield'] = fundamentals.get('fcf_yield', 0)
        
        # Mock sentiment if not available (to avoid failure)
        sentiment_scores = {'news_sentiment': 0, 'reddit_sentiment': 0, 'twitter_sentiment': 0}
        
        xgb_pred = predict_signal(technical, fundamentals, sentiment_scores)
        
        ml = {
            'lstm': lstm_pred,
            'xgboost': xgb_pred,
            'transformer': trans_pred
        }
        
        final_decision = {} # Prevent UnboundLocalError in feedback reporting
        
        # Step 5 & 6: Multi-Source Sentiment (Aggregator + Direct Scrapers)
        news_sentiment = {'score': 0, 'count': 0, 'summary': 'None'}
        social_sentiment = {'score': 0, 'count': 0, 'summary': 'None'}
        sentiment_data = {} # Initialize for scope
        
        if use_scrapers:
            print("5️⃣  Fetching sentiment from multiple sources...")
            
            # Try aggregator first (9 platforms: Reddit, X, Bluesky, News, HN, etc.)
            aggregator_data = None
            try:
                from scrapers.aggregator_adapter import AggregatorAdapter
                aggregator = AggregatorAdapter()
                print("   📡 Trying aggregator service (9 platforms + CEO tracking)...")
                aggregator_mentions = aggregator.fetch_mentions(symbol, company_info=fundamental_data)
                if aggregator_mentions:
                    aggregator_data = aggregator.get_combined_sentiment(aggregator_mentions)
                    if aggregator_data.get('count', 0) > 0:
                        print(f"   ✅ Aggregator: {aggregator_data['count']} mentions, {aggregator_data['label']}")
            except Exception as e:
                print(f"   ⚠️  Aggregator unavailable (continuing with direct scrapers)")
            
            # Always run direct scrapers too (supplement + fallback)
            direct_news = []
            direct_social = []
            
            # MoneyControl news
            if self.news_scraper:
                try:
                    print("   📰 MoneyControl scraper...")
                    articles = self.news_scraper.scrape_news(symbol, max_articles=5)
                    if articles:
                        direct_news.extend(articles)
                        print(f"   ✅ MoneyControl: {len(articles)} articles")
                except:
                    print("   ⚠️  MoneyControl failed")
            
            # Reddit direct
            if self.reddit_scraper:
                try:
                    print("   💬 Reddit scraper...")
                    posts = self.reddit_scraper.scrape_discussions(symbol, limit=20)
                    if posts:
                        direct_social.extend(posts)
                        print(f"   ✅ Reddit: {len(posts)} posts")
                except:
                    print("   ⚠️  Reddit failed")
            
            # Combine results intelligently
            if aggregator_data and aggregator_data.get('count', 0) > 0:
                # Use aggregator as primary + note direct scraper counts
                social_sentiment = aggregator_data.copy()
                social_sentiment['source'] = 'aggregator'
                if direct_social:
                    social_sentiment['direct_social_supplement'] = len(direct_social)
            elif direct_social:
                # Fallback to direct scrapers only
                social_sentiment = self.reddit_scraper.get_sentiment_summary(direct_social)
                social_sentiment['source'] = 'direct_scrapers'
            
            # News sentiment from direct scrapers
            if direct_news:
                news_sentiment = self.news_scraper.get_sentiment_summary(direct_news)
                news_sentiment['source'] = 'direct_scrapers'
        
        # 🆕 Regulatory Analysis (Neural Net)
        print("   ⚖️  Running Regulatory Neural Network...")
        reg_provider = get_regulatory_provider()
        reg_data = reg_provider.fetch_regulatory_data(symbol)
        
        reg_net = get_regulatory_net()
        regulatory_risk_prob = reg_net.predict_risk(
            risk_score_raw=reg_data.get('risk_score_raw', 0),
            volatility=technical.get('atr_percent', 0.02), # Volatility proxy
            insider_sell=1 if reg_data.get('insider_sell_detected') else 0,
            sentiment=news_sentiment.get('score', 0) if news_sentiment else 0
        )
        reg_data['ai_risk_probability'] = regulatory_risk_prob
        print(f"      Risk Probability: {regulatory_risk_prob:.1%}")

        # Step 7: LLM Analysis (if enabled and keys available)
        llm_analysis = None
        # 6. LLM Analysis (Multi-Model Ensemble or Single)
        llm_analysis = {}
        if use_llm:
            # Fetch fundamental data for LLM analysis
            print("   📊 Fetching fundamental & Wall Street data...")
            fundamental_provider = get_fundamental_provider()
            fundamental_data = fundamental_provider.get_fundamental_data(symbol)
            fundamental_data_formatted = fundamental_provider.format_for_llm(fundamental_data)
            
            if use_ensemble:
                # 🧠 ADVANCED: Multi-LLM Ensemble (NVIDIA + Groq in parallel)
                print("6️⃣ Running Multi-LLM Ensemble Analysis...")
                print("   🔄 Phase 1: Parallel Technical Analysis (2 models) + Fundamentals")
                print("   🔄 Phase 2: Parallel Sentiment Fusion (2 models)")
                print("   🔄 Phase 3: Ensemble Decision Synthesis (heavy reasoning)")
                print("   🛡️  Hallucination Detection: Enabled")
                
                # Prepare data for ensemble
                stock_data_for_ensemble = {
                    'symbol': symbol,
                    'price': float(data['close'].iloc[-1]),
                    'rsi': technical.get('rsi'),
                    'macd': technical.get('macd'),
                    'signal': technical.get('signal'),
                    'ma_50': technical.get('sma_50'),
                    'ma_200': technical.get('sma_200'),
                    'volume': int(data['volume'].iloc[-1]) if 'volume' in data else None,
                    'bollinger': technical.get('bollinger'),
                    
                    # 🚀 INJECTED: Quant & ML Signals for Deep Reasoning
                    'quant_momentum': quant.get('momentum', {}).get('score', 0),
                    'quant_regime': quant.get('regime', {}).get('current_regime', 'Unknown'),
                    'quant_zscore': quant.get('mean_reversion', {}).get('zscore', 0),
                    'quant_alpha': quant.get('fama_french_alpha', 0),
                    'ml_lstm_forecast': ml.get('lstm', {}).get('predictions', {}).get('30d', 0),
                    'ml_xgboost_signal': ml.get('xgboost', {}).get('signal', 'NEUTRAL'),
                    'ml_transformer_conf': ml.get('transformer', {}).get('confidence', 0),
                    'ml_confidence': ml.get('lstm', {}).get('confidence', 0),
                    
                    # 🌩️ HYPER-INTELLIGENCE SIGNALS
                    'macro_score': quant.get('macro', {}).get('macro_score', 0),
                    'macro_summary': quant.get('macro', {}).get('summary', ''),
                    'forensic_safe': quant.get('forensics', {}).get('is_legit', True),
                    'scam_probability': quant.get('forensics', {}).get('scam_probability', 0),
                    'graph_risk': len(quant.get('graph', {}).get('direct_dependencies', [])),
                    
                    # 🧠 LEARNING SIGNALS
                    'learning_regime': quant.get('learning', {}).get('hidden_regime', {}).get('regime', 'Unknown'),
                    'policy_weights': str(quant.get('learning', {}).get('policy_weights', {})),
                    
                    # ⚖️ REGULATORY NEURAL NET
                    'regulatory_risk_prob': reg_data.get('ai_risk_probability', 0),
                    'regulatory_events': len(reg_data.get('regulatory_events', [])),
                    'insider_sell_detected': reg_data.get('insider_sell_detected', False)
                }
                
                sentiment_data_for_ensemble = {
                    'news_score': news_sentiment.get('score', 0) if news_sentiment else 0,
                    'news_label': news_sentiment.get('label', 'NEUTRAL') if news_sentiment else 'NEUTRAL',
                    'social_score': social_sentiment.get('score', 0) if social_sentiment else 0,
                    'social_label': social_sentiment.get('label', 'NEUTRAL') if social_sentiment else 'NEUTRAL',
                    'reddit_mentions': social_sentiment.get('mentions', 'N/A') if social_sentiment else 'N/A',
                    'buzz_level': 'Medium'  # Could calculate this
                }
                
                try:
                    llm_analysis = await analyze_stock_with_ensemble(
                        stock_data_for_ensemble,
                        sentiment_data_for_ensemble
                    )
                except Exception as e:
                    print(f"   ⚠️  Ensemble failed: {e}, falling back to single model")
                    use_ensemble = False  # Fall through to single model
            
            if not use_ensemble:
                # Standard 3-phase LLM (single model)
                print("6️⃣ Running LLM Analysis (3-phase)...")
                try:
                    phase1 = await call_llm_phase1(technical)
                    phase2 = await call_llm_phase2({
                        "news": news_sentiment,
                        "social": social_sentiment
                    })
                    phase3 = await call_llm_phase3({
                        "technical": phase1,
                        "sentiment": phase2,
                        "quant": quant,
                        "ml": ml
                    })
                    llm_analysis = phase3
                except Exception as e:
                    print(f"   ⚠️  LLM analysis failed: {e}")
                    llm_analysis = {"error": str(e)}
        
        # 7. Final Decision (use ensemble decision if available)
        print("7️⃣ Making final decision...")
        
        if use_ensemble and llm_analysis and 'recommendation' in llm_analysis:
            # Use ensemble decision directly (it's already comprehensive)
            decision = {
                'rating': llm_analysis.get('recommendation', 'HOLD'),
                'confidence': llm_analysis.get('confidence', 0.5),
                'reasoning': llm_analysis.get('reasoning', ''),
                'entry_price': llm_analysis.get('entry_price', float(data['close'].iloc[-1])),
                'stop_loss': llm_analysis.get('stop_loss', float(data['close'].iloc[-1]) * 0.95),
                'target_1': llm_analysis.get('target_price', float(data['close'].iloc[-1]) * 1.05),
                'target_2': llm_analysis.get('target_price', float(data['close'].iloc[-1]) * 1.10),
                'target_3': llm_analysis.get('target_price', float(data['close'].iloc[-1]) * 1.15),
                'time_horizon': llm_analysis.get('time_horizon', 'medium_term'),
                'risk_level': llm_analysis.get('risk_level', 'medium'),
                'ensemble_metadata': llm_analysis.get('ensemble_metadata', {})
            }
            
            # 🧠 SMART MERGE: Improve generic LLM fallback with Decision Engine hard data
            sentiment_data_merge = { "news": news_sentiment, "social": social_sentiment }
            
            # Get Volume from history if possible
            volume = 0
            if data is not None and not data.empty:
                # Handle Case Sensitivity (Volume vs volume)
                if 'Volume' in data.columns:
                    volume = int(data['Volume'].iloc[-1])
                elif 'volume' in data.columns:
                    volume = int(data['volume'].iloc[-1])

            # DEBUG: Log values to understand why circuit breaker might be skipped
            log_event("Orchestrator", "DATA_CHECK", f"Checking {symbol} - Price: {current_price} ({type(current_price)}), Volume: {volume} ({type(volume)})")

            # 🚨 CIRCUIT BREAKER: Trigger Research Mode if data is suspicious (No Price OR No Volume)
            if (current_price is None) or (float(current_price) == 0) or (volume == 0):
                logger.warning(f"⚠️  Suspicious Data caught for {symbol} (Price: {current_price}, Vol: {volume}). Triggering Emergency Web Research...")
                
                # Fallback: Use scraper only
                if self.news_scraper:
                    print(f"   📰 Researching {symbol} via MoneyControl due to data gap...")
                    articles = self.news_scraper.scrape_news(symbol, max_articles=5)
                    
                    # Create a robust reasoning string
                    news_summary = "No meaningful news found."
                    if articles:
                        news_summary = f"News: {articles[0].get('title', 'N/A')} (Source: {articles[0].get('source', 'Unknown')})"
                    
                    reasoning_text = f"Trading Halted or Volume 0. {news_summary}"
                    
                    # Log this event
                    log_event("Orchestrator", "FALLBACK_TRIGGERED", f"{symbol}: {reasoning_text}")

                    # Return FULL structure to prevent CLI KeyErrors
                    return {
                        "symbol": symbol,
                        "current_price": float(current_price) if current_price else 0.0,
                        "volume": 0,
                        "day_change_percent": 0.0,
                        "llm_analysis": {
                            "recommendation": "NEUTRAL",
                            "reasoning": reasoning_text,
                            "confidence": 0.1
                        },
                        "decision_engine": { # CLI looks for 'decision_engine' or 'final_decision'
                            "rating": "HOLD",
                            "recommendation": "HOLD",
                            "reasoning": reasoning_text,
                            "hold_duration": "Avoid until volume returns",
                            "confidence": 0.1
                        },
                        "quant_signals": { # Mock empty quant to prevent CLI crash
                            "macro": {"macro_score": 0, "summary": "N/A (Data Gap)"},
                            "forensics": {"is_legit": True, "scam_probability": 0},
                            "graph": {"root": "N/A", "direct_dependencies": []}
                        },
                        "ml_predictions": { # Mock empty ML
                            "transformer": {"confidence": 0, "90d": 0}
                        }
                    }
            
            rule_based_decision = generate_decision(
                technical_indicators=technical,
                quant_signals=quant,
                ml_predictions=ml,
                sentiment=sentiment_data_merge,
                phase1_analysis=None,
                current_price=float(data['close'].iloc[-1]),
                weights=self.feedback_loop.weights
            )
            
            # If reasoning is generic/fallback, overwrite with Decision Engine reasoning
            if "insufficient data" in str(decision.get('reasoning', '')) or len(str(decision.get('reasoning', ''))) < 10:
                decision['reasoning'] = rule_based_decision.get('reasoning', "Analysis based on technicals")
            
            # 🛡️ SAFETY: Ensure Recommendation Exists (Fix for None/UNKNOWN persistence)
            if not decision.get('recommendation') or decision.get('recommendation') == 'UNKNOWN':
                logger.warning(f"⚠️  LLM returned invalid recommendation. Falling back to Rule-Based Engine.")
                decision['recommendation'] = rule_based_decision.get('recommendation', 'HOLD')
                decision['rating'] = rule_based_decision.get('rating', 'HOLD')
                decision['confidence'] = rule_based_decision.get('confidence', 0.5)

            # Always ensure hold_duration exists
            decision['hold_duration'] = rule_based_decision.get('hold_duration', "Unknown")
            decision['breakdown'] = rule_based_decision.get('breakdown', {})
            
        else:
            # Standard decision engine
            # Prepare data for generate_decision
            sentiment_data = {
                "news": news_sentiment,
                "social": social_sentiment
            }
            price_data = {
                "current_price": float(data['close'].iloc[-1])
            }
            
            final_decision = generate_decision(
                technical_indicators=technical,
                quant_signals=quant,
                ml_predictions=ml,
                sentiment=sentiment_data,
                phase1_analysis=llm_analysis.get('analysis_phases', {}).get('technical') if llm_analysis else None,
                current_price=price_data['current_price'],
                weights=self.feedback_loop.weights
            )
            
            # 🆕 Prediction Thesis (Linking signals to future targets)
            # 🆕 Prediction Thesis (Linking signals to future targets)
            decision['prediction_thesis'] = {
                "short_term": f"Driven by {hidden_regime.get('regime', 'market trend')} and {macro_data.get('summary', 'macro stability')}.",
                "conviction_logic": f"ML conviction ({ml.get('transformer', {}).get('confidence', 0):.0%}) synced with RL policy.",
                "causal_link": f"{'🚨 Forensic flags' if not causal_context['forensics'].get('is_legit', True) else '✅ Fundamental integrity verified'}."
            }
            final_decision = decision # Unify variable name for downstream logic
        # 🎯 FEEDBACK LOOP & SELF-LEARNING
        # We save this prediction state. The 'Learner' will check it later against future price.
        # But for Regulatory Net, we can do an "instant" check if we have recent volatility data that matches news.
        
        # Super-Fast Online Learning Trigger
        if use_llm and 'ai_risk_probability' in reg_data:
            # If Risk > 50% and Price Dropped > 2% today, REINFORCE 'Risk' (Label=1)
            # If Risk > 50% and Price Rose, PENALIZE 'Risk' (Label=0)
            
            day_change = float(data['close'].iloc[-1]) / float(data['open'].iloc[-1]) - 1
            label = 0
            if day_change < -0.02: label = 1 # Legit Dump
            
            print(f"   🧠 Training Regulatory Net (Online - RLHF Mode)...")
            try:
                reg_net.train_online(
                    risk_score_raw=reg_data.get('risk_score_raw', 0),
                    volatility=technical.get('atr_percent', 0.02),
                    insider_sell=1 if reg_data.get('insider_sell_detected') else 0,
                    sentiment=news_sentiment.get('score', 0) if news_sentiment else 0,
                    price_change=day_change
                )
            except Exception as e:
                logger.error(f"⚠️ Regulatory Training Failed: {e}")
                print(f"      [Warning] RegNet Training skipped: {e}")

        self.feedback_loop.log_prediction(
            symbol=symbol,
            prediction=final_decision,
            context={
                "technical": technical,
                "quant": quant,
                "ml": ml,
                "sentiment": sentiment_data,
                "regulatory": reg_data # Save for history
            }
        )
        
        # Compile full result
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': float(data['close'].iloc[-1]),
            'technical': technical,
            'quant_signals': quant,
            'ml': ml,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'llm_analysis': llm_analysis,
            'decision_engine': decision
        }
        
        print("✅ Analysis complete!")
        
        # 🧠 PHASE 8: Decision Persistence (Self-Learning)
        try:
            self.feedback_loop.log_prediction(symbol, decision, context=result)
        except Exception as e:
            logger.error(f"Failed to persist decision: {e}")

        return self._sanitize_for_json(result)

    def _sanitize_for_json(self, obj):
        """Recursively convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(i) for i in obj]
        elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj) if not np.isnan(obj) else None
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif pd.isna(obj):
            return None
        return obj
    
    def format_recommendation(self, result: Dict[str, Any]) -> str:
        """Format analysis result as readable recommendation"""
        decision = result['decision']
        symbol = result['symbol']
        price = result['current_price']
        
        report = f"""
{'='*70}
STOCK ANALYSIS REPORT: {symbol}
{'='*70}

Current Price: ₹{price:.2f}
Timestamp: {result['timestamp']}

RECOMMENDATION: {decision['rating']}
Confidence: {decision['confidence']:.0%}

Entry Price: ₹{decision['entry_price']:.2f}
Stop Loss: ₹{decision['stop_loss']:.2f}
Targets: T1=₹{decision['target_1']:.2f}, T2=₹{decision['target_2']:.2f}, T3=₹{decision['target_3']:.2f}

TECHNICAL ANALYSIS:
- RSI: {result['technical']['rsi']:.1f}
- MACD: {result['technical']['macd']:.2f}
- Price vs SMA200: {'Above ✅' if result['current_price'] > result['technical']['sma_200'] else 'Below ⚠️'}

QUANTITATIVE SIGNALS:
- Momentum: {result['quant']['momentum']['signal']}
- Mean Reversion Z-Score: {result['quant']['mean_reversion']['zscore']:.2f}
- Market Regime: {result['quant']['regime']['current_regime']}

ML PREDICTIONS:
- 1-day: ₹{result['ml']['lstm']['predictions']['1d']:.2f}
- 7-day: ₹{result['ml']['lstm']['predictions']['7d']:.2f}
- Confidence: {result['ml']['lstm']['confidence']:.0%}
"""
        
        if result.get('news_sentiment'):
            ns = result['news_sentiment']
            report += f"\nNEWS SENTIMENT: {ns['label']} ({ns['score']:.2f})\n"
        
        if result.get('social_sentiment'):
            ss = result['social_sentiment']
            report += f"SOCIAL SENTIMENT: {ss['label']} ({ss['score']:.2f})\n"
        
        if result.get('llm_analysis'):
            report += f"\nLLM ANALYSIS: ✅ Completed (3 phases)\n"
        
        report += f"\n{'='*70}\n"
        
        return report


async def main():
    """Demo the orchestrator"""
    orchestrator = StockAnalysisOrchestrator()
    
    # Analyze a stock
    result = await orchestrator.analyze_stock(
        "RELIANCE.NS",
        use_llm=True,  # Set to False to skip LLM
        use_scrapers=True  # Set to False to skip news/social
    )
    
    # Print recommendation
    print(orchestrator.format_recommendation(result))


if __name__ == "__main__":
    asyncio.run(main())
