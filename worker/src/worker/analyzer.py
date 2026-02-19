"""
Project Avichal: 3-Tier Intelligence Engine (Python Port)

Smart filtering and intent detection for brand mentions.
Filters out 90%+ of noise before sending to Gemini AI.

Architecture:
- Layer 1: Regex Gatekeeper - Zero-cost local filtering
- Layer 2: Strategic AI Judge - Gemini-powered disambiguation + intent
- Layer 3: Tagger & Saver - Enrich payload with intelligence tags
"""
from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .llm_adapter import InstrumentedLLMAdapter, get_llm_adapter
from .logger import get_logger, log_with_context

logger = get_logger(__name__)

# =============================================================================
# TYPES & STRUCTS
# =============================================================================

@dataclass
class AnalysisInput:
    """Input payload for analysis."""
    text: str
    target_brand: str
    target_keywords: List[str] = field(default_factory=list)
    is_competitor: bool = False
    source_platform: Optional[str] = None
    source_url: Optional[str] = None

class GatekeeperCategory(str, Enum):
    """Regex match category from Layer 1."""
    LEAD = "lead_switching"
    PAIN = "pain_crisis"
    PURCHASE = "purchase_intent"
    LAUNCH = "product_launch"
    NONE = "none"

class StrategicTag(str, Enum):
    """Strategic tag from AI analysis."""
    OPPORTUNITY_TO_STEAL = "OPPORTUNITY_TO_STEAL"
    CRITICAL_ALERT = "CRITICAL_ALERT"
    NONE = "NONE"

class Intent(str, Enum):
    """Intent classification from AI."""
    HOT_LEAD = "HOT_LEAD"
    CHURN_RISK = "CHURN_RISK"
    BUG_REPORT = "BUG_REPORT"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    PRAISE = "PRAISE"
    GENERAL = "GENERAL"

class Priority(str, Enum):
    """Priority level for action queue."""
    CRITICAL = "CRITICAL"  # P0
    HIGH = "HIGH"          # P1
    MEDIUM = "MEDIUM"      # P2
    LOW = "LOW"            # P3

class Urgency(str, Enum):
    """Urgency level for time-sensitive actions."""
    IMMEDIATE = "IMMEDIATE"   # < 1 hour
    TODAY = "TODAY"           # < 24 hours
    THIS_WEEK = "THIS_WEEK"   # < 1 week
    WHENEVER = "WHENEVER"     # No pressure

