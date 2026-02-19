"""LLM adapter abstractions for summaries and sentiment."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol
from contextlib import contextmanager


from .logger import get_logger
from .config import get_settings
from . import fallback_analysis
from .llm_executor import (
    invoke_strategic,
    invoke_sentiment,
    invoke_general,
    invoke_launch_detection,
    invoke_response_suggestion,
    invoke_competitor_analysis,
    invoke_web_insights,
    invoke_prompt_text,
)
from .llm.prompts import (
    SUMMARY_PROMPT,
    SENTIMENT_PROMPT,
    ENHANCED_ANALYSIS_PROMPT,
    RESPONSE_SUGGESTION_PROMPT,
    COMMERCIAL_INTENT_PROMPT,
    COMPETITOR_COMPLAINT_PROMPT,
    WEB_INSIGHTS_PROMPT,
)
from .metrics import (
    worker_llm_latency_seconds,
)

logger = get_logger(__name__)


# ... (Prompts hidden for brevity, unchanged) ...

class LangChainLLMAdapter:
    # ... (init and other methods unchanged) ...

    async def strategic_analyze(self, prompt: str) -> dict[str, Any]:
        """Perform strategic analysis/disambiguation via LLM."""
        response = await invoke_strategic(
            brand_name=self._brand,
            context="Strategic analysis request",
            text=prompt,
            timeout=self._timeout,
            brand=self._brand,
            chunk_id=self._chunk_id,
            operation="strategic_analysis",
            format_json=True
        )
        
        if isinstance(response, str):
            try:
                clean_response = response.strip()
                if clean_response.startswith("```"):
                    parts = clean_response.split("```")
                    if len(parts) >= 2:
                        possible_json = parts[1]
                        if possible_json.strip().lower().startswith("json"):
                             possible_json = possible_json.strip()[4:]
                        clean_response = possible_json.strip()
                return json.loads(clean_response)
            except json.JSONDecodeError:
                return {"relevant": False, "summary": f"Failed to parse strategic analysis: {response[:50]}..."}
        elif isinstance(response, dict):
            return response
        else:
            return {"relevant": False, "summary": "Invalid response type"}

    # ... (other methods) ...

@dataclass
class InstrumentedLLMAdapter:
    """Wrapper for metrics and logging."""
    _adapter: LangChainLLMAdapter
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self._adapter, name)

    async def summarize(self, texts: list[str]) -> str:
        start = time.time()
        try:
            return await self._adapter.summarize(texts)
        finally:
            worker_llm_latency_seconds.labels(worker_id=self._adapter._worker_id, brand=self._adapter._brand, operation="summary").observe(time.time() - start)

    async def sentiment(self, texts: list[str]) -> dict[str, float]:
        start = time.time()
        try:
            return await self._adapter.sentiment(texts)
        finally:
            worker_llm_latency_seconds.labels(worker_id=self._adapter._worker_id, brand=self._adapter._brand, operation="sentiment").observe(time.time() - start)

    async def strategic_analyze(self, prompt: str) -> dict[str, Any]:
        start = time.time()
        try:
            return await self._adapter.strategic_analyze(prompt)
        finally:
             worker_llm_latency_seconds.labels(worker_id=self._adapter._worker_id, brand=self._adapter._brand, operation="strategic_analysis").observe(time.time() - start)






class SupportsInvoke(Protocol):
    async def ainvoke(self, input: Any) -> Any:  # pragma: no cover - protocol definition
        ...


class LangChainLLMAdapter:
    """Adapter that leverages LangChain chat models for summaries and sentiment."""

    def __init__(self, primary: Any, fallback: Any | None, *, max_tokens: int, timeout: int, worker_id: str) -> None:
        self._primary = primary
        self._fallback = fallback
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._worker_id = worker_id
        self._brand = "unknown"
        self._chunk_id = "unknown"

    @contextmanager
    def context(self, *, brand: str, chunk_id: str) -> Any:
        previous_brand = self._brand
        previous_chunk = self._chunk_id
        self._brand = brand
        self._chunk_id = chunk_id
        try:
            yield self
        finally:
            self._brand = previous_brand
            self._chunk_id = previous_chunk

    async def _safe_invoke(self, prompt: str, operation: str) -> Any:
        """Invoke with rate limiting and circuit breaking."""
        # Using the invoke_general structure from llm_executor handles rate limiting there
        # but for direct prompt formatting tasks we might use this wrapper logic
        # For simplicity and to fix the circular dependency/logic, we'll route valid operations
        # directly to llm_executor functions where possible, or use the primary client (OllamaProxy)
        
        # If primary is OllamaProxy, we can use its ainvoke directly if not using detailed executor
        # but since we want global rate limits, we should prefer invoke_general/invoke_prompt_text
        
        # Delegate to invoke_prompt_text for generic safe invocation if not a specialized op
        return await invoke_prompt_text(
            prompt, 
            timeout=self._timeout, 
            brand=self._brand, 
            chunk_id=self._chunk_id, 
            operation=operation,
            format_json=True
        )

    async def summarize(self, texts: list[str]) -> str:
        try:
            prompt = SUMMARY_PROMPT.format(joined_texts="\n".join(texts), max_tokens=self._max_tokens)
            return await invoke_general(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="summary",
                format_json=False
            )
        except Exception as e:
            # FALLBACK: Return first 2 sentences of combined text
            logger.warning(f"LLM summarize failed, using fallback: {e}")
            combined = " ".join(texts)[:500]
            # Extract first 2 sentences
            sentences = combined.split(".")
            if len(sentences) >= 2:
                return f"{sentences[0].strip()}. {sentences[1].strip()}."
            return combined[:200] + "..."

    async def sentiment(self, texts: list[str]) -> dict[str, float]:
        try:
            prompt = SENTIMENT_PROMPT.format(joined_texts="\n".join(texts))
            response = await invoke_sentiment(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="sentiment",
                format_json=True
            )
            
            if isinstance(response, str):
                try:
                    parsed = json.loads(response)
                except json.JSONDecodeError:
                    parsed = {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
            elif isinstance(response, dict):
                parsed = response
            else:
                parsed = {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
                
            return {
                "positive": float(parsed.get("positive", 0.0)),
                "negative": float(parsed.get("negative", 0.0)),
                "neutral": float(parsed.get("neutral", 1.0)),
            }
        except Exception as e:
            # FALLBACK: Use regex-based sentiment analysis
            logger.warning(f"LLM sentiment failed, using fallback: {e}")
            combined_text = " ".join(texts)
            fb = fallback_analysis.analyze_sentiment_regex(combined_text)
            score = fb["sentiment_score"]
            # Convert score to positive/negative/neutral distribution
            if score > 0.2:
                return {"positive": 0.6 + score * 0.3, "negative": 0.1, "neutral": 0.3 - score * 0.2}
            elif score < -0.2:
                return {"positive": 0.1, "negative": 0.6 + abs(score) * 0.3, "neutral": 0.3 - abs(score) * 0.2}
            else:
                return {"positive": 0.25, "negative": 0.25, "neutral": 0.5}

    async def analyze_enhanced(self, texts: list[str]) -> dict[str, Any]:
        """Perform enhanced analysis with emotions, urgency, sarcasm, topics."""
        try:
            prompt = ENHANCED_ANALYSIS_PROMPT.format(joined_texts="\n".join(texts))
            # enhanced_analysis maps to general brand analysis with JSON format
            response = await invoke_general(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="enhanced_analysis",
                format_json=True
            )
            
            # Default fallback values for parsing errors ONLY
            default_result = {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "emotions": {
                    "joy": 0.0, "anger": 0.0, "fear": 0.0, "sadness": 0.0, "surprise": 0.0, "disgust": 0.0,
                },
                "is_sarcastic": False,
                "urgency": "low",
                "topics": [],
                "language": "en",
                "entities": {"people": [], "companies": [], "products": []},
            }

            parsed = {}
            if isinstance(response, str):
                try:
                    clean_response = response.strip()
                    if clean_response.startswith("```"):
                        parts = clean_response.split("```")
                        if len(parts) >= 2:
                            possible_json = parts[1]
                            if possible_json.strip().lower().startswith("json"):
                                    possible_json = possible_json.strip()[4:]
                            clean_response = possible_json.strip()
                    parsed = json.loads(clean_response)
                except json.JSONDecodeError:
                    import re
                    match = re.search(r'\{[\s\S]*\}', response)
                    if match:
                        try:
                            parsed = json.loads(match.group(0))
                        except json.JSONDecodeError:
                            raise ValueError("JSON parsing failed after regex extraction")
                    else:
                        raise ValueError("No JSON object found in response")
            elif isinstance(response, dict):
                parsed = response
            else:
                raise ValueError(f"Unexpected response type: {type(response)}")
            
            def get_safe_entities(data):
                """Parse entities with confidence filtering and relationship extraction."""
                CONFIDENCE_THRESHOLD = 0.7
                ents = data.get("entities")
                if not isinstance(ents, dict):
                    return {"people": [], "companies": [], "products": []}
                
                def filter_by_confidence(items):
                    """Filter entities by confidence threshold and normalize structure."""
                    result = []
                    for item in items:
                        if isinstance(item, str):
                            # Old format: just a string name - keep for backward compatibility
                            result.append(item)
                        elif isinstance(item, dict):
                            # New format: object with confidence
                            confidence = float(item.get("confidence", 0.8))
                            if confidence >= CONFIDENCE_THRESHOLD:
                                result.append(item)
                    return result
                
                return {
                    "people": filter_by_confidence(ents.get("people", [])),
                    "companies": filter_by_confidence(ents.get("companies", [])),
                    "products": filter_by_confidence(ents.get("products", []))
                }

            result = {
                "sentiment_score": self._clamp(float(parsed.get("sentiment_score", 0.0)), -1.0, 1.0),
                "sentiment_label": parsed.get("sentiment_label", "neutral") if parsed.get("sentiment_label") in ["positive", "neutral", "negative"] else "neutral",
                "emotions": {
                    "joy": self._clamp(float(parsed.get("emotions", {}).get("joy", 0.0)), 0.0, 1.0),
                    "anger": self._clamp(float(parsed.get("emotions", {}).get("anger", 0.0)), 0.0, 1.0),
                    "fear": self._clamp(float(parsed.get("emotions", {}).get("fear", 0.0)), 0.0, 1.0),
                    "sadness": self._clamp(float(parsed.get("emotions", {}).get("sadness", 0.0)), 0.0, 1.0),
                    "surprise": self._clamp(float(parsed.get("emotions", {}).get("surprise", 0.0)), 0.0, 1.0),
                    "disgust": self._clamp(float(parsed.get("emotions", {}).get("disgust", 0.0)), 0.0, 1.0),
                },
                "is_sarcastic": bool(parsed.get("is_sarcastic", False)),
                "urgency": parsed.get("urgency", "low") if parsed.get("urgency") in ["high", "medium", "low"] else "low",
                "topics": parsed.get("topics", []),
                "language": parsed.get("language", "en"),
                "entities": get_safe_entities(parsed),
                # Business fields
                "feature_requests": parsed.get("feature_requests", []),
                "pain_points": parsed.get("pain_points", []),
                "churn_risks": parsed.get("churn_risks", []),
                "recommended_actions": parsed.get("recommended_actions", []),
                "lead_score": int(parsed.get("lead_score", 0)),
            }
            
            # DEBUG: Log what was parsed from LLM
            entities = result.get("entities", {})
            logger.info(f"[LLM_PARSED] Entities: people={len(entities.get('people', []))}, "
                       f"companies={len(entities.get('companies', []))}, "
                       f"products={len(entities.get('products', []))} | "
                       f"FeatureReq={len(result.get('feature_requests', []))} | "
                       f"PainPoints={len(result.get('pain_points', []))}")
            
            return result
        except Exception as e:
            # FALLBACK: Use regex-based enhanced analysis
            logger.warning(f"LLM analyze_enhanced failed, using fallback: {e}")
            return fallback_analysis.analyze_enhanced_fallback(texts)

    async def detect_launch(self, prompt: str) -> dict[str, Any]:
        """Detect product launch (The Oracle)."""
        response = await invoke_launch_detection(
            prompt,
            timeout=self._timeout,
            brand=self._brand,
            chunk_id=self._chunk_id,
            operation="launch_detection",
            format_json=True
        )
        
        default_result = {
            "is_launch": False, 
            "product_name": "", 
            "success_score": 0, 
            "reason": "LLM response parsing failed",
            "hype_signals": [],
            "skepticism_signals": [],
            "reception": "none"
        }

        if isinstance(response, str):
            try:
                import re
                clean_response = response.strip()
                json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
                if json_match:
                    clean_response = json_match.group(0)
                parsed = json.loads(clean_response)
            except json.JSONDecodeError:
                 return default_result
        elif isinstance(response, dict):
            parsed = response
        else:
             return default_result
        
        # Return the full parsed response, as _parse_oracle_response expects
        # the original LLM output structure (is_launch, success_score, etc.)
        return parsed

    @staticmethod
    def _extract_last_json(text: str) -> dict | None:
        """Robustly extract the last valid JSON object from text."""
        import json
        text = text.strip()
        
        # Fast path: It is valid JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Markdown code block
        if "```json" in text:
            chunks = text.split("```json")
            if len(chunks) > 1:
                last_chunk = chunks[-1].split("```")[0].strip()
                try:
                    return json.loads(last_chunk)
                except json.JSONDecodeError:
                    pass
        
        # Scan for JSON objects
        decoder = json.JSONDecoder()
        idx = 0
        last_valid = None
        while idx < len(text):
            start = text.find('{', idx)
            if start == -1:
                break
            try:
                obj, end = decoder.raw_decode(text, start)
                last_valid = obj
                idx = end
            except json.JSONDecodeError:
                idx = start + 1
        
        return last_valid

    async def generate_response_suggestion(self, text: str, sentiment: str) -> list[str]:
        try:
            response = await invoke_response_suggestion(
                brand_name=self._brand,
                text=text,
                sentiment=sentiment,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="response_suggestion",
                format_json=True
            )
            
            clean = response.strip()
            if isinstance(clean, str):
                if clean.startswith("```"):
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                suggestions = json.loads(clean)
            elif isinstance(clean, list):
                suggestions = clean
            else:
                suggestions = []
                
            if isinstance(suggestions, list):
                return suggestions[:3]
            return []
            
        except Exception as e:
            logger.warning(f"LLM generate_suggestion failed, using fallback: {e}")
            # Fallback Templates
            if sentiment == "positive":
                return [
                    "Thank you so much for the kind words!",
                    "We're thrilled you're enjoying it! Let us know if you need anything.",
                    "Thanks for the support! It means the world to our team."
                ]
            elif sentiment == "negative":
                return [
                    "We're sorry to hear this. Please DM us so we can fix it.",
                    "This doesn't sound right. Could you reach out to support so we can help?",
                    "We appreciate the feedback and are actively working to improve this."
                ]
            else:
                 return [
                     "Thanks for mentioning us!",
                     "We appreciate the feedback.",
                     "Let us know if you have any questions!"
                 ]

    async def strategic_analyze(self, prompt: str, brand_name: str = "unknown") -> dict[str, Any]:
        """Perform strategic analysis/disambiguation via LLM."""
        response = await invoke_strategic(
            brand_name=brand_name,  # Pass the explicit brand name
            context="Strategic analysis request",
            text=prompt,
            timeout=self._timeout,
            brand=brand_name,       # Pass the explicit brand name for logging
            chunk_id=self._chunk_id,
            operation="strategic_analysis",
            format_json=True
        )
        
        clean_response = {}
        if isinstance(response, str):
            extracted = self._extract_last_json(response)
            if extracted is not None:
                clean_response = extracted
            else:
                return {"relevant": False, "summary": f"Failed to parse strategic analysis: {response[:50]}..."}
        elif isinstance(response, dict):
            clean_response = response
        else:
            return {"relevant": False, "summary": "Invalid response type"}
            
        return clean_response

    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(max_val, value))

    async def analyze_commercial_intent(self, text: str) -> dict[str, Any]:
        """V4.0 Money Mode: Analyze text for commercial/sales intent."""
        try:
            prompt = COMMERCIAL_INTENT_PROMPT.format(text=text)
            response = await invoke_general(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="commercial_intent",
                format_json=True
            )
            
            default_result = {
                "sales_intent": False,
                "confidence": 0.0,
                "intent_type": "none",
                "pain_point": None,
            }
            
            parsed = default_result
            if isinstance(response, str):
                extracted = self._extract_last_json(response)
                if extracted is not None:
                    parsed = extracted
            elif isinstance(response, dict):
                parsed = response
            
            valid_intents = ["alternative_seeking", "price_sensitive", "feature_request", "complaint", "comparison_shopping", "none"]
            return {
                "sales_intent": bool(parsed.get("sales_intent", False)),
                "confidence": self._clamp(float(parsed.get("confidence", 0.0)), 0.0, 1.0),
                "intent_type": parsed.get("intent_type", "none") if parsed.get("intent_type") in valid_intents else "none",
                "pain_point": parsed.get("pain_point") if isinstance(parsed.get("pain_point"), str) else None,
            }
        except Exception as e:
            # FALLBACK: Use regex-based commercial intent analysis
            logger.warning(f"LLM analyze_commercial_intent failed, using fallback: {e}")
            return fallback_analysis.analyze_commercial_intent_fallback(text)

    async def categorize_competitor_complaint(self, text: str, competitor_name: str) -> dict[str, Any]:
        """V4.0 Market Gap: Categorize a competitor complaint."""
        try:
            prompt = COMPETITOR_COMPLAINT_PROMPT.format(text=text, competitor_name=competitor_name)
            response = await invoke_competitor_analysis(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="competitor_complaint",
                format_json=True
            )
            
            default_result = {
                "category": "other",
                "specific_issue": "Unknown issue",
                "pain_level": 5,
            }
            
            if isinstance(response, str):
                try:
                    clean_response = response.strip()
                    if clean_response.startswith("```"):
                        clean_response = clean_response.split("```")[1]
                        if clean_response.startswith("json"):
                            clean_response = clean_response[4:]
                    parsed = json.loads(clean_response)
                except json.JSONDecodeError:
                    return default_result
            elif isinstance(response, dict):
                parsed = response
            else:
                return default_result
            
            valid_categories = ["pricing", "missing_features", "support_issues", "performance", "usability", "reliability", "other"]
            return {
                "category": parsed.get("category", "other") if parsed.get("category") in valid_categories else "other",
                "specific_issue": str(parsed.get("specific_issue", "Unknown issue"))[:500],
                "pain_level": max(1, min(10, int(parsed.get("pain_level", 5)))),
            }
        except Exception as e:
            # FALLBACK: Use regex-based complaint categorization
            logger.warning(f"LLM categorize_competitor_complaint failed, using fallback: {e}")
            return fallback_analysis.categorize_complaint_fallback(text)

    async def analyze_web_content(self, brand_name: str, scraped_content: list[dict]) -> dict[str, Any]:
        """Analyze scraped web content about a brand using the LLM."""
        if not scraped_content:
            return {"insights": [], "competitors": [], "opportunities": []}
            
        content_summary = "\n\n".join([
            f"Source: {item.get('title', 'Unknown')}\n{item.get('snippet', '')[:500]}"
            for item in scraped_content[:5]
        ])
        
        prompt = WEB_INSIGHTS_PROMPT.format(brand_name=brand_name, scraped_content=content_summary)
        
        try:
            result = await invoke_web_insights(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="web_insights",
                format_json=True
            )
            return result if isinstance(result, dict) else {"insights": [], "competitors": [], "opportunities": []}
        except Exception as e:
            logger.error(f"Web content analysis failed: {e}")
            return {"insights": [], "competitors": [], "opportunities": []}
    
    async def detect_competitors(self, brand_name: str, brand_description: str | None, brand_keywords: list[str] | None) -> dict[str, Any]:
        """Use LLM to detect competitors based on brand information."""
        keywords_str = ", ".join(brand_keywords) if brand_keywords else "None provided"
        desc_str = brand_description or "Not provided"
        
        prompt = f"""You are a market research analyst identifying competitors for a brand.

