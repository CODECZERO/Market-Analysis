"""
LLM API Integration - Actual API Calls
Connects to Groq/NVIDIA/OpenRouter for 3-phase analysis
"""

import os
import time
import json
from typing import Dict, Any, Optional
import requests


class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    def __init__(self):
        # Load API keys from environment
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.nvidia_api_key = os.getenv('NVIDIA_API_KEY', '')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
        
        # Select provider based on available keys
        self.provider = self._select_provider()
        
        # Rate limiting
        self.last_call_time = 0
        self.min_delay = 2.0  # 2 seconds between calls
    
    def _select_provider(self) -> str:
        """Select API provider based on available keys"""
        if self.groq_api_key:
            return 'groq'
        elif self.nvidia_api_key:
            return 'nvidia'
        elif self.openrouter_api_key:
            return 'openrouter'
        else:
            return 'mock'  # Fallback to mock responses
    
    async def _rate_limit(self):
        """
        Enforce rate limiting (async, non-blocking).
        
        ⚡ PERFORMANCE: Uses asyncio.sleep instead of time.sleep
        to avoid blocking the event loop.
        """
        import asyncio
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)
        self.last_call_time = time.time()
    
    async def call_groq(self, messages: list, model: str = "mixtral-8x7b-32768") -> str:
        """Call Groq API (async)"""
        await self._rate_limit()
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._mock_response(messages)
    
    async def call_nvidia(self, messages: list, model: str = None) -> str:
        """Call NVIDIA NIM API (async)"""
        await self._rate_limit()
        
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.nvidia_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model if model else "meta/llama-3.1-8b-instruct",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"NVIDIA API error: {e}")
            return self._mock_response(messages)
    
    async def call_openrouter(self, messages: list, model: str = "google/gemini-pro") -> str:
        """Call OpenRouter API (async)"""
        await self._rate_limit()
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://market-analysis.local",
            "X-Title": "Market Analysis System"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            return self._mock_response(messages)
    
    def _mock_response(self, messages: list) -> str:
        """Generate mock response when API is unavailable"""
        prompt = messages[-1]['content'] if messages else ""
        
        if "what" in prompt.lower() or "why" in prompt.lower():
            return json.dumps({
                "analysis": "Based on technical and fundamental factors, the stock shows mixed signals.",
                "strengths": ["Strong revenue growth", "Good market position"],
                "weaknesses": ["High valuation", "Market volatility"],
                "recommendation": "HOLD with cautious outlook"
            })
        elif "when" in prompt.lower() or "where" in prompt.lower():
            return json.dumps({
                "entry_timing": "Wait for pullback to support levels",
                "entry_zone": "2420-2450 range",
                "horizon": "MEDIUM (3-6 months)",
                "confidence": "MODERATE"
            })
        else:
            return json.dumps({
                "execution_plan": "Enter in phases, maintain stop loss",
                "position_sizing": "Start with 50% position",
                "risk_management": "Use trailing stop after profit",
                "exit_strategy": "Book 50% at T1, trail rest"
            })
    
    def call(self, messages: list) -> str:
        """Call appropriate provider"""
        if self.provider == 'groq':
            return self.call_groq(messages)
        elif self.provider == 'nvidia':
            return self.call_nvidia(messages)
        elif self.provider == 'openrouter':
            return self.call_openrouter(messages)
        else:
            print("⚠️  No API keys found, using mock responses")
            print("   Add GROQ_API_KEY, NVIDIA_API_KEY, or OPENROUTER_API_KEY to .env")
            return self._mock_response(messages)


# Global client instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get singleton LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def call_llm_phase1(technical: Dict, quant: Dict, symbol: str) -> Dict[str, Any]:
    """Phase 1: What/Why analysis"""
    client = get_llm_client()
    
    messages = [
        {"role": "system", "content": "You are an expert stock market analyst. Provide concise, actionable insights."},
        {"role": "user", "content": f"""Analyze {symbol}:

Technical Indicators:
- RSI: {technical.get('rsi', 0):.1f}
- MACD: {technical.get('macd', 0):.2f}
- Price vs SMA200: {'Above' if technical.get('sma_200', 0) > 0 else 'Below'}

Quant Signals:
- Momentum: {quant.get('momentum', {}).get('signal', 'UNKNOWN')}
- Mean Reversion Z-Score: {quant.get('mean_reversion', {}).get('zscore', 0):.2f}
- Regime: {quant.get('regime', {}).get('current_regime', 'UNKNOWN')}

Question: WHAT is happening with this stock WHY?
Provide: strengths, weaknesses, key factors. JSON format."""}
    ]
    
    response = client.call(messages)
    
    try:
        return json.loads(response)
    except:
        return {"analysis": response, "strengths": [], "weaknesses": [], "recommendation": "HOLD"}


def call_llm_phase2(phase1_result: Dict, technical: Dict) -> Dict[str, Any]:
    """Phase 2: When/Where analysis"""
    time.sleep(2)  # Delay between phases
    
    client = get_llm_client()
    
    messages = [
        {"role": "system", "content": "You are an expert at market timing and entry strategies."},
        {"role": "user", "content": f"""Given this analysis:
{json.dumps(phase1_result, indent=2)}

Technical levels:
- Support: {technical.get('support_level', 0):.2f}
- Resistance: {technical.get('resistance_level', 0):.2f}
- Current: {technical.get('current_price', 0):.2f}

Question: WHEN to enter and WHERE (price level)?
Provide: entry_timing, entry_zone, horizon, confidence. JSON format."""}
    ]
    
    response = client.call(messages)
    
    try:
        return json.loads(response)
    except:
        return {"entry_timing": "Monitor", "entry_zone": "Current levels", "horizon": "MEDIUM", "confidence": "MODERATE"}


def call_llm_phase3(phase1: Dict, phase2: Dict, ml_predictions: Dict) -> Dict[str, Any]:
    """Phase 3: How to execute"""
    time.sleep(3)  # Delay between phases
    
    client = get_llm_client()
    
    messages = [
        {"role": "system", "content": "You are an expert at trade execution and risk management."},
        {"role": "user", "content": f"""Given:
Analysis: {json.dumps(phase1, indent=2)}
Timing: {json.dumps(phase2, indent=2)}

ML Predictions:
- 1-day: {ml_predictions.get('lstm', {}).get('predictions', {}).get('1d', 0):.2f}
- 7-day: {ml_predictions.get('lstm', {}).get('predictions', {}).get('7d', 0):.2f}
- Confidence: {ml_predictions.get('lstm', {}).get('confidence', 0):.0%}

Question: HOW to execute this trade?
Provide: execution_plan, position_sizing, risk_management, exit_strategy. JSON format."""}
    ]
    
    response = client.call(messages)
    
    try:
        return json.loads(response)
    except:
        return {"execution_plan": "Standard entry", "position_sizing": "Conservative", "risk_management": "Use stop loss", "exit_strategy": "Take profits at targets"}


if __name__ == "__main__":
    # Test
    print("Testing LLM Client...")
    client = get_llm_client()
    print(f"Using provider: {client.provider}")
    
    if client.provider == 'mock':
        print("\n⚠️  Add API keys to .env to test real API calls:")
        print("   GROQ_API_KEY=your_key_here")
        print("   NVIDIA_API_KEY=your_key_here")
        print("   OPENROUTER_API_KEY=your_key_here")