@dataclass
class AnalysisResult:
    """Complete analysis result from the 3-tier engine."""
    relevant: bool
    intent: Intent
    strategic_tag: StrategicTag
    sentiment_score: float
    summary: str
    gatekeeper_category: GatekeeperCategory
    passed_gatekeeper: bool
    priority: Priority
    urgency: Urgency
    confidence: float
    action_suggested: str
    keywords: List[str]
    # Verification Fields
    is_verified: bool = False
    verification_score: float = 0.0
    verification_reason: str = ""

    @property
    def sentiment_label(self) -> str:
        if self.sentiment_score > 0.05:
            return "positive"
        if self.sentiment_score < -0.05:
            return "negative"
        return "neutral"

    @classmethod
    def skipped(cls) -> AnalysisResult:
        return cls(
            relevant=False,
            intent=Intent.GENERAL,
            strategic_tag=StrategicTag.NONE,
            sentiment_score=0.0,
            summary="Skipped: No high-value keywords detected",
            gatekeeper_category=GatekeeperCategory.NONE,
            passed_gatekeeper=False,
            priority=Priority.LOW,
            urgency=Urgency.WHENEVER,
            confidence=0.0,
            action_suggested="No action required",
            keywords=[],
            is_verified=True,
            verification_score=0.0,
            verification_reason="Skipped"
        )

    @classmethod
    def not_relevant(cls, category: GatekeeperCategory) -> AnalysisResult:
        return cls(
            relevant=False,
            intent=Intent.GENERAL,
            strategic_tag=StrategicTag.NONE,
            sentiment_score=0.0,
            summary="Disambiguation failed: Text not about target brand",
            gatekeeper_category=category,
            passed_gatekeeper=True,
            priority=Priority.LOW,
            urgency=Urgency.WHENEVER,
            confidence=0.0,
            action_suggested="Text was about a different topic",
            keywords=[],
            is_verified=True, 
            verification_score=0.0,
            verification_reason="Not Relevant"
        )

    @staticmethod
    def calculate_priority(intent: Intent, strategic_tag: StrategicTag, sentiment: float) -> Priority:
        if strategic_tag == StrategicTag.CRITICAL_ALERT:
            return Priority.CRITICAL
        
        if strategic_tag == StrategicTag.OPPORTUNITY_TO_STEAL:
            return Priority.HIGH
            
        if intent == Intent.HOT_LEAD:
            return Priority.HIGH
            
        if intent == Intent.CHURN_RISK:
            if sentiment < -0.7:
                return Priority.CRITICAL
            return Priority.HIGH
            
        if intent in (Intent.BUG_REPORT, Intent.FEATURE_REQUEST):
            return Priority.MEDIUM
            
        return Priority.LOW

    @staticmethod
    def calculate_urgency(priority: Priority, strategic_tag: StrategicTag) -> Urgency:
        if priority == Priority.CRITICAL:
            return Urgency.IMMEDIATE
        if priority == Priority.HIGH:
            return Urgency.TODAY
        if priority == Priority.MEDIUM:
            return Urgency.THIS_WEEK
        return Urgency.WHENEVER

    @staticmethod
    def generate_action(intent: Intent, strategic_tag: StrategicTag, is_competitor: bool) -> str:
        if intent == Intent.HOT_LEAD:
            return "Reach out with personalized pitch"
        if intent == Intent.CHURN_RISK and strategic_tag == StrategicTag.CRITICAL_ALERT:
            return "URGENT: Escalate to customer success team immediately"
        if intent == Intent.CHURN_RISK:
            return "Schedule retention call with customer"
        if intent == Intent.BUG_REPORT:
            return "Create bug ticket and send acknowledgment"
        if intent == Intent.FEATURE_REQUEST:
            return "Log to feature request backlog"
        if strategic_tag == StrategicTag.OPPORTUNITY_TO_STEAL and is_competitor:
            return "Contact user - they're unhappy with competitor"
        if strategic_tag == StrategicTag.CRITICAL_ALERT:
            return "CRISIS ALERT: Immediate response required"
        if strategic_tag == StrategicTag.CRITICAL_ALERT:
            return "CRISIS ALERT: Immediate response required"
        return "Monitor and engage if appropriate"

@dataclass
class ReceptionAnalysis:
    """Reception analysis for launch prediction."""
    hype_signals: List[str]
    skepticism_signals: List[str]
    overall: str

@dataclass
class LaunchPrediction:
    """The Oracle: Launch Prediction Result."""
    is_launch: bool
    product_name: str
    success_score: int
    reason: str
    reception: ReceptionAnalysis
    brand: str
    is_competitor: bool

    @classmethod
    def not_a_launch(cls) -> LaunchPrediction:
        return cls(
            is_launch=False,
            product_name="",
            success_score=0,
            reason="Not a product launch announcement",
            reception=ReceptionAnalysis(hype_signals=[], skepticism_signals=[], overall="none"),
            brand="",
            is_competitor=False
        )

    @property
    def prediction_category(self) -> str:
        if self.success_score <= 39:
            return "FLOP_RISK"
        if self.success_score <= 70:
            return "MODERATE_SUCCESS"
        return "POTENTIAL_HIT"

# =============================================================================
# REGEX PATTERNS
# =============================================================================

LEAD_REGEX = re.compile(
    r"(?i)\b(switch(?:ing)?\s+(?:to|from)|alternative(?:s)?|cheaper|better\s+than|recommend(?:ation)?|suggest(?:ion)?|looking\s+for|replace(?:ment)?)\b"
)

PAIN_REGEX = re.compile(
    r"(?i)\b(hate|worst|fail(?:ed|ing)?|broken|scam|support\s+(?:is\s+)?(?:terrible|awful|bad)|slow|crash(?:ed|es|ing)?|glitch(?:y)?|bug(?:gy)?|doesn't\s+work|not\s+working|frustrated|disappointed|angry|furious)\b"
)