Brand Name: {brand_name}
Description: {desc_str}  
Keywords: {keywords_str}

Task: Identify 5-10 REAL direct competitors in the same industry/market.

IMPORTANT RULES:
- ONLY include REAL companies you are CERTAIN exist
- Do NOT make up fictional competitors
- Set confidence < 0.7 for any competitor you're unsure about
- Include their KEY PRODUCTS that compete with {brand_name}

For each competitor, provide:
1. name - Official company/brand name
2. keywords - Array of 3-5 relevant keywords for monitoring mentions
3. products - Array of 2-4 key products/services that compete with {brand_name}
4. confidence - Score from 0.0 to 1.0 (only include if >= 0.7)
5. reason - One sentence explaining the competitive relationship
6. website - Official website URL if known (or null)

Return JSON:
{{
    "competitors": [
        {{ 
            "name": "Competitor Corp", 
            "keywords": ["keyword1", "keyword2"], 
            "products": ["Product A", "Service B"],
            "confidence": 0.95, 
            "reason": "They offer similar services in the same market",
            "website": "https://competitor.com"
        }}
    ]
}}
"""
        try:
            result = await invoke_prompt_text(
                prompt,
                timeout=self._timeout,
                brand=brand_name,
                chunk_id=self._chunk_id,
                operation="competitor_detection",
                format_json=True
            )
            
            if isinstance(result, str):
                try:
                    clean_response = result.strip()
                    if clean_response.startswith("```"):
                        clean_response = clean_response.split("```")[1]
                        if clean_response.startswith("json"):
                            clean_response = clean_response[4:]
                    return json.loads(clean_response)
                except json.JSONDecodeError:
                    return {"competitors": []}
            elif isinstance(result, dict):
                return result
            else:
                return {"competitors": []}
        except Exception as e:
            logger.error(f"Competitor detection failed: {e}")
            return {"competitors": []}

    async def generate_insights(self, brand_name: str) -> dict[str, Any]:
        """Generate web insights report for a brand using LLM knowledge."""
        prompt = f"""Act as an expert market researcher. Perform a "Deep Web Scan" analysis for the brand: "{brand_name}".
        
