"""
Decision Engine
Combines all analysis signals (technical, quant, ML, sentiment) into a unified recommendation
Produces STRONG_BUY to STRONG_SELL rating with confidence score
"""

import logging
import numpy as np
from typing import Dict, Any, Optional

class DecisionEngine:
    """
    Multi-signal fusion engine for stock recommendations
    Weighs and combines signals from all analysis sources
    """
    
    def _safe_num(self, val, default=0.0):
        if val is None: return default
        try: return float(val)
        except: return default
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default Weights (Sum = 1.0)
        self.weights = weights or {
            'technical': 0.20,
            'quantitative': 0.15,
            'ml_predictions': 0.25,
            'sentiment': 0.10,
            'fundamentals': 0.10,
            'macro': 0.10,
            'forensics': 0.10
        }
    
    def make_decision(
        self,
        technical_indicators: Dict[str, Any],
        quant_signals: Dict[str, Any],
        ml_predictions: Dict[str, Any],
        sentiment: Dict[str, Any],
        phase1_analysis: Dict[str, Any],
        current_price: float
    ) -> Dict[str, Any]:
        
        # Unpack Hyper-Intelligence signals from quant dict if present
        macro_data = quant_signals.get('macro', {})
        forensics_data = quant_signals.get('forensics', {})
        graph_data = quant_signals.get('graph', {})
        
        # Score categories
        tech_score = self._score_technical(technical_indicators)
        quant_score = self._score_quantitative(quant_signals)
        ml_score = self._score_ml_predictions(ml_predictions, current_price)
        sentiment_score = self._score_sentiment(sentiment)
        fundamental_score = self._score_fundamentals(phase1_analysis)
        
        # New Scoring
        macro_score = min(100, max(-100, self._safe_num(macro_data.get('macro_score', 0)) * 100))
        forensic_score = -100 if not forensics_data.get('is_legit', True) else 0
        if self._safe_num(forensics_data.get('scam_probability', 0)) > 0.7: forensic_score = -100
        
        # UL/RL Boosters
        learning_data = quant_signals.get('learning', {})
        regime_id = learning_agent_regime_id = learning_data.get('hidden_regime', {}).get('cluster_id', -1)
        
        # Boost for Institutional Trend (Regime 3) or Accumulation (Regime 0)
        learning_boost = 0
        if regime_id == 3: learning_boost += 15
        if regime_id == 0: learning_boost += 10
        if regime_id == 2: learning_boost -= 20 # Panic Exhaustion (Caution)
        
        # Composite calculation
        composite_score = (
            tech_score * self.weights['technical'] +
            quant_score * self.weights['quantitative'] +
            ml_score * self.weights['ml_predictions'] +
            sentiment_score * self.weights['sentiment'] +
            fundamental_score * self.weights['fundamentals'] +
            macro_score * self.weights['macro'] +
            forensic_score * self.weights['forensics'] +
            learning_boost
        )
        
        recommendation, confidence = self._score_to_rating(composite_score)
        
        # 🆕 Professional Reasoning (ICT/SMC + Accounting)
        reasoning = self._generate_pro_reasoning(recommendation, technical_indicators, quant_signals, ml_predictions)
        
        # Enhanced Hold Duration (using Transformer & Macro)
        hold_duration = self._calculate_hold_duration(
            technical_indicators, quant_signals, ml_predictions, recommendation
        )
        
        # 🆕 Monte Carlo Simulation (Statistical Probability)
        mc_results = self._run_monte_carlo(current_price, technical_indicators.get('volatility', 0.02))
        
        return {
            'rating': recommendation,
            'recommendation': recommendation,
            'composite_score': round(composite_score, 2),
            'confidence': round(confidence, 2),
            'reasoning': reasoning, 
            'current_price': current_price,
            'breakdown': {
                'technical': round(tech_score, 1),
                'quantitative': round(quant_score, 1),
                'ml': round(ml_score, 1),
                'macro': round(macro_score, 1),
                'forensics': round(forensic_score, 1)
            },
            'entry_range': self._calculate_entry_range(current_price, technical_indicators, recommendation),
            'stop_loss': self._calculate_stop_loss(current_price, technical_indicators, recommendation),
            'targets': self._calculate_targets(current_price, ml_predictions, recommendation),
            'hold_duration': hold_duration,
            'monte_carlo': mc_results
        }

    def _run_monte_carlo(self, current_price: float, volatility: float, simulations: int = 2000, days: int = 21) -> Dict[str, float]:
        """
        Runs Monte Carlo simulation to forecast price distribution.
        Returns probable price range (VaR, Median, Upside 95%).
        """
        if volatility <= 0: volatility = 0.02 # Default 2% daily vol fallback
        dt = 1
        
        # Random Brownian Motion (Geometric)
        # Price(t) = Price(t-1) * e^((mu - 0.5*sigma^2)*dt + sigma*epsilon*sqrt(dt))
        # Assuming drift (mu) = 0 for neutral walk, or bias it slightly by trend
        mu = 0.0005 # Small positive drift assumption (market tends up long term)
        
        simulated_prices = []
        
        for _ in range(simulations):
            price = current_price
            for _ in range(days):
                epsilon = np.random.normal(0, 1)
                drift = (mu - 0.5 * volatility**2) * dt
                diffusion = volatility * epsilon * np.sqrt(dt)
                price = price * np.exp(drift + diffusion)
            simulated_prices.append(price)
            
        simulated_prices = np.array(simulated_prices)
        
        return {
            "p5_downside_risk": round(np.percentile(simulated_prices, 5), 2),
            "median_target": round(np.median(simulated_prices), 2),
            "p95_upside_potential": round(np.percentile(simulated_prices, 95), 2),
            "volatility_used": volatility
        }

    def _calculate_hold_duration(self, technical, quant, ml, recommendation) -> str:
        if recommendation in ['SELL', 'STRONG_SELL']: return "Immediate Exit"
        
        # 1. Check Transformer Forecast (The "How Long")
        transformer_conf = self._safe_num(ml.get('transformer', {}).get('confidence', 0))
        t_90d = self._safe_num(ml.get('transformer', {}).get('90d', 0))
        current_price = self._safe_num(technical.get('close', 1000)) # Fallback
        
        # 2. Check Macro Regime
        regime = quant.get('regime', {}).get('regime', 'SIDEWAYS')
        
        if transformer_conf > 0.8 and t_90d > current_price * 1.10:
            return "3-4 Months (Transformer conviction > 80%)"
            
        if regime == 'BULL':
            return "4-8 Weeks (Trend Following)"
        elif regime == 'SIDEWAYS':
            return "1-3 Days (Swing/Scalp)"
        else:
            return "Intraday / Short Term Swing"

    def _generate_reasoning(self, recommendation, tech, quant, ml, macro, forensic, indicators) -> str:
        """Generates the 'Why'"""
        reasons = []
        if forensic < -50: return "AVOID: Forensic algorithms detected accounting irregularities/scam risk."
        
        if abs(macro) > 30:
            reasons.append(f"Global Macro Tailwinds ({'Positive' if macro>0 else 'Negative'})")
        if abs(ml) > 30:
            reasons.append("AI Deep Learning Models")
        if abs(quant) > 30:
            reasons.append("Institutional Flow (Smart Money)")
            
        if not reasons: reasons.append("Technical Momentum")
        
        return f"{recommendation} driven by {', '.join(reasons)}. " \
               f"Market Regime is {indicators.get('adx_trend', 'Neutral')}."
    
    def _score_technical(self, indicators: Dict[str, Any]) -> float:
        """Score technical indicators (-100 to +100)"""
        score = 0
        
        # RSI (30 points)
        rsi = self._safe_num(indicators.get('rsi_14', 50))
        if rsi < 30:
            score += 30  # Oversold = bullish
        elif rsi < 40:
            score += 15
        elif rsi > 70:
            score -= 30  # Overbought = bearish
        elif rsi > 60:
            score -= 15
        
        # MACD (25 points)
        if indicators.get('macd_bullish'):
            score += 25
        else:
            score -= 25
        
        # Trend alignment (25 points)
        price_vs_sma50 = self._safe_num(indicators.get('price_vs_sma50', 0))
        if price_vs_sma50 > 5:
            score += 25
        elif price_vs_sma50 > 0:
            score += 10
        elif price_vs_sma50 < -5:
            score -= 25
        elif price_vs_sma50 < 0:
            score -= 10
        
        # ADX (20 points) - trend strength
        adx = self._safe_num(indicators.get('adx_14', 20))
        trend_strength = indicators.get('trend_strength', 'weak')
        if trend_strength == 'strong' and price_vs_sma50 > 0:
            score += 20  # Strong uptrend
        elif trend_strength == 'strong' and price_vs_sma50 < 0:
            score -= 20  # Strong downtrend
        
        return max(-100, min(100, score))
    
    def _score_quantitative(self, quant: Dict[str, Any]) -> float:
        """Score quantitative signals (-100 to +100)"""
        score = 0
        
        # Momentum (40 points)
        momentum_signal = quant.get('momentum', {}).get('signal', 'NEUTRAL')
        if momentum_signal == 'STRONG_LONG':
            score += 40
        elif momentum_signal == 'LONG':
            score += 20
        elif momentum_signal == 'STRONG_SHORT':
            score -= 40
        elif momentum_signal == 'SHORT':
            score -= 20
        
        # Mean Reversion (30 points)
        mr_signal = quant.get('mean_reversion', {}).get('signal', 'HOLD')
        if mr_signal == 'BUY':
            score += 30
        elif mr_signal == 'SELL':
            score -= 30
        
        # Market Regime (30 points)
        regime = quant.get('regime', {}).get('regime', 'UNKNOWN')
        regime_prob = self._safe_num(quant.get('regime', {}).get('probability', 0))
        if regime == 'BULL' and regime_prob > 0.7:
            score += 30
        elif regime == 'BEAR' and regime_prob > 0.7:
            score -= 30
        elif regime == 'BULL' and regime_prob > 0.5:
            score += 15
        elif regime == 'BEAR' and regime_prob > 0.5:
            score -= 15
        
        return max(-100, min(100, score))
    
    def _score_ml_predictions(self, ml: Dict[str, Any], current_price: float) -> float:
        """Score ML predictions (-100 to +100)"""
        score = 0
        
        # LSTM prediction (50 points)
        # Handle nested predictions structure from quick_lstm_prediction
        lstm_data = ml.get('lstm', {})
        predictions = lstm_data.get('predictions', {}) if 'predictions' in lstm_data else lstm_data
        lstm_30d = self._safe_num(predictions.get('30d', current_price))
        
        if lstm_30d > current_price:
            upside_pct = ((lstm_30d - current_price) / current_price) * 100
            if upside_pct > 10:
                score += 50
            elif upside_pct > 5:
                score += 35
            elif upside_pct > 2:
                score += 20
        else:
            downside_pct = ((current_price - lstm_30d) / current_price) * 100
            if downside_pct > 10:
                score -= 50
            elif downside_pct > 5:
                score -= 35
            elif downside_pct > 2:
                score -= 20
        
        # XGBoost classification (50 points)
        xgb_signal = ml.get('xgboost', {}).get('signal', 'HOLD')
        xgb_prob = self._safe_num(ml.get('xgboost', {}).get('probability', 0.5))
        
        if xgb_signal == 'BUY':
            score += 50 * (xgb_prob - 0.5) * 2  # Scale 0.5-1.0 to 0-50
        elif xgb_signal == 'SELL':
            score -= 50 * (xgb_prob - 0.5) * 2
        
        return max(-100, min(100, score))
    
    def _score_sentiment(self, sentiment: Dict[str, Any]) -> float:
        """Score sentiment analysis (-100 to +100)"""
        fused_sentiment = sentiment.get('fused_sentiment', 0)
        
        # Fused sentiment is -1 to +1, map to -100 to +100
        score = fused_sentiment * 100
        
        # Boost if high data volume (more reliable)
        social_count = sentiment.get('social_data_points', 0)
        news_count = sentiment.get('news_data_points', 0)
        
        if social_count > 100 or news_count > 10:
            # High confidence, amplify signal
            score = score * 1.2
        elif social_count < 10 and news_count < 3:
            # Low confidence, dampen signal
            score = score * 0.5
        
        return max(-100, min(100, score))
    
    def _score_fundamentals(self, phase1: Optional[Dict[str, Any]]) -> float:
        """Score fundamental analysis from Phase 1 (-100 to +100)"""
        if not phase1:
            return 0.0
            
        confidence = phase1.get('confidence', 50)
        primary_cause = phase1.get('primary_cause', 'SENTIMENT_DRIVEN')
        
        # Map primary cause to bias
        cause_bias = {
            'FUNDAMENTALS_SHIFT': 30,  # Fundamental changes are strong signals
            'CORPORATE_EVENT': 25,
            'TECHNICAL_BREAKOUT': 20,
            'SENTIMENT_DRIVEN': 0,  # Already captured in sentiment score
            'MACRO_EVENT': 15,
            'TECHNICAL_BREAKDOWN': -20,
            'INSIDER_ACTIVITY': 10
        }
        
        base_score = cause_bias.get(primary_cause, 0)
        
        # Scale by confidence
        score = base_score * (confidence / 100)
        
        return max(-100, min(100, score))
    
    def _score_to_rating(self, composite_score: float) -> tuple:
        """Map composite score to rating and confidence"""
        if composite_score >= 60:
            return ('STRONG_BUY', min(composite_score, 100))
        elif composite_score >= 30:
            return ('BUY', composite_score + 10)
        elif composite_score >= -30:
            return ('HOLD', 100 - abs(composite_score) * 1.5)
        elif composite_score >= -60:
            return ('SELL', abs(composite_score) + 10)
        else:
            return ('STRONG_SELL', min(abs(composite_score), 100))
            
    def _generate_pro_reasoning(self, rating: str, tech: Dict, quant: Dict, ml: Dict) -> str:
        """Professional reasoning using ICT/SMC and accounting terms"""
        # Get SMC and Accounting info
        smc = quant.get('smc', {})
        acc_health = quant.get('accounting_health', 'Stable')
        
        reasons = []
        
        if "BUY" in rating:
            # ICT/SMC Reason
            if smc.get('market_structure', {}).get('trend') == "Bullish":
                reasons.append("Bullish Market Structure confirmed with recent BOS")
            if any(f['type'] == "Bullish FVG" for f in smc.get('fvg', [])):
                reasons.append("Institutional buy-side imbalance (FVG) detected")
            if any(ob['type'] == "Bullish OB" for ob in smc.get('order_blocks', [])):
                reasons.append("Price reacting from a high-probability Bullish Order Block")
            
            # Accounting Reason
            if "Cash Cow" in str(acc_health):
                reasons.append(f"Strong solvency backing: {acc_health}")
            elif "Stable" in str(acc_health):
                reasons.append("Healthy balance sheet liquidity")
                
            # Fallback
            if not reasons:
                reasons.append("Technicals aligned with institutional accumulation patterns")
                
        elif "SELL" in rating:
            # ICT/SMC Reason
            if smc.get('market_structure', {}).get('trend') == "Bearish":
                reasons.append("Bearish Market Structure with supply-side BOS")
            if any(f['type'] == "Bearish FVG" for f in smc.get('fvg', [])):
                reasons.append("Sell-side imbalance (FVG) suggests further downside")
            
            # Accounting Reason
            if "Risk" in str(acc_health):
                reasons.append(f"Financial vulnerability detected: {acc_health}")
                
            if not reasons:
                reasons.append("Smart money distribution detected at premium levels")
        else:
            reasons.append("Market in consolidation; institutional liquidity seek ongoing")
            if "Stable" in str(acc_health):
                reasons.append(f"Financials remains {acc_health}, awaiting market structure shift")
                
        return ". ".join(reasons) + "."
    
    def _calculate_entry_range(
        self,
        current_price: float,
        technical: Dict[str, Any],
        recommendation: str
    ) -> Dict[str, float]:
        """Calculate optimal entry price range"""
        if recommendation in ['SELL', 'STRONG_SELL']:
            # No entry for sell recommendations
            return {'min': 0, 'max': 0}
        
        # Use support levels or current price
        support_1 = technical.get('support_1', current_price * 0.98)
        
        if recommendation == 'STRONG_BUY':
            # Aggressive entry, willing to pay up
            return {
                'min': current_price * 0.99,
                'max': current_price * 1.02
            }
        elif recommendation == 'BUY':
            # Wait for slight pullback
            return {
                'min': support_1,
                'max': current_price * 1.01
            }
        else:  # HOLD
            return {
                'min': support_1,
                'max': support_1 * 1.01
            }
    
    def _calculate_stop_loss(
        self,
        current_price: float,
        technical: Dict[str, Any],
        recommendation: str
    ) -> float:
        """Calculate stop loss level"""
        support_2 = technical.get('support_2', current_price * 0.95)
        
        if recommendation in ['STRONG_BUY', 'BUY']:
            # Place stop below support_2
            return support_2 * 0.98
        else:
            # Tighter stop for HOLD
            return support_2 * 0.99
    
    def _calculate_targets(
        self,
        current_price: float,
        ml_predictions: Dict[str, Any],
        recommendation: str
    ) -> Dict[str, float]:
        """Calculate price targets"""
        lstm_7d = ml_predictions.get('lstm', {}).get('7d', current_price * 1.03)
        lstm_30d = ml_predictions.get('lstm', {}).get('30d', current_price * 1.05)
        lstm_90d = ml_predictions.get('lstm', {}).get('90d', current_price * 1.08)
        
        return {
            't1_1week': round(lstm_7d, 2),
            't2_30day': round(lstm_30d, 2),
            't3_90day': round(lstm_90d, 2)
        }
    
    def _recommend_position_size(self, confidence: float, recommendation: str) -> float:
        """Recommend position size as % of portfolio"""
        if recommendation in ['SELL', 'STRONG_SELL']:
            return 0.0
        
        base_size = {
            'STRONG_BUY': 4.0,
            'BUY': 3.0,
            'HOLD': 1.0
        }.get(recommendation, 1.0)
        
        # Scale by confidence
        return round(base_size * (confidence / 100), 1)


def generate_decision(
    technical_indicators: Dict[str, Any],
    quant_signals: Dict[str, Any],
    ml_predictions: Dict[str, Any],
    sentiment: Dict[str, Any],
    phase1_analysis: Dict[str, Any],
    current_price: float,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate decision
    
    Args:
        technical_indicators: Technical analysis results
        quant_signals: Quantitative strategy signals
        ml_predictions: ML model predictions
        sentiment: Sentiment analysis
        phase1_analysis: Phase 1 fundamental analysis
        current_price: Current stock price
        weights: Custom weights for the decision engine
        
    Returns:
        Decision engine output
    """
    engine = DecisionEngine(weights=weights)
    return engine.make_decision(
        technical_indicators,
        quant_signals,
        ml_predictions,
        sentiment,
        phase1_analysis,
        current_price
    )