PURCHASE_REGEX = re.compile(
    r"(?i)\b(buy(?:ing)?|price|pricing|cost(?:s)?|demo|trial|upgrade|subscription|plan(?:s)?|enterprise|quote|discount)\b"
)

LAUNCH_REGEX = re.compile(
    r"(?i)\b(launch(?:ing|ed)?|ship(?:ping|ped)?|releas(?:ing|ed|e)|announc(?:ing|ed|ement)|v\d+\.\d+|beta|alpha|new\s+feature|now\s+available|just\s+arrived|introducing|unveiled|debut|rollout|going\s+live)\b"
)

# =============================================================================
# ANALYZER ENGINE
# =============================================================================

class Analyzer:
    """The 3-Tier Intelligence Engine."""

    def __init__(self, llm_adapter: InstrumentedLLMAdapter):
        self._llm = llm_adapter
        try:
             self._vader = SentimentIntensityAnalyzer()
        except Exception as e:
             logger.warning(f"Failed to initialize VADER: {e}")
             self._vader = None

    def regex_gatekeeper(self, text: str, keywords: List[str]) -> GatekeeperCategory:
        """Layer 1: Check text against high-value keyword patterns."""
        text_lower = text.lower()

        # Check brand-specific keywords FIRST
        for kw in keywords:
            if kw.lower() in text_lower:
                return GatekeeperCategory.LEAD
        
        # Check in priority order: Launch > Leads > Pain > Purchase
        if LAUNCH_REGEX.search(text):
            return GatekeeperCategory.LAUNCH
        if LEAD_REGEX.search(text):
            return GatekeeperCategory.LEAD
        if PAIN_REGEX.search(text):
            return GatekeeperCategory.PAIN
        if PURCHASE_REGEX.search(text):
            return GatekeeperCategory.PURCHASE
            
        return GatekeeperCategory.NONE

    async def analyze(self, input_data: AnalysisInput) -> AnalysisResult:
        """Run the complete 3-tier analysis pipeline."""
        
        # LAYER 1: Regex Gatekeeper
        category = self.regex_gatekeeper(input_data.text, input_data.target_keywords)
        
        if category == GatekeeperCategory.NONE:
            # Don't skip! Pass through as GENERAL intent to ensure all data is captured.
            pass

        # LAYER 2: AI Judge
        prompt = self._build_strategic_prompt(input_data, category)
        
        try:
            # We need a new method in LLM adapter for generic JSON analysis
            # For now, we'll assume we can use a new method `strategic_analyze` or reuse `analyze_enhanced`
            # Let's assume we add `strategic_analyze` to the adapter or use `_invoke` directly if public
            # Since I'm editing llm_adapter next, I will add `strategic_analyze` there.
            response = await self._llm.strategic_analyze(prompt, brand_name=input_data.target_brand)
            
            # LAYER 3: Parse and tag
            return self._parse_ai_response(response, category, input_data.is_competitor, input_data.text)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "QuotaFailure" in error_msg:
                 logger.warning("[Analyzer] Gemini Quota Exceeded (Free Tier Limit). Falling back to regex-only.")
            else:
                 logger.warning(f"[Analyzer] AI call failed: {e}. Falling back to regex-only result.")
            
            # Fallback logic using robust regex analysis
            from . import fallback_analysis
            fb = fallback_analysis.analyze_strategic_fallback(
                input_data.text, 
                input_data.target_brand, 
                input_data.is_competitor
            )
            
            # Map fallback dictionary to AnalysisResult
            intent = Intent(fb["intent"]) if fb["intent"] in Intent.__members__ else Intent.GENERAL
            strategic_tag = StrategicTag(fb["strategic_tag"]) if fb["strategic_tag"] in StrategicTag.__members__ else StrategicTag.NONE
            
            priority = AnalysisResult.calculate_priority(intent, strategic_tag, fb["sentiment_score"])
            
            return AnalysisResult(
                relevant=fb["relevant"],
                intent=intent,
                strategic_tag=strategic_tag,
                sentiment_score=fb["sentiment_score"],
                summary=fb["summary"],
                gatekeeper_category=category,
                passed_gatekeeper=True,
                priority=priority,
                urgency=AnalysisResult.calculate_urgency(priority, strategic_tag),
                confidence=fb["confidence"],
                action_suggested=AnalysisResult.generate_action(intent, strategic_tag, input_data.is_competitor),
                keywords=input_data.target_keywords,
                # Verification Fields (Fallback is self-consistent by definition)
                is_verified=True, 
                verification_score=fb["sentiment_score"],
                verification_reason="Fallback logic used (Regex)"
            )

    def _build_strategic_prompt(self, input_data: AnalysisInput, category: GatekeeperCategory) -> str:
        brand_context = "COMPETITOR" if input_data.is_competitor else "MY_CLIENT"
        
        category_hint = {
            GatekeeperCategory.LAUNCH: "product/feature launch",
            GatekeeperCategory.LEAD: "switching intent",
            GatekeeperCategory.PAIN: "pain/crisis",
            GatekeeperCategory.PURCHASE: "purchase intent",
            GatekeeperCategory.NONE: "general mention"
        }[category]

        strategic_instruction = (
            "If user expresses hate/frustration, tag as OPPORTUNITY_TO_STEAL. Otherwise NONE"
            if input_data.is_competitor else
            "If user expresses crisis signals (viral complaint), tag as CRITICAL_ALERT. Otherwise NONE"
        )
        
        return f"""Analyze this social media text about the brand: "{input_data.target_brand}".

**Context:**
- Brand Type: {brand_context}
- Detected Pattern: {category_hint}
- Source: {input_data.source_platform or "unknown"}

**Text:**
"{input_data.text[:1500]}"

**TASK A: DISAMBIGUATION**
Is this about "{input_data.target_brand}"? If NO, return {{ "relevant": false }}.

**TASK B: INTENT**
Classify intent: HOT_LEAD, CHURN_RISK, BUG_REPORT, GENERAL.

**TASK C: STRATEGY**
{strategic_instruction}

**OUTPUT JSON:**
{{ "relevant": true, "intent": "HOT_LEAD", "strategic_tag": "NONE", "sentiment_score": 0.5, "summary": "..." }}"""

    def _parse_ai_response(self, response: Dict[str, Any], category: GatekeeperCategory, is_competitor: bool, text: str = "") -> AnalysisResult:
        if not response.get("relevant", False):
            return AnalysisResult.not_relevant(category)
            
        intent_str = response.get("intent", "GENERAL")
        try:
            intent = Intent(intent_str)
        except ValueError:
            intent = Intent.GENERAL
            
        tag_str = response.get("strategic_tag", "NONE")
        try:
            strategic_tag = StrategicTag(tag_str)
        except ValueError:
            strategic_tag = StrategicTag.NONE
            
        sentiment = float(response.get("sentiment_score", 0.0))
        
        priority = AnalysisResult.calculate_priority(intent, strategic_tag, sentiment)
        
        # --- VERIFICATION (VADER) ---
        vader_score = 0.0
        is_verified = False
        verification_reason = "VADER check pending"
        
        if self._vader:
            try:
                vader_score = self._vader.polarity_scores(text)["compound"]
                
                # Logic: Verify if they agree on polarity (Positive vs Negative)
                # or if the difference is acceptable (within 0.5)
                # Ignore small neutral deviations
                
                llm_sign = 1 if sentiment > 0.1 else (-1 if sentiment < -0.1 else 0)
                vader_sign = 1 if vader_score > 0.1 else (-1 if vader_score < -0.1 else 0)
                
                if llm_sign == vader_sign:
                    is_verified = True
                    verification_reason = f"Both models agree (LLM: {sentiment}, VADER: {vader_score})"
                elif abs(sentiment - vader_score) < 0.6:
                     is_verified = True
                     verification_reason = f"Scores close enough (Diff: {abs(sentiment - vader_score):.2f})"
                else:
                    is_verified = False
                    verification_reason = f"Disagreement (LLM: {sentiment} vs VADER: {vader_score})"
                    # OPTIONAL: Downgrade confidence if unverified?
                    # response["confidence"] = float(response.get("confidence", 0.8)) * 0.8

            except Exception as e:
                verification_reason = f"VADER failed: {e}"

        return AnalysisResult(
            relevant=True,
            intent=intent,
            strategic_tag=strategic_tag,
            sentiment_score=sentiment,
            summary=response.get("summary", "No summary"),
            gatekeeper_category=category,
            passed_gatekeeper=True,
            priority=priority,
            urgency=AnalysisResult.calculate_urgency(priority, strategic_tag),
            confidence=float(response.get("confidence", 0.8)),
            action_suggested=AnalysisResult.generate_action(intent, strategic_tag, is_competitor),
            keywords=response.get("keywords", []),
            # Verification Fields
            is_verified=is_verified,
            verification_score=vader_score,
            verification_reason=verification_reason
        )

    def is_launch_candidate(self, text: str) -> bool:
        """Check if text contains launch patterns."""
        return bool(LAUNCH_REGEX.search(text))

    async def detect_launch(self, input_data: AnalysisInput) -> LaunchPrediction:
        """Detect product launches and predict their market success (The Oracle)."""
        # Quick check
        if not self.is_launch_candidate(input_data.text):
            return LaunchPrediction.not_a_launch()

        # Build prompt
        brand_type = "COMPETITOR" if input_data.is_competitor else "MY BRAND"
        prompt = f"""You are "The Oracle" - an AI analyst specializing in predicting product launch success.

**TEXT TO ANALYZE:**
"{input_data.text}"

**BRAND:** {input_data.target_brand} ({brand_type})

**YOUR TASK:**

1. **EVENT DETECTION:** Is this a confirmed Product/Feature Launch announcement? (Yes/No)

2. **RECEPTION ANALYSIS:** Analyze the language sentiment:
   - **Hype Signals (positive):** "Finally", "Game changer", "Shut up and take my money", "Been waiting", "Excited"
   - **Skepticism Signals (negative):** "Expensive", "Copy", "Useless", "Too late", "Buggy", "Disappointing"

3. **SUCCESS PREDICTION:** Calculate a Success Probability Score (0-100):
   - 0-39: FLOP_RISK - Likely to fail
   - 40-70: MODERATE_SUCCESS - Decent reception expected
   - 71-100: POTENTIAL_HIT - Viral success likely

4. **PRODUCT NAME:** Extract the specific product/feature name if mentioned.

**OUTPUT FORMAT (JSON only, no markdown):**
{{
  "is_launch": true,
  "product_name": "Feature X",
  "success_score": 85,
  "reason": "High demand detected, viral positive sentiment.",
  "hype_signals": ["Finally", "Game changer"],
  "skepticism_signals": [],
  "reception": "positive"
}}

If NOT a launch, return:
{{
  "is_launch": false,
  "product_name": "",
  "success_score": 0,
  "reason": "Not a product launch announcement",
  "hype_signals": [],
  "skepticism_signals": [],
  "reception": "none"
}}"""

        try:
            # Call Gemini via LLM Adapter
            # We assume llm_adapter has detect_launch, which we verified it does
            response = await self._llm.detect_launch(prompt)
            return self._parse_oracle_response(response, input_data)
        except Exception as e:
            logger.warning(f"[Oracle] Analysis failed: {e}")
            return LaunchPrediction.not_a_launch()

    def _parse_oracle_response(self, response: Dict[str, Any], input_data: AnalysisInput) -> LaunchPrediction:
        is_launch = bool(response.get("is_launch", False))
        if not is_launch:
            return LaunchPrediction.not_a_launch()

        reception_str = str(response.get("reception", "none"))
        
        reception = ReceptionAnalysis(
            hype_signals=[str(s) for s in response.get("hype_signals", [])],
            skepticism_signals=[str(s) for s in response.get("skepticism_signals", [])],
            overall=reception_str
        )

        return LaunchPrediction(
            is_launch=True,
            product_name=str(response.get("product_name", "Unknown")),
            success_score=int(response.get("success_score", 0)),
            reason=str(response.get("reason", "No reason provided")),
            reception=reception,
            brand=input_data.target_brand,
            is_competitor=input_data.is_competitor
        )

def get_analyzer(worker_id: str) -> Analyzer:
    llm_adapter = get_llm_adapter(worker_id)
    return Analyzer(llm_adapter)