Generate a JSON report with the following structure:
{{
    "summary": "Executive summary of the brand's current online standing...",
    "sentiment": "positive" | "neutral" | "negative" | "mixed",
    "key_themes": ["theme1", "theme2", ...],
    "notable_mentions": [
        {{ "source": "TechCrunch", "highlight": "Recent news...", "sentiment": "positive" }},
        {{ "source": "Reddit", "highlight": "Community feedback...", "sentiment": "neutral" }}
    ],
    "opportunities": ["Opportunity 1", "Opportunity 2", ...],
    "risks": ["Risk 1", "Risk 2", ...],
    "recommended_actions": ["Action 1", "Action 2", ...]
}}

Ensure the data is realistic and based on general knowledge of the brand (or plausible if unknown).
Return only the JSON object, no other text."""
        
        result = await invoke_prompt_text(
            prompt,
            timeout=self._timeout,
            brand=self._brand,
            chunk_id=self._chunk_id,
            operation="web_insights",
            format_json=True
        )
        
        if isinstance(result, str):
            try:
                clean_response = result.strip()
                if clean_response.startswith("```"):
                    clean_response = clean_response.split("```")[1]
                    if clean_response.startswith("json"):
                        clean_response = clean_response[4:]
                return json.loads(clean_response)
            except json.JSONDecodeError:
                # Return partial result with the text
                return {
                    "summary": result[:500],
                    "sentiment": "neutral",
                    "key_themes": [],
                    "notable_mentions": [],
                    "opportunities": [],
                    "risks": [],
                    "recommended_actions": []
                }
            return result
        else:
            return {
                "summary": "Analysis complete but no structured data returned.",
                "sentiment": "neutral",
                "key_themes": [],
                "notable_mentions": [],
                "opportunities": [],
                "risks": [],
                "recommended_actions": []
            }

    async def analyze_competitor_mentions(self, prompt: str) -> Dict[str, Any]:
        """Analyze mentions text to extract competitor companies."""
        try:
            result = await invoke_prompt_text(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="competitor_mentions",
                format_json=True
            )
            
            if isinstance(result, str):
                clean_response = result.strip()
                if clean_response.startswith("```"):
                    clean_response = clean_response.split("```")[1]
                    if clean_response.startswith("json"):
                        clean_response = clean_response[4:]
                return json.loads(clean_response)
            elif isinstance(result, dict):
                return result
            return {"competitors": []}
        except Exception as e:
            logger.warning(f"analyze_competitor_mentions failed: {e}")
            return {"competitors": []}

    async def analyze_competitor_web_content(self, prompt: str) -> Dict[str, Any]:
        """Analyze scraped web content to extract competitor information."""
        try:
            result = await invoke_prompt_text(
                prompt,
                timeout=self._timeout,
                brand=self._brand,
                chunk_id=self._chunk_id,
                operation="competitor_web_analysis",
                format_json=True
            )
            
            if isinstance(result, str):
                clean_response = result.strip()
                if clean_response.startswith("```"):
                    clean_response = clean_response.split("```")[1]
                    if clean_response.startswith("json"):
                        clean_response = clean_response[4:]
                return json.loads(clean_response)
            elif isinstance(result, dict):
                return result
            return {"summary": "Analysis failed", "competitors": []}
        except Exception as e:
            logger.warning(f"analyze_competitor_web_content failed: {e}")
            return {"summary": f"Analysis failed: {str(e)[:100]}", "competitors": []}


def _build_chat_models(settings: Any) -> tuple[Any, Any]:
    """Build chat models - deprecated, now handled by llm_executor."""
    # We no longer instantiate ChatOllama here to avoid warnings and unused connections
    # The LangChainLLMAdapter methods delegate to llm_executor
    return None, None


def get_llm_adapter(worker_id: str) -> InstrumentedLLMAdapter:
    """Factory for LLM adapter."""
    settings = get_settings()
    primary, fallback = _build_chat_models(settings)
    
    adapter = LangChainLLMAdapter(
        primary=primary,
        fallback=fallback,
        max_tokens=256,
        timeout=settings.llm_timeout_sec,
        worker_id=worker_id,
    )
    from .llm_adapter import InstrumentedLLMAdapter
    return InstrumentedLLMAdapter(adapter)
    
@dataclass
class InstrumentedLLMAdapter:
    """Wrapper for metrics and logging."""
    _adapter: LangChainLLMAdapter
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self._adapter, name)

    async def summarize(self, texts: list[str]) -> str:
        start = time.time()
        try:
            return await self._adapter.summarize(texts)
        finally:
            worker_llm_latency_seconds.labels(
                worker_id=self._adapter._worker_id,
                brand=self._adapter._brand,
                operation="summary"
            ).observe(time.time() - start)

    async def sentiment(self, texts: list[str]) -> dict[str, float]:
        start = time.time()
        try:
            return await self._adapter.sentiment(texts)
        finally:
            worker_llm_latency_seconds.labels(
                worker_id=self._adapter._worker_id,
                brand=self._adapter._brand,
                operation="sentiment"
            ).observe(time.time() - start)
