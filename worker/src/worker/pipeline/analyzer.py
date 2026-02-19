"""Pipeline component for analyzing mentions (Regex + LLM)."""
import logging
import time
from typing import List, Dict, Tuple

from ..logger import get_logger
from ..domain_types import Chunk, Mention, Intent, StrategicTag
from ..analyzer import get_analyzer, AnalysisResult, AnalysisInput
from ..llm_adapter import InstrumentedLLMAdapter
from .. import fallback_analysis

logger = get_logger(__name__)

class PipelineAnalyzer:
    """Orchestrates the analysis of mentions using Regex and LLM."""

    def __init__(
        self, 
        worker_id: str, 
        llm_adapter: InstrumentedLLMAdapter,
        storage = None,
        regex_analyzer = None
    ):
        self._worker_id = worker_id
        self._llm_adapter = llm_adapter
        self._storage = storage
        self._regex_analyzer = regex_analyzer or get_analyzer(worker_id)

    async def analyze_mentions(
        self, 
        chunk: Chunk, 
        mentions: List[Mention], 
        keywords: List[str], 
        envelope: dict = None
    ) -> Tuple[List[Mention], Dict[str, AnalysisResult]]:
        """
        Run 3-Tier Analysis:
        1. Pre-filter (Keyword check)
        2. Fast Analysis (Regex) -> Incremental Push
        3. Deep Analysis (LLM) -> Tags -> Money Mode -> Market Gap
        """
        valid_mentions: List[Mention] = []
        analysis_map: Dict[str, AnalysisResult] = {}
        filtered_count = 0
        
        # Establish LLM Context for this brand/chunk if not already set by caller?
        # We'll assume the caller sets context or we do it here. 
        # Safer to do it here if we want to isolate.
        with self._llm_adapter.context(brand=chunk.brand, chunk_id=chunk.chunk_id):
        
            for i, mention in enumerate(mentions):
                # Metadata extraction
                meta = mention.metadata or {}
                real_platform = meta.get("platform") or meta.get("source") or mention.source
                if real_platform == "aggregator" and meta.get("raw", {}).get("platform"):
                     real_platform = meta.get("raw", {}).get("platform")
                
                # Check for Competitor Context
                is_competitor = bool(meta.get("isCompetitor", False))
                competitor_name = meta.get("competitorName")
                competitor_id = meta.get("competitorId")
                
                target_brand_name = competitor_name if is_competitor and competitor_name else chunk.brand
                
                input_data = AnalysisInput(
                    text=mention.text,
                    target_brand=target_brand_name,
                    target_keywords=keywords, # Ideally we pass competitor keywords here too if available
                    is_competitor=is_competitor, 
                    source_platform=real_platform,
                    source_url=meta.get("url") or meta.get("permalink")
                )
                
                # --- PRE-FILTER ---
                text_lower = mention.text.lower()
                
                matched_target = False
                
                if is_competitor and competitor_name:
                    # For competitors, we check if the text mentions the COMPETITOR
                    comp_lower = competitor_name.lower()
                    if comp_lower in text_lower:
                        matched_target = True
                else:
                    # Normal brand check
                    brand_lower = chunk.brand.lower().replace("-", " ").replace("_", " ")
                    if keywords:
                        matched_target = any(kw in text_lower for kw in keywords)
                    else:
                        matched_target = brand_lower in text_lower
                        if not matched_target:
                             brand_vars = [brand_lower, brand_lower.replace(" ", ""), brand_lower.replace(" ", "-")]
                             matched_target = any(var in text_lower for var in brand_vars)
                
                if not matched_target:
                    filtered_count += 1
                    continue
                
                try:
                    # --- FAST ANALYSIS ---
                    fast_sent = fallback_analysis.analyze_sentiment_regex(mention.text)
                    fast_emo = fallback_analysis.detect_emotion_regex(mention.text)
                    
                    # --- INCREMENTAL PUSH (FAST) ---
                    if self._storage and envelope:
                            mention_dict = mention.model_dump(mode='json') 
                            mention_dict["sentiment_score"] = fast_sent["sentiment_score"]
                            mention_dict["sentiment"] = fast_sent["sentiment_label"]
                            mention_dict["intent"] = "GENERAL"
                            mention_dict["strategic_tag"] = "NONE"
                            
                            if real_platform and real_platform != "aggregator":
                                mention_dict["source"] = real_platform
                            
                            if not mention_dict.get("metadata"):
                                mention_dict["metadata"] = {}
                            mention_dict["metadata"]["emotion"] = fast_emo
                            
                            # Ensure competitor metadata is preserved in the push
                            if is_competitor:
                                mention_dict["metadata"]["isCompetitor"] = True
                                mention_dict["metadata"]["competitorId"] = competitor_id
                                mention_dict["metadata"]["competitorName"] = competitor_name
                            
                            await self._storage.push_mention_stats(chunk.brand, [mention_dict])

                    # --- DEEP ANALYSIS (LLM) ---
                    result = await self._regex_analyzer.analyze(input_data)
                    
                    if result.relevant:
                        # V4 Features: Money Mode & Market Gap
                        should_check_commercial = (
                            result.gatekeeper_category in ["purchase_intent", "lead_switching"] or 
                            result.intent in [Intent.HOT_LEAD, Intent.CHURN_RISK] 
                        )
                        
                        if should_check_commercial:
                             try:
                                 comm_intent = await self._llm_adapter.analyze_commercial_intent(mention.text)
                                 if comm_intent["sales_intent"]:
                                     result.intent = Intent.HOT_LEAD
                                     if not result.strategic_tag or result.strategic_tag == StrategicTag.NONE:
                                         result.strategic_tag = StrategicTag.OPPORTUNITY_TO_STEAL
                                     
                                     pain_point = comm_intent.get("pain_point")
                                     if pain_point:
                                          if len(result.keywords) < 5: 
                                              result.keywords.append(f"Pain: {pain_point}")
                             except Exception:
                                 pass

                        if result.sentiment_score < -0.4:
                            try:
                               comp = await self._llm_adapter.categorize_competitor_complaint(mention.text, chunk.brand)
                               if comp["category"] != "other":
                                   mention.metadata["complaint_category"] = comp["category"]
                                   mention.metadata["complaint_pain_level"] = comp["pain_level"]
                            except Exception:
                               pass

                        # --- INCREMENTAL PUSH (FINAL) ---
                        if self._storage and envelope:
                             mention_dict = mention.model_dump(mode='json')
                             mention_dict["sentiment_score"] = result.sentiment_score
                             mention_dict["sentiment"] = result.sentiment_label
                             mention_dict["intent"] = result.intent.value if result.intent else "GENERAL"
                             mention_dict["strategic_tag"] = result.strategic_tag.value if result.strategic_tag else "NONE"
                             mention_dict["is_verified"] = result.is_verified
                             mention_dict["verification_score"] = result.verification_score
                             mention_dict["verification_reason"] = result.verification_reason
                             
                             if is_competitor:
                                mention_dict["metadata"]["isCompetitor"] = True
                                mention_dict["metadata"]["competitorId"] = competitor_id
                                mention_dict["metadata"]["competitorName"] = competitor_name

                             await self._storage.push_mention_stats(chunk.brand, [mention_dict])

                        valid_mentions.append(mention)
                        analysis_map[mention.text] = result
                        
                        if result.gatekeeper_category == "product_launch":
                            logger.info(f"Launch detected for {chunk.brand}: {result.summary}")
                            
                except Exception as e:
                    logger.error(f"Analysis failed for mention: {e}")
                    continue
        
        if filtered_count > 0:
            logger.info(f"Pre-filter: {filtered_count}/{len(mentions)} mentions skipped")
            
        return valid_mentions, analysis_map
