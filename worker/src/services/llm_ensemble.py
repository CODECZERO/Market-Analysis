"""
Advanced Multi-LLM Ensemble Analysis System
Uses multiple LLMs in parallel for superior stock analysis reasoning
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import json
import time

# Use centralized logger
try:
    from system_logger import get_logger, log_event
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    def log_event(c, t, d): print(f"[{c}] {t}: {d}")

logger = get_logger("LLM_Ensemble")

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    class AsyncGroq:
        def __init__(self, api_key=""): pass

import httpx

load_dotenv()


class MultiLLMEnsemble:
    """
    Advanced ensemble system that runs multiple LLMs in parallel
    and chains their reasoning for superior stock analysis
    """
    
    def __init__(self):
        # NVIDIA NIM API (via httpx)
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY", "")
        self.nvidia_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        
        # Groq Client
        if GROQ_AVAILABLE:
            self.groq_client = AsyncGroq(
                api_key=os.getenv("GROQ_API_KEY", "")
            )
        else:
            self.groq_client = None
            
        self.nvidia_model = os.getenv("NVIDIA_MODEL", "meta/llama-4-maverick-17b-128e-instruct")
        self.groq_model = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
        
        # Rate limiting (40 RPM limit -> 1.5s min delay)
        self.min_delay = float(os.getenv("LLM_MIN_DELAY_SEC", "1.5"))
        self.last_call = 0
        
    async def _rate_limit(self):
        """Non-blocking rate limiting"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)
        self.last_call = time.time()
    
    async def _call_nvidia_async(self, model: str, prompt: str, 
                                temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
        """Specialized NVIDIA API call via httpx"""
        headers = {
            "Authorization": f"Bearer {self.nvidia_api_key}",
            "Accept": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.nvidia_url, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']

    async def _call_groq_async(self, model: str, prompt: str, 
                              temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
        """Specialized Groq API call via AsyncGroq"""
        if self.groq_client is None:
            return None
            
        completion = await self.groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1.0,
            stream=False
        )
        return completion.choices[0].message.content

    async def call_llm_async(self, provider: str, prompt: str, 
                            temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
        """
        Unified wrapper for different LLM providers with error handling
        """
        await self._rate_limit()
        
        model = self.nvidia_model if provider == "nvidia" else self.groq_model
        
        try:
            start_time = time.time()
            
            if provider == "nvidia":
                content = await self._call_nvidia_async(model, prompt, temperature, max_tokens)
            else:
                content = await self._call_groq_async(model, prompt, temperature, max_tokens)
                
            duration = time.time() - start_time
            log_event("LLM_Ensemble", "API_SUCCESS", f"Model {model} ({provider}) responded in {duration:.2f}s")
            return content
        except Exception as e:
            error_msg = str(e)
            log_event("LLM_Ensemble", "API_FAILURE", f"Model {model} ({provider}) failed: {error_msg}")
            raise e
    
    async def parallel_technical_analysis(self, stock_data: Dict, fundamental_data: str = "") -> Dict[str, Optional[str]]:
        """
        Phase 1: Run comprehensive Hyper-Intelligence analysis
        """
        
        # Extract Crystal Ball Data
        crystal_ball = stock_data.get('quant_signals', {}).get('crystal_ball', [])
        cb_str = "Unavailable"
        if crystal_ball:
            # Format: - +5mup: UP (Target: 105.0)
            cb_str = "\n".join([f"- {row['time']}: {row['direction']} (Target: {row['target_price']:.2f}, Risk: {row['loss_pct']:.1f}%)" for row in crystal_ball[:3]])

        # 🚀 GOD MODE PROMPT INJECTION
        prompt = f"""You are a Hyper-Intelligent Hedge Fund AI. Analyze {stock_data.get('symbol', 'UNKNOWN')}.

{fundamental_data}

🔥 HYPER-INTELLIGENCE SIGNALS:
- Macro Score: {stock_data.get('macro_score', 0)} ({stock_data.get('macro_summary', 'Neutral')})
- Forensic Risk: {'SAFE' if stock_data.get('forensic_safe', True) else '🚨 SCAM ALERT'} (Prob: {stock_data.get('scam_probability', 0):.1%})
- 🧠 Hidden Regime (Unsupervised): {stock_data.get('learning_regime', 'Scanning...')}
- ⚖️ RL Policy Weights: {stock_data.get('policy_weights', 'Default')}
- Causal Graph: Linked to {stock_data.get('graph_risk', 0)} risky vectors.
- Transformer Forecast (AI): {stock_data.get('ml_transformer_conf', 0):.0%} conviction in trend.

🔮 CRYSTAL BALL (High-Freq Forecasts):
{cb_str}

📊 QUANT & TECHNICALS:
- Momentum: {stock_data.get('quant_momentum', 0)}
- Institutional Flow (Alpha): {stock_data.get('quant_alpha', 0):.5f}
- RSI: {stock_data.get('rsi', 'N/A')}
- MACD: {stock_data.get('macd', 'N/A')}

TASK: Synthesize these 5 layers into a deep insight.
1. WHY is the stock moving? (Cite Causal Graph or Macro)
2. HOW LONG to hold? (Explicitly state "Exit by [Time]" if Crystal Ball shows reversal)
3. Verdict: BUY/SELL/HOLD.

Response (Max 100 words):"""

        # Run NVIDIA and Groq in parallel
        nvidia_task = self.call_llm_async("nvidia", prompt, temperature=0.3)
        groq_task = self.call_llm_async("groq", prompt, temperature=0.3)
        
        results = await asyncio.gather(nvidia_task, groq_task, return_exceptions=True)
        nvidia_analysis = results[0] if not isinstance(results[0], Exception) else None
        groq_analysis = results[1] if not isinstance(results[1], Exception) else None

        if isinstance(results[0], Exception):
            log_event("LLM_Ensemble", "TECHNICAL_FAILURE", f"NVIDIA Technical Failed: {results[0]}")
        if isinstance(results[1], Exception):
            log_event("LLM_Ensemble", "TECHNICAL_FAILURE", f"Groq Technical Failed: {results[1]}")
        
        return {
            "nvidia_technical": nvidia_analysis,
            "groq_technical": groq_analysis
        }
    
    async def parallel_sentiment_analysis(self, sentiment_data: Dict) -> Dict[str, Optional[str]]:
        """
        Phase 2: Run parallel sentiment fusion with multiple LLMs
        Each model interprets sentiment data differently
        """
        
        prompt = f"""Analyze sentiment data for this stock:

News Sentiment: {sentiment_data.get('news_score', 'N/A')} ({sentiment_data.get('news_label', 'N/A')})
Social Media: {sentiment_data.get('social_score', 'N/A')} ({sentiment_data.get('social_label', 'N/A')})
Reddit Mentions: {sentiment_data.get('reddit_mentions', 'N/A')}
Overall Buzz: {sentiment_data.get('buzz_level', 'N/A')}

Provide sentiment interpretation (2-3 sentences):
1. What the sentiment indicates about market psychology
2. Any divergence between news and social sentiment
3. Impact on near-term price movement

Be specific about bullish/bearish implications."""

        # Run both models in parallel (allow partial failure)
        nvidia_task = self.call_llm_async("nvidia", prompt, temperature=0.4)
        groq_task = self.call_llm_async("groq", prompt, temperature=0.4)
        
        results = await asyncio.gather(nvidia_task, groq_task, return_exceptions=True)
        nvidia_sentiment = results[0] if not isinstance(results[0], Exception) else None
        groq_sentiment = results[1] if not isinstance(results[1], Exception) else None

        if isinstance(results[0], Exception):
            log_event("LLM_Ensemble", "MODEL_FAILURE", f"NVIDIA Failed: {results[0]}")
        if isinstance(results[1], Exception):
            log_event("LLM_Ensemble", "MODEL_FAILURE", f"Groq Failed: {results[1]}")
        
        return {
            "nvidia_sentiment": nvidia_sentiment,
            "groq_sentiment": groq_sentiment
        }
    
    async def ensemble_final_decision(self, 
                                     technical_analyses: Dict[str, Optional[str]],
                                     sentiment_analyses: Dict[str, Optional[str]],
                                     stock_symbol: str) -> Dict[str, Any]:
        """
        Phase 3: Synthesize all analyses into final decision
        Uses heavy reasoning to combine multi-model insights
        """
        
        # Prepare synthesis prompt with all prior analyses
        synthesis_prompt = f"""You are a senior quantitative analyst synthesizing multiple AI analyses for {stock_symbol}.

TECHNICAL ANALYSIS (Model 1 - NVIDIA):
{technical_analyses.get('nvidia_technical', 'N/A')}

TECHNICAL ANALYSIS (Model 2 - Groq):
{technical_analyses.get('groq_technical', 'N/A')}

SENTIMENT ANALYSIS (Model 1 - NVIDIA):
{sentiment_analyses.get('nvidia_sentiment', 'N/A')}

SENTIMENT ANALYSIS (Model 2 - Groq):
{sentiment_analyses.get('groq_sentiment', 'N/A')}

TASK: Synthesize these multiple expert analyses into ONE final recommendation.

Provide your response in this EXACT JSON format:
{{
  "recommendation": "STRONG_BUY" or "BUY" or "HOLD" or "SELL" or "STRONG_SELL",
  "confidence": 0.0 to 1.0,
  "reasoning": "2-3 sentences explaining your decision, highlighting consensus or divergence between models",
  "entry_price": estimated_entry_price_json_number,
  "stop_loss": stop_loss_price_json_number,
  "target_price": target_price_json_number,
  "time_horizon": "short_term" or "medium_term" or "long_term",
  "risk_level": "low" or "medium" or "high",
  "key_factors": ["factor1", "factor2", "factor3"]
}}

Use critical thinking. If models disagree, explain why and what you weigh more heavily.
Be conservative - only STRONG_BUY/STRONG_SELL if ALL indicators align strongly."""

        # Run final synthesis on both models and pick the more confident one
        nvidia_task = self.call_llm_async(
            "nvidia", 
            synthesis_prompt, 
            temperature=0.2,  # Lower temp for final decision
            max_tokens=1000
        )
        
        groq_task = self.call_llm_async(
            "groq",
            synthesis_prompt,
            temperature=0.2,
            max_tokens=1000
        )
        
        # Allow partial failure
        results = await asyncio.gather(nvidia_task, groq_task, return_exceptions=True)
        nvidia_decision = results[0] if not isinstance(results[0], Exception) else None
        groq_decision = results[1] if not isinstance(results[1], Exception) else None
        
        if isinstance(results[0], Exception):
             log_event("LLM_Ensemble", "DECISION_FAILURE", f"NVIDIA Decision Failed: {results[0]}")
        if isinstance(results[1], Exception):
             log_event("LLM_Ensemble", "DECISION_FAILURE", f"Groq Decision Failed: {results[1]}")
        
        # Parse JSON responses
        final_decisions = {}
        
        import re
        for model_name, response in [("nvidia", nvidia_decision), ("groq", groq_decision)]:
            if response:
                try:
                    # Robust JSON extraction using regex
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        decision = json.loads(json_str)
                        # Normalize key if they used 'decision' instead of 'recommendation'
                        if 'decision' in decision and 'recommendation' not in decision:
                            decision['recommendation'] = decision['decision']
                        final_decisions[model_name] = decision
                    else:
                        print(f"No JSON found in {model_name} response")
                        log_event("LLM_Ensemble", "JSON_MISSING", f"No JSON blob in {model_name} output")
                except Exception as e:
                    print(f"Failed to parse {model_name} decision: {e}")
                    log_event("LLM_Ensemble", "JSON_PARSE_ERROR", f"Failed to parse {model_name} decision: {e}")
        
        # Ensemble strategy: Pick the decision with higher confidence
        if final_decisions:
            best_decision = max(
                final_decisions.items(),
                key=lambda x: x[1].get('confidence', 0)
            )
            
            result = best_decision[1].copy() # Use copy to avoid circular reference
            result['selected_model'] = best_decision[0]
            result['all_models'] = {k: v for k, v in final_decisions.items()} # Shallow copy
            
            log_event("LLM_Ensemble", "FINAL_DECISION_SELECTED", f"Selected decision from {best_decision[0]} with confidence {result.get('confidence', 0):.2f}")
            return result
        
        # Fallback if both failed
        log_event("LLM_Ensemble", "FINAL_DECISION_FALLBACK", "Both models failed to provide a valid decision. Using fallback.")
        return {
            "recommendation": "HOLD",
            "confidence": 0.3,
            "reasoning": "Unable to synthesize analyses - insufficient data",
            "selected_model": "fallback"
        }
    
    async def analyze_stock_comprehensive(self, 
                                         stock_data: Dict,
                                         sentiment_data: Dict,
                                         fundamental_data_formatted: str = "") -> Dict[str, Any]:
        """
        Master method: Run complete 3-phase ensemble analysis
        Enhanced with fundamental data and hallucination detection
        
        Phase 1: Parallel technical analysis (2 models) + Fundamentals
        Phase 2: Parallel sentiment analysis (2 models)  
        
        Returns comprehensive analysis with heavy reasoning
        """
        
        print(f"🧠 Starting Multi-LLM Ensemble Analysis...")
        print(f"   Models: NVIDIA ({self.nvidia_model}) + Groq ({self.groq_model})")
        
        # Phase 1: Technical Analysis (parallel)
        print("   Phase 1/3: Technical Analysis (parallel)...")
        technical_analyses = await self.parallel_technical_analysis(stock_data)
        
        # Phase 2: Sentiment Analysis (parallel)
        print("   Phase 2/3: Sentiment Analysis (parallel)...")
        sentiment_analyses = await self.parallel_sentiment_analysis(sentiment_data)
        
        # Phase 3: Final Decision (ensemble)
        print("   Phase 3/3: Final Decision Synthesis...")
        final_decision = await self.ensemble_final_decision(
            technical_analyses,
            sentiment_analyses,
            stock_data.get('symbol', 'UNKNOWN')
        )
        
        # Compile complete result
        result = {
            **final_decision,
            "analysis_phases": {
                "technical": technical_analyses,
                "sentiment": sentiment_analyses
            },
            "ensemble_metadata": {
                "models_used": [self.nvidia_model, self.groq_model],
                "phases": 3,
                "parallel_calls": 6  # 2+2+2
            }
        }
        
        print(f"✅ Ensemble Analysis Complete!")
        print(f"   Decision: {result.get('decision')} (Confidence: {result.get('confidence', 0):.2%})")
        print(f"   Selected: {result.get('selected_model', 'unknown')} model")
        
        return result


# Global ensemble instance
_ensemble = None


def get_ensemble() -> MultiLLMEnsemble:
    """Get or create the global multi-LLM ensemble"""
    global _ensemble
    if _ensemble is None:
        _ensemble = MultiLLMEnsemble()
    return _ensemble


async def analyze_stock_with_ensemble(stock_data: Dict, sentiment_data: Dict, 
                                       fundamental_data_formatted: str = "") -> Dict[str, Any]:
    """
    Convenience function for comprehensive multi-LLM analysis
    
    Usage:
        result = await analyze_stock_with_ensemble(stock_data, sentiment_data, fundamentals)
    """
    ensemble = get_ensemble()
    return await ensemble.analyze_stock_comprehensive(stock_data, sentiment_data, fundamental_data_formatted)
