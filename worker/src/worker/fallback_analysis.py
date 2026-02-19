"""Robust fallback analysis when LLM providers are unavailable.

This module provides regex-based and rule-based alternatives to LLM analysis,
ensuring core features work even when all LLM providers fail.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Any


# =============================================================================
# SENTIMENT WORD LISTS
# =============================================================================

POSITIVE_WORDS = frozenset([
    # Strong positive
    "love", "amazing", "awesome", "excellent", "fantastic", "brilliant", "outstanding",
    "perfect", "wonderful", "incredible", "superb", "phenomenal", "exceptional",
    # Moderate positive
    "good", "great", "nice", "happy", "glad", "pleased", "satisfied", "enjoy",
    "like", "helpful", "useful", "easy", "fast", "quick", "reliable", "impressed",
    "recommend", "best", "favorite", "favourite", "thanks", "thank", "appreciate",
    # Product positive
    "works", "working", "solved", "fixed", "improved", "upgrade", "better", "smooth",
])

NEGATIVE_WORDS = frozenset([
    # Strong negative
    "hate", "terrible", "awful", "horrible", "worst", "disgusting", "pathetic",
    "useless", "garbage", "trash", "crap", "scam", "fraud",
    # Moderate negative
    "bad", "poor", "slow", "broken", "bug", "buggy", "crash", "crashing", "crashed",
    "fail", "failed", "failing", "error", "issue", "problem", "annoying", "frustrating",
    "disappointed", "disappointing", "upset", "angry", "furious", "unacceptable",
    # Product negative
    "doesn't work", "not working", "stopped", "glitch", "laggy", "unusable",
    "refund", "cancel", "unsubscribe", "switch", "leaving", "alternative",
])

INTENSIFIERS = frozenset([
    "very", "really", "extremely", "absolutely", "totally", "completely", "so",
    "such", "incredibly", "super", "seriously", "genuinely", "truly",
])

NEGATORS = frozenset([
    "not", "no", "never", "neither", "nobody", "nothing", "nowhere",
    "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't",
    "shouldn't", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
])


# =============================================================================
# INTENT PATTERNS
# =============================================================================

HOT_LEAD_PATTERNS = [
    re.compile(r"\b(want(?:s|ed)?|need(?:s|ed)?|looking\s+for|interested\s+in)\b.*\b(buy|purchase|get|try|subscribe|demo|trial)\b", re.I),
    re.compile(r"\b(where\s+can\s+i|how\s+do\s+i|how\s+can\s+i)\s+(?:buy|get|purchase|subscribe|sign\s*up)\b", re.I),
    re.compile(r"\b(thinking\s+(?:of|about)|considering|planning\s+to)\s+(?:buy|get|switch|try)\b", re.I),
    re.compile(r"\b(price|pricing|cost|how\s+much|discount|deal|offer|promo)\b", re.I),
    re.compile(r"\b(upgrade|subscribe|premium|pro\s+plan|enterprise)\b", re.I),
    re.compile(r"\bshut\s+up\s+and\s+take\s+my\s+money\b", re.I),
    re.compile(r"\btake\s+my\s+money\b", re.I),
]

CHURN_RISK_PATTERNS = [
    re.compile(r"\b(cancel|cancelling|canceling|cancelled|canceled)\b", re.I),
    re.compile(r"\b(unsubscribe|unsubscribing|unsubscribed)\b", re.I),
    re.compile(r"\b(switching|switch\s+to|moving\s+to|leaving|left)\b.*\b(alternative|competitor|another)\b", re.I),
    re.compile(r"\b(refund|money\s+back|waste\s+of\s+money)\b", re.I),
    re.compile(r"\b(giving\s+up|fed\s+up|done\s+with|had\s+enough)\b", re.I),
    re.compile(r"\b(not\s+worth|overpriced|too\s+expensive)\b", re.I),
]

BUG_REPORT_PATTERNS = [
    re.compile(r"\b(bug|error|crash|crashing|crashed|glitch|broken)\b", re.I),
    re.compile(r"\b(doesn't|does\s+not|won't|will\s+not)\s+work\b", re.I),
    re.compile(r"\b(not\s+working|stopped\s+working|keeps\s+crashing)\b", re.I),
    re.compile(r"\b(issue|problem)\s+with\b", re.I),
    re.compile(r"\b(fix|please\s+fix|needs?\s+to\s+be\s+fixed)\b", re.I),
]

FEATURE_REQUEST_PATTERNS = [
    re.compile(r"\b(feature\s+request|can\s+you\s+add|please\s+add|would\s+be\s+nice)\b", re.I),
    re.compile(r"\b(wish|hoping|hope)\s+(you|it|they)\s+(had|would|could)\b", re.I),
    re.compile(r"\b(should\s+have|need(?:s)?\s+to\s+have|missing)\b", re.I),
    re.compile(r"\b(when\s+will|eta\s+on|roadmap|planned)\b", re.I),
]

PRAISE_PATTERNS = [
    re.compile(r"\b(love|loving|loved)\s+(?:this|it|the|your)\b", re.I),
    re.compile(r"\b(amazing|awesome|excellent|fantastic|brilliant|best)\b", re.I),
    re.compile(r"\b(thank\s+you|thanks|kudos|shoutout|shout\s+out)\b", re.I),
    re.compile(r"\b(recommend|recommended|highly\s+recommend)\b", re.I),
    re.compile(r"\b(game\s+changer|life\s+saver|must\s+have)\b", re.I),
]


# =============================================================================
# ENTITY PATTERNS
# =============================================================================

# Common tech companies
COMPANY_PATTERNS = [
    re.compile(r"\b(Google|Meta|Facebook|Microsoft|Apple|Amazon|Netflix|Twitter|X|LinkedIn|Slack|Zoom|Stripe|Shopify|Salesforce|Adobe|Oracle|IBM|Intel|AMD|Nvidia|Tesla|SpaceX)\b", re.I),
]

# Product patterns (generic)
PRODUCT_PATTERNS = [
    re.compile(r"\b(\w+(?:\s+(?:Pro|Plus|Premium|Enterprise|Free|Basic|Standard|Ultimate))?(?:\s+(?:Plan|Tier|Edition|Version)))\b"),
    re.compile(r"\b(v\d+(?:\.\d+)*)\b"),  # Version patterns
]


# =============================================================================
# FALLBACK FUNCTIONS
# =============================================================================


# =============================================================================
# EMOTION KEYWORDS (Rule-Based)
# =============================================================================

EMOTION_KEYWORDS = {
    "joy": frozenset([
        "happy", "joy", "excited", "love", "awesome", "great", "amazing", "thrilled", 
        "delighted", "fun", "enjoy", "smile", "laugh", "wonderful", "celebrate"
    ]),
    "anger": frozenset([
        "angry", "mad", "hate", "furious", "rage", "annoyed", "pissed", "stupid", 
        "idiot", "worst", "horrible", "awful", "terrible", "disgusting", "trash"
    ]),
    "sadness": frozenset([
        "sad", "depressed", "unhappy", "cry", "crying", "tears", "sorry", "miss", 
        "grief", "loss", "bad news", "heartbroken", "disappointed", "hopeless"
    ]),
    "fear": frozenset([
        "scared", "afraid", "fear", "terrified", "worried", "anxious", "nervous", 
        "panic", "danger", "threat", "risk", "unsafe", "creepy"
    ]),
    "surprise": frozenset([
        "wow", "omg", "shocked", "surprised", "unexpected", "crazy", "unbelievable", 
        "whoa", "can't believe", "suddenly"
    ]),
    "disgust": frozenset([
        "gross", "nasty", "sick", "vomit", "puke", "repulsive", "revolting", "yuck", "eww"
    ])
}

def detect_emotion_regex(text: str) -> str:
    """Detect dominant emotion using keyword matching."""
    text_lower = text.lower()
    scores = {emo: 0 for emo in EMOTION_KEYWORDS}
    
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        for emo, keywords in EMOTION_KEYWORDS.items():
            if word in keywords:
                scores[emo] += 1
    
    # Find max score
    best_emo = "neutral"
    max_score = 0
    
    for emo, score in scores.items():
        if score > max_score:
            max_score = score
            best_emo = emo
            
    return best_emo

def analyze_sentiment_regex(text: str) -> Dict[str, Any]:
    """
    Rule-based sentiment analysis using word lists.
    Returns sentiment score (-1.0 to 1.0) and label.
    """
    text_lower = text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    positive_count = 0
    negative_count = 0
    has_negator = False
    has_intensifier = False
    
    # Check for negators and intensifiers
    for word in words:
        if word in NEGATORS:
            has_negator = True
        if word in INTENSIFIERS:
            has_intensifier = True
        if word in POSITIVE_WORDS:
            positive_count += 1
        if word in NEGATIVE_WORDS:
            negative_count += 1
    
    # Check for phrase-level negative patterns
    if re.search(r"\b(doesn't|does\s+not|not)\s+(work|good|great|help)\b", text_lower):
        negative_count += 2
    
    # Calculate base score
    total = positive_count + negative_count
    if total == 0:
        score = 0.0
    else:
        score = (positive_count - negative_count) / max(total, 1)
    
    # Apply negator flipping (reduces magnitude)
    if has_negator and score != 0:
        score = score * -0.5
    
    # Apply intensifier boost
    if has_intensifier:
        score = min(1.0, max(-1.0, score * 1.5))
    
    # Clamp to [-1, 1]
    score = max(-1.0, min(1.0, score))
    
    # Determine label
    if score > 0.2:
        label = "positive"
    elif score < -0.2:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "sentiment_score": round(score, 2),
        "sentiment_label": label,
        "positive_words": positive_count,
        "negative_words": negative_count,
        "confidence": 0.6 if total > 0 else 0.3,  # Lower confidence for fallback
    }


def detect_intent_regex(text: str) -> str:
    """
    Detect user intent using regex patterns.
    Returns one of: HOT_LEAD, CHURN_RISK, BUG_REPORT, FEATURE_REQUEST, PRAISE, GENERAL
    """
    # Check in priority order (most actionable first)
    for pattern in CHURN_RISK_PATTERNS:
        if pattern.search(text):
            return "CHURN_RISK"
    
    for pattern in HOT_LEAD_PATTERNS:
        if pattern.search(text):
            return "HOT_LEAD"
    
    for pattern in BUG_REPORT_PATTERNS:
        if pattern.search(text):
            return "BUG_REPORT"
    
    for pattern in FEATURE_REQUEST_PATTERNS:
        if pattern.search(text):
            return "FEATURE_REQUEST"
    
    for pattern in PRAISE_PATTERNS:
        if pattern.search(text):
            return "PRAISE"
    
    return "GENERAL"


def extract_entities_regex(text: str) -> Dict[str, List[str]]:
    """
    Extract basic entities using regex patterns.
    Returns dict with people, companies, products lists.
    """
    entities = {
        "people": [],
        "companies": [],
        "products": [],
    }
    
    # Extract companies
    for pattern in COMPANY_PATTERNS:
        matches = pattern.findall(text)
        entities["companies"].extend([m for m in matches if m not in entities["companies"]])
    
    # Limit to prevent noise
    entities["companies"] = entities["companies"][:10]
    
    return entities


def detect_topics_regex(text: str) -> List[str]:
    """
    Extract topics based on keyword patterns.
    """
    topics = []
    text_lower = text.lower()
    
    topic_keywords = {
        "pricing": ["price", "pricing", "cost", "expensive", "cheap", "discount", "deal"],
        "customer_support": ["support", "help", "response", "wait", "ticket", "agent"],
        "bugs": ["bug", "error", "crash", "broken", "glitch", "issue"],
        "features": ["feature", "add", "missing", "wish", "need", "roadmap"],
        "performance": ["slow", "fast", "speed", "lag", "performance", "loading"],
        "ui_ux": ["ui", "ux", "design", "interface", "usability", "confusing"],
        "onboarding": ["onboarding", "setup", "getting started", "tutorial", "documentation"],
        "integration": ["integration", "api", "connect", "sync", "plugin"],
        "mobile": ["mobile", "app", "ios", "android", "phone"],
        "security": ["security", "privacy", "safe", "secure", "data", "breach"],
    }
    
    for topic, keywords in topic_keywords.items():
        if any(kw in text_lower for kw in keywords):
            topics.append(topic)
    
    return topics[:5]  # Limit to 5 topics


def calculate_lead_score_regex(text: str) -> int:
    """
    Calculate a lead score (0-100) based on purchase intent signals.
    """
    score = 0
    text_lower = text.lower()
    
    # High intent signals (+30 each)
    high_intent = [
        r"\b(want\s+to\s+buy|ready\s+to\s+buy|want\s+to\s+purchase)\b",
        r"\b(pricing|how\s+much|cost)\b",
        r"\b(demo|trial|sign\s*up)\b",
        r"\btake\s+my\s+money\b",
    ]
    
    # Medium intent signals (+15 each)
    medium_intent = [
        r"\b(considering|thinking\s+about|looking\s+at)\b",
        r"\b(recommend|recommendation|review)\b",
        r"\b(alternative|vs|versus|compare)\b",
    ]
    
    # Low intent signals (+5 each)
    low_intent = [
        r"\b(interesting|curious|heard\s+about)\b",
        r"\b(what\s+is|how\s+does)\b",
    ]
    
    for pattern in high_intent:
        if re.search(pattern, text_lower):
            score += 30
    
    for pattern in medium_intent:
        if re.search(pattern, text_lower):
            score += 15
    
    for pattern in low_intent:
        if re.search(pattern, text_lower):
            score += 5
    
    # Negative signals (reduce score)
    negative_signals = [
        r"\b(hate|terrible|worst|scam)\b",
        r"\b(cancel|unsubscribe|refund)\b",
    ]
    
    for pattern in negative_signals:
        if re.search(pattern, text_lower):
            score -= 20
    
    return max(0, min(100, score))


def analyze_enhanced_fallback(texts: List[str]) -> Dict[str, Any]:
    """
    Complete fallback for analyze_enhanced when LLM fails.
    Provides sentiment, emotions, topics, entities, and business fields.
    """
    combined_text = " ".join(texts)
    
    # Get sentiment
    sentiment_result = analyze_sentiment_regex(combined_text)
    
    # Get intent for lead/urgency signals
    intent = detect_intent_regex(combined_text)
    
    # Map intent to urgency
    urgency_map = {
        "CHURN_RISK": "high",
        "HOT_LEAD": "high",
        "BUG_REPORT": "medium",
        "FEATURE_REQUEST": "low",
        "PRAISE": "low",
        "GENERAL": "low",
    }
    
    
    # Get sentiment score
    sentiment_score = sentiment_result["sentiment_score"]

    # Emotion Keywords
    EMOTION_KEYWORDS = {
        "joy": ["happy", "love", "great", "excited", "amazing", "wonderful", "delighted", "glad"],
        "anger": ["hate", "angry", "furious", "mad", "annoying", "frustrated", "terrible", "worst"],
        "fear": ["scared", "afraid", "worried", "nervous", "anxious", "risk", "security", "breach", "unsafe"],
        "sadness": ["sad", "unhappy", "disappointed", "sorry", "miss", "regret", "depressing"],
        "surprise": ["wow", "omg", "shocked", "surprised", "unexpected", "unbelievable", "suddenly"],
        "disgust": ["disgusting", "gross", "yuck", "vile", "revolting", "trash", "garbage"]
    }

    # Calculate emotions based on keywords + sentiment
    emotions = {k: 0.0 for k in EMOTION_KEYWORDS}
    text_lower = combined_text.lower()
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            # Base score from keyword presence (capped at 0.8)
            emotions[emotion] = min(0.8, count * 0.3)
    
    # Boost based on sentiment alignment
    if sentiment_score > 0.5:
        emotions["joy"] = max(emotions["joy"], sentiment_score)
    elif sentiment_score < -0.5:
        emotions["anger"] = max(emotions["anger"], abs(sentiment_score) * 0.8)
        emotions["disgust"] = max(emotions["disgust"], abs(sentiment_score) * 0.5)
        
    # Ensure at least one emotion has a score if sentiment is strong
    if sentiment_score > 0.3 and emotions["joy"] == 0:
        emotions["joy"] = 0.5
    if sentiment_score < -0.3 and all(v == 0 for v in emotions.values()):
        emotions["frustration"] = 0.5 # Default negative emotion replacement for anger/sadness mismatch
    
    # Extract topics and entities
    topics = detect_topics_regex(combined_text)
    entities = extract_entities_regex(combined_text)
    
    # Business intelligence
    lead_score = calculate_lead_score_regex(combined_text)
    
    # Extract pain points (negative context)
    pain_points = []
    if sentiment_result["negative_words"] > 0:
        for word in ["slow", "broken", "expensive", "confusing", "buggy"]:
            if word in combined_text.lower():
                pain_points.append(word)
    
    # If no specific pain points but sentiment is negative, add generic
    if not pain_points and sentiment_score < -0.2:
         pain_points.append("General dissatisfaction detected")

    # Feature requests
    feature_requests = []
    if intent == "FEATURE_REQUEST":
        feature_requests = topics[:2]  # Use detected topics as proxy
    
    # If no feature requests but "wish" or "hope" is present
    if not feature_requests and ("wish" in combined_text.lower() or "hope" in combined_text.lower()):
         feature_requests.append("Unspecified improvement")

    # Churn risks
    churn_risks = []
    if intent == "CHURN_RISK":
        churn_risks = ["User showing exit signals"]
    elif sentiment_score < -0.6:
         churn_risks.append("High negative sentiment risk")

    # Recommended actions (Defaults based on sentiment/intent)
    recommended_actions = []
    if intent == "HOT_LEAD":
         recommended_actions.append("Engage with personalized sales outreach")
    elif intent == "CHURN_RISK":
         recommended_actions.append("Prioritize retention support")
    elif intent == "BUG_REPORT":
         recommended_actions.append("Log issue and acknowledge user")
    
    # Add general actions if empty
    if not recommended_actions:
         if sentiment_score < -0.2:
             recommended_actions.append("Monitor sentiment and address complaints")
         elif sentiment_score > 0.2:
             recommended_actions.append("Amplify positive feedback")
         else:
             recommended_actions.append("Continue monitoring brand conversations")

    return {
        "sentiment_score": sentiment_result["sentiment_score"],
        "sentiment_label": sentiment_result["sentiment_label"],
        "emotions": emotions,
        "is_sarcastic": False,  # Can't detect sarcasm without LLM
        "urgency": urgency_map.get(intent, "low"),
        "topics": topics,
        "language": "en",  # Default, can't detect without LLM
        "entities": entities,
        # Business fields
        "feature_requests": feature_requests,
        "pain_points": pain_points,
        "churn_risks": churn_risks,
        "recommended_actions": recommended_actions,
        "lead_score": lead_score,
        # Metadata
        "_fallback": True,
        "_confidence": 0.5,
    }


def analyze_commercial_intent_fallback(text: str) -> Dict[str, Any]:
    """
    Fallback for commercial intent analysis.
    """
    intent = detect_intent_regex(text)
    lead_score = calculate_lead_score_regex(text)
    sentiment = analyze_sentiment_regex(text)
    
    is_sales_intent = intent == "HOT_LEAD" or lead_score > 30
    
    # Detect pain points
    pain_point = None
    if "expensive" in text.lower() or "cost" in text.lower():
        pain_point = "pricing"
    elif "slow" in text.lower():
        pain_point = "performance"
    elif "support" in text.lower():
        pain_point = "customer_support"
    
    return {
        "sales_intent": is_sales_intent,
        "confidence": lead_score / 100.0,
        "intent_type": "purchase" if is_sales_intent else "research",
        "pain_point": pain_point,
        "_fallback": True,
    }


def analyze_strategic_fallback(text: str, brand: str, is_competitor: bool) -> Dict[str, Any]:
    """
    Fallback for strategic analysis.
    """
    sentiment = analyze_sentiment_regex(text)
    intent = detect_intent_regex(text)
    
    # Determine strategic tag
    strategic_tag = "NONE"
    if is_competitor and sentiment["sentiment_score"] < -0.3:
        strategic_tag = "OPPORTUNITY_TO_STEAL"
    elif not is_competitor and intent == "CHURN_RISK" and sentiment["sentiment_score"] < -0.5:
        strategic_tag = "CRITICAL_ALERT"
    
    return {
        "relevant": True,
        "intent": intent,
        "strategic_tag": strategic_tag,
        "sentiment_score": sentiment["sentiment_score"],
        "summary": f"[Fallback] {intent} detected with {sentiment['sentiment_label']} sentiment",
        "confidence": 0.5,
        "_fallback": True,
    }


def categorize_complaint_fallback(text: str) -> Dict[str, Any]:
    """
    Fallback for competitor complaint categorization.
    Uses regex patterns to detect complaint category.
    """
    text_lower = text.lower()
    
    # Category patterns
    category_patterns = {
        "pricing": [r"\b(expensive|overpriced|cost|price|fee|charge|billing)\b"],
        "performance": [r"\b(slow|crash|bug|error|glitch|lag|freeze|loading)\b"],
        "support_issues": [r"\b(support|help|response|wait|ticket|customer\s+service)\b"],
        "missing_features": [r"\b(feature|missing|need|want|wish|add|integration)\b"],
        "usability": [r"\b(confusing|hard\s+to|difficult|ui|ux|interface|complicated)\b"],
        "reliability": [r"\b(unreliable|down|outage|data\s+loss|inconsistent)\b"],
    }
    
    detected_category = "other"
    for category, patterns in category_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                detected_category = category
                break
        if detected_category != "other":
            break
    
    # Estimate pain level from negative words
    pain_level = 5  # Default
    strong_negative = ["hate", "terrible", "worst", "awful", "horrible", "useless", "scam"]
    moderate_negative = ["bad", "annoying", "frustrating", "disappointed"]
    
    for word in strong_negative:
        if word in text_lower:
            pain_level = 8
            break
    
    if pain_level == 5:
        for word in moderate_negative:
            if word in text_lower:
                pain_level = 6
                break
    
    # Extract specific issue (first sentence or first 100 chars)
    sentences = text.split(".")
    specific_issue = sentences[0].strip()[:100] if sentences else text[:100]
    
    return {
        "category": detected_category,
        "specific_issue": specific_issue,
        "pain_level": pain_level,
        "_fallback": True,
    }
