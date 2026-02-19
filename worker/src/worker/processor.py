"""Processing pipeline coordinating preprocessing, embeddings, clustering, LLM, and spike detection."""
from __future__ import annotations

import logging
import re
import json
import time
from datetime import datetime, timezone
import os
import requests

import numpy as np

from .config import get_settings
from .embeddings import InstrumentedEmbeddingAdapter, get_embedding_adapter
from .clustering import Clusterer, ClusteringOutput
from .llm_adapter import InstrumentedLLMAdapter, get_llm_adapter

from .analyzer import get_analyzer, AnalysisResult, AnalysisInput, Intent, StrategicTag
from .logger import get_logger, log_with_context
from .metrics import (
    worker_preprocessing_time_seconds,
)
from .spike_detector import SpikeDetector
from .domain_types import Chunk, ChunkMetrics, ChunkResult, ClusterResult, Mention, Emotions, EnhancedAnalysis
from .health_score import HealthScoreCalculator
from .web_scanner import get_web_scanner
from .crisis_detector import CrisisDetector

# Pipeline Components
from .pipeline.preprocessor import PipelinePreprocessor
from .pipeline.analyzer import PipelineAnalyzer
from .pipeline.publisher import ResultPublisher

logger = get_logger(__name__)


CLEAN_URL_RE = re.compile(r"https?://\S+")
CLEAN_WHITESPACE_RE = re.compile(r"\s+")


class ChunkProcessor:
    """Main processing pipeline for a chunk of mentions."""

    def __init__(
        self,
        worker_id: str,
        redis_client,
        # Dependencies injected from Composition Root
        storage=None,
        embedding_adapter: InstrumentedEmbeddingAdapter = None,
        llm_adapter: InstrumentedLLMAdapter = None,
        analyzer=None,
        clusterer: Clusterer = None,
        spike_detector: SpikeDetector = None,
        health_score_calculator: HealthScoreCalculator = None,
        web_scanner=None,
        crisis_detector: CrisisDetector = None,
    ) -> None:
        self._settings = get_settings()
        self._worker_id = worker_id
        self._redis_client = redis_client
        self._storage = storage

        # Default to factory method if not provided (Backwards Compatibility / Default wiring)
        self._embedding_adapter = embedding_adapter or get_embedding_adapter(worker_id)
        self._llm_adapter = llm_adapter or get_llm_adapter(worker_id)
        self._clusterer = clusterer or Clusterer(worker_id)
        
        if spike_detector:
            self._spike_detector = spike_detector
        else:
            from .services.brand_service import BrandService
            brand_service = BrandService(redis_client)
            self._spike_detector = SpikeDetector(brand_service, worker_id)

        self._analyzer = analyzer or get_analyzer(worker_id)
        self._health_score_calculator = health_score_calculator or HealthScoreCalculator(redis_client, worker_id)
        self._web_scanner = web_scanner or get_web_scanner(worker_id)
        self._crisis_detector = crisis_detector or CrisisDetector(redis_client, worker_id)

    async def _publish_event(self, brand: str, event_data: dict) -> None:
        """Publish event to Redis for WebSocket broadcasting."""
        import json
        try:
            channel = f"events:brand:{brand}"
            await self._redis_client.publish(channel, json.dumps(event_data))
            logger.info(f"[WS] Published event to {channel}")
        except Exception as e:
            logger.error(f"[WS] Failed to publish event: {e}")

    async def process_chunk(self, chunk: Chunk, *, fetch_time_ms: float, envelope: dict = None) -> ChunkResult:
        metrics = ChunkMetrics(io_time_ms=fetch_time_ms)
        total_start = time.perf_counter()
        
        # 1. Preprocess
        # ---------------------------------------------------------------------
        # Extract regex cleaning and deduplication
        preprocessor = PipelinePreprocessor(self._worker_id)
        valid_mentions = preprocessor.preprocess(chunk, metrics)
        
        # Establish LLM Context
        with self._llm_adapter.context(brand=chunk.brand, chunk_id=chunk.chunk_id):
            
            # 2. Analyze (Regex -> AI)
            # -----------------------------------------------------------------
            # Determine keywords from context/envelope
            keywords = []
            if envelope:
                 keywords = envelope.get("keywords", []) or []
                 if envelope.get("brand_name"):
                     keywords.append(envelope.get("brand_name").lower())
                 keywords.append(chunk.brand.lower())
                 keywords = list(set(k.lower() for k in keywords if k))

            # Run Analysis Loop
            pipeline_analyzer = PipelineAnalyzer(self._worker_id, self._llm_adapter, self._storage, self._analyzer)
            
            # Note: valid_mentions here is actually "preprocessed mentions", not yet filtered for relevance by analyzer
            # But Analyzer logic includes pre-filtering.
            processed_mentions, analysis_map = await pipeline_analyzer.analyze_mentions(
                chunk, valid_mentions, keywords, envelope
            )
            
            # Update valid_mentions to only those deemed relevant by Analyzer
            valid_mentions = processed_mentions
            
            logger.info(f"Analysis complete: {len(valid_mentions)} mentions relevant")

            if not valid_mentions:
                 processing_ms = (time.perf_counter() - total_start) * 1000
                 metrics.total_task_time_ms = processing_ms + metrics.io_time_ms
                 return ChunkResult(
                     chunk_id=chunk.chunk_id,
                     brand=chunk.brand,
                     timestamp=int(chunk.created_at.timestamp()),
                     clusters=[],
                     metrics=metrics,
                 )

            # 3. Embeddings
            # -----------------------------------------------------------------
            embeddings, embed_duration = await self._generate_embeddings(chunk, valid_mentions)
            metrics.embedding_time_ms = embed_duration

            # 4. Clustering
            # -----------------------------------------------------------------
            clustering_output = await self._perform_clustering(chunk, embeddings)
            metrics.clustering_time_ms = clustering_output.duration_ms

            # 5. Cluster Analysis
            # -----------------------------------------------------------------
            clusters = await self._analyze_clusters(chunk, valid_mentions, clustering_output, metrics, analysis_map)
            
            processing_ms = (time.perf_counter() - total_start) * 1000
            metrics.total_task_time_ms = processing_ms + metrics.io_time_ms
            
            # 6. Aggregation & Formatting
            # -----------------------------------------------------------------
            agg_summary = clusters[0].summary if clusters and clusters[0].summary else ""
            agg_topics = set()
            # Use dict-based deduplication to handle both string and dict entities
            agg_entities = {"people": {}, "companies": {}, "products": {}}
            agg_actions = []
            agg_feature_requests = {}
            agg_pain_points = {}
            agg_churn_risks = {}
            agg_rec_actions = {}
            any_spike = False

            def get_item_key(item):
                """Get a hashable key from item (string or dict)."""
                if isinstance(item, str):
                    return item
                elif isinstance(item, dict):
                    return item.get("name") or item.get("text") or str(item)
                return str(item)

            for c in clusters:
                agg_topics.update(c.topics)
                if c.spike:
                    any_spike = True
                
                if c.enhanced_analysis:
                    ents = c.enhanced_analysis.entities or {}
                    for key in ["people", "companies", "products"]:
                        for item in ents.get(key, []):
                            item_key = get_item_key(item)
                            if item_key not in agg_entities[key]:
                                agg_entities[key][item_key] = item
                    
                    for item in (c.enhanced_analysis.feature_requests or []):
                        item_key = get_item_key(item)
                        if item_key not in agg_feature_requests:
                            agg_feature_requests[item_key] = item
                    for item in (c.enhanced_analysis.pain_points or []):
                        item_key = get_item_key(item)
                        if item_key not in agg_pain_points:
                            agg_pain_points[item_key] = item
                    for item in (c.enhanced_analysis.churn_risks or []):
                        item_key = get_item_key(item)
                        if item_key not in agg_churn_risks:
                            agg_churn_risks[item_key] = item
                    for item in (c.enhanced_analysis.recommended_actions or []):
                        item_key = get_item_key(item)
                        if item_key not in agg_rec_actions:
                            agg_rec_actions[item_key] = item
                        agg_actions.append(item)

            final_entities = {k: list(v.values()) for k, v in agg_entities.items()}
            final_action = agg_actions[0] if agg_actions else None

            result = ChunkResult(
                chunk_id=chunk.chunk_id,
                brand=chunk.brand,
                timestamp=int(chunk.created_at.timestamp()),
                clusters=clusters,
                metrics=metrics,
                summary=agg_summary,
                topics=list(agg_topics)[:10],
                spikeDetected=any_spike,
                entities=final_entities,
                action_suggested=final_action,
                feature_requests=list(agg_feature_requests.values())[:10],
                pain_points=list(agg_pain_points.values())[:10],
                churn_risks=list(agg_churn_risks.values())[:10],
                recommended_actions=list(agg_rec_actions.values())[:10]
            )
            
            # 7. Publishing & Events
            # -----------------------------------------------------------------
            publisher = ResultPublisher(self._worker_id, self._redis_client, self._storage)
            
            # A. Publish Results
            await publisher.persist_results(chunk, result, envelope)

            # NEW: Publish analyzed mentions (with intent/sentiment) to timeline
            # This overwrites the raw mentions from QueueWorker with enriched data for Money Feed
            await publisher.publish_mention_stats(chunk.brand, [m.model_dump(mode='json') for m in valid_mentions])
            
            # B. Dashboard Event
            await publisher.publish_metrics(chunk.brand, chunk.chunk_id, len(clusters), len(valid_mentions))
            
            # C. Spike Timeline
            if any_spike and self._storage:
                spike_event = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "spikeScore": 1.0, 
                    "mentionCount": len(valid_mentions),
                    "clusters": [{"id": c.cluster_id, "label": c.summary or ""} for c in clusters if c.spike]
                }
                await self._storage.push_spike_timeline(chunk.brand, spike_event)

            # D. Health Score & Brand Summary
            enhanced_results = [cluster.enhanced_analysis for cluster in clusters if cluster.enhanced_analysis]
            health_score = await self._health_score_calculator.calculate(chunk.brand, enhanced_results)
            await publisher.update_brand_summary(chunk.brand, result, health_score)

            # E. Leads (Money Feed)
            # Filter leads from analysis_map
            leads = []
            for m in valid_mentions:
                 res = analysis_map.get(m.text)
                 if res:
                     should_push = (res.intent in [Intent.HOT_LEAD, Intent.CHURN_RISK] 
                                    or res.strategic_tag in [StrategicTag.OPPORTUNITY_TO_STEAL, StrategicTag.CRITICAL_ALERT])
                     if should_push:
                         m_data = m.model_dump(mode='json') 
                         m_data["intent"] = res.intent.value
                         m_data["strategic_tag"] = res.strategic_tag.value
                         m_data["confidence"] = res.verification_score if res.verification_score > 0 else 0.8
                         leads.append(m_data)
            
            await publisher.publish_leads(chunk.brand, leads)

            # F. Crisis Detection
            try:
                 all_analyses = [c.enhanced_analysis for c in clusters if c.enhanced_analysis]
                 all_texts = [m.text for m in valid_mentions]
                 crisis_result = await self._crisis_detector.check_for_crisis(chunk.brand, all_analyses, mention_texts=all_texts)
                 
                 if crisis_result["is_crisis"]:
                     event = {
                         "timestamp": datetime.now(timezone.utc).isoformat(),
                         "severity": crisis_result["severity"],
                         "reasons": crisis_result["reasons"],
                         "recommended_action": crisis_result["recommended_action"],
                         "metrics": crisis_result["metrics"]
                     }
                     await publisher.publish_crisis(
                         chunk.brand, 
                         event, 
                         {
                             "riskScore": int(crisis_result["metrics"].get("negative_ratio", 0) * 100),
                             "severity": crisis_result["severity"],
                             "mentionCount": crisis_result["metrics"].get("mention_count", 0),
                             "reasons": crisis_result["reasons"]
                         }
                     )
            except Exception as e:
                logger.error(f"Crisis detection failed: {e}")

            # G. The Oracle (Launch Detection)
            # Check for launch
            # ... (Keep existing logic or use Analyzer?)
            # The Analyzer had launch detection logic, but `process_chunk` had the loop.
            # `PipelineAnalyzer` does NOT do the Oracle loop currently (it does gatekeeper check but not the specific launch logic).
            # I should move Oracle logic to Analyzer or keep it here.
            # For now, keep it here to match existing behavior or simplified.
            
            # 6.5 THE ORACLE: Launch Detection
            # Check if any mentions contain launch patterns (supports both brand and competitor launches)
            try:
                # Check if this is a competitor chunk from envelope metadata
                is_competitor_chunk = envelope and envelope.get("competitor_id")
                competitor_name = envelope.get("competitor_name") if envelope else None
                competitor_id = envelope.get("competitor_id") if envelope else None
                
                for mention in valid_mentions:
                    if self._analyzer.is_launch_candidate(mention.text):
                        # Determine target brand: competitor name if competitor chunk, else brand
                        target_brand = competitor_name if is_competitor_chunk else chunk.brand
                        
                        # Analyze for launch prediction
                        launch_input = AnalysisInput(
                            text=mention.text,
                            target_brand=target_brand,
                            target_keywords=keywords if keywords else [],
                            is_competitor=bool(is_competitor_chunk),
                            source_platform=mention.source,
                            source_url=mention.url
                        )
                        prediction = await self._analyzer.detect_launch(launch_input)
                        
                        if prediction.is_launch:
                            # Store the prediction with proper competitor flag
                            is_competitor_launch = bool(is_competitor_chunk) or prediction.is_competitor
                            
                            prediction_data = {
                                "is_launch": True,
                                "product_name": prediction.product_name,
                                "success_score": prediction.success_score,
                                "reason": prediction.reason,
                                "brand": target_brand,
                                "is_competitor": is_competitor_launch,
                                "reception": {
                                    "hype_signals": prediction.reception.hype_signals,
                                    "skepticism_signals": prediction.reception.skepticism_signals,
                                    "overall": prediction.reception.overall
                                },
                                "detected_at": datetime.now(timezone.utc).isoformat()
                            }
                            
                            # Push to Redis: for competitor launches, write to competitor's OWN :my key
                            if is_competitor_launch and competitor_name:
                                # Write to competitor's launch key (API reads launch:brand:{slug}:my)
                                await self._storage.push_launch_prediction(
                                    competitor_name.lower().replace(" ", "-"),  # slug format
                                    prediction_data, 
                                    is_competitor=False  # Use :my suffix so API can read it
                                )
                                logger.info(f"Oracle: COMPETITOR launch detected - {competitor_name}: {prediction.product_name} (Score: {prediction.success_score})")
                            else:
                                # Normal brand launch
                                await self._storage.push_launch_prediction(
                                    chunk.brand, 
                                    prediction_data, 
                                    is_competitor=False
                                )
                                logger.info(f"Oracle: Brand launch detected - {chunk.brand}: {prediction.product_name} (Score: {prediction.success_score})")
                            break  # Only detect one launch per chunk
            except Exception as e:
                logger.warning(f"Oracle launch detection failed: {e}")

            # 6. Persistence (MongoDB & Redis)
            if self._storage and envelope:
                # MongoDB
                await self._storage.save_result(envelope, result.model_dump())

                # Dashboard Charts (Market Share, Sentiment)
                # Prepare mentions for Chart Stats logic (Market Share, Sentiment)
                # Note: We ALREADY pushed to optimized_mentions incrementally above.
                # However, push_mention_stats also updates aggregated stats keys?
                # push_mention_stats implementation: lpush to optimized_mentions, and zadd to influencers.
                # It does NOT aggregate counters locally. It's just Redis commands.
                # So calling it incrementally is safe and sufficient.
                # We skip the batch push here to avoid duplication.
                
                # Re-create stats_mentions for Money Feed usage (High Intent Leads)
                stats_mentions = []
                for m in valid_mentions:
                    m_data = m.model_dump()
                    if m.text in analysis_map:
                        res = analysis_map[m.text]
                        m_data["sentiment_score"] = res.sentiment_score
                        m_data["sentiment"] = res.sentiment_label
                        m_data["intent"] = res.intent.value if res.intent else "GENERAL"
                        m_data["strategic_tag"] = res.strategic_tag.value if res.strategic_tag else "NONE"
                    else:
                        m_data["intent"] = fallback_analysis.detect_intent_regex(m.text)
                        m_data["strategic_tag"] = "NONE"

                    # INJECT METADATA for Competitor Intelligence
                    if envelope and envelope.get("competitor_id"):
                         m_data["metadata"] = {
                             "isCompetitor": True,
                             "competitorId": envelope.get("competitor_id")
                         }
                    
                    stats_mentions.append(m_data)

                await self._storage.push_mention_stats(chunk.brand, stats_mentions)
                
                # Global Health Score
                enhanced_results = [cluster.enhanced_analysis for cluster in clusters if cluster.enhanced_analysis]
                health_score = await self._health_score_calculator.calculate(chunk.brand, enhanced_results)
                logger.info(f"Updated health score for {chunk.brand}: {health_score}")
                
                # Global Brand Summary (Sentiment Score, Topics, Health Score)
                await self._storage.update_brand_summary(chunk.brand, result, health_score=health_score)

            # NEW: Push High-Intent Leads (Money Feed)
            # Filter from stats_mentions where we already normalized the data
            leads = []
            for m in stats_mentions:
                intent = m.get("intent", "GENERAL")
                tag = m.get("strategic_tag", "NONE")
                
                # Definition of a Lead for Money Feed
                if intent in ["HOT_LEAD", "CHURN_RISK"] or tag in ["OPPORTUNITY_TO_STEAL", "CRITICAL_ALERT"]:
                    # Ensure format allows recreation of Lead object in API Gateway
                    # API Gateway expects: id, sourcePlatform, sourceText, leadScore, status, intentType
                    # Add confidence score from verification or analysis
                    confidence = m.get("verification_score", 0.0)
                    if confidence == 0.0:
                        # Fallback: derive from intent type
                        if intent == "HOT_LEAD" or tag == "OPPORTUNITY_TO_STEAL":
                            confidence = 0.85
                        elif intent == "CHURN_RISK" or tag == "CRITICAL_ALERT":
                            confidence = 0.80
                        else:
                            confidence = 0.65
                    m["confidence"] = confidence
                    leads.append(m)
            
            if leads:
                await self._storage.push_leads(chunk.brand, leads)
                
            # NEW: Crisis Detection (Crisis Monitor)
            # We need enhanced analysis results from clusters to check for crisis
            try:
                 # Flatten enhanced analysis from clusters
                 all_analyses = []
                 for c in clusters:
                     if c.enhanced_analysis:
                        # Weight it by count? CrisisDetector takes list of analyses.
                        # Ideally we pass each mention's analysis, but we only ran EA on clusters.
                        # We can pass the cluster EA multiple times or just unique EAs.
                        # Passing unique EAs is safer for "ratio" checks.
                        all_analyses.append(c.enhanced_analysis)
                 
                 # Also pass raw texts for keyword check
                 all_texts = [m.text for m in valid_mentions]
                 
                 crisis_result = await self._crisis_detector.check_for_crisis(
                     chunk.brand, 
                     all_analyses, 
                     mention_texts=all_texts
                 )
                 
                 if crisis_result["is_crisis"]:
                     # Push Event
                     event = {
                         "timestamp": datetime.now(timezone.utc).isoformat(),
                         "severity": crisis_result["severity"],
                         "reasons": crisis_result["reasons"],
                         "recommended_action": crisis_result["recommended_action"],
                         "metrics": crisis_result["metrics"]
                     }
                     await self._storage.push_crisis_event(chunk.brand, event)
                     
                     # Update Current Metrics
                     await self._storage.update_crisis_metrics(chunk.brand, {
                         "riskScore": int(crisis_result["metrics"].get("negative_ratio", 0) * 100), # Simple proxy
                         "severity": crisis_result["severity"],
                         "velocityMultiplier": 1.0, # TODO: Calculate velocity
                         "sentimentIntensity": abs(crisis_result["metrics"].get("avg_sentiment", 0)),
                         "mentionCount": crisis_result["metrics"].get("mention_count", 0),
                         "reasons": crisis_result["reasons"]
                     })
                     
                     logger.warning(f"CRISIS DETECTED for {chunk.brand}: {crisis_result['severity']}")
            except Exception as e:
                logger.error(f"Crisis detection failed: {e}")

        log_with_context(
            logger,
            level=logging.INFO,
            message="Chunk processed",
            context={
                "worker_id": self._worker_id,
                "brand": chunk.brand,
                "chunk_id": chunk.chunk_id,
                "mentions": len(valid_mentions),
                "clusters": len(clusters),
            },
            metrics=metrics.model_dump(),
        )

        # 7. Publish WebSocket event for real-time dashboard updates
        await self._publish_event(chunk.brand, {
            "type": "chunk_processed",
            "brand": chunk.brand,
            "chunkId": chunk.chunk_id,
            "clusterCount": len(clusters),
            "mentionCount": len(valid_mentions),
        })

        # 8. AUTO COMPETITOR DETECTION (runs once per brand)
        try:
            competitors_key = f"brand:{chunk.brand}:competitors_detected"
            already_detected = await self._redis_client.exists(competitors_key)
            
            if not already_detected:
                logger.info(f"Auto-detecting competitors for new brand: {chunk.brand}")
                # Trigger competitor detection asynchronously
                await self.process_competitor_detection({
                    "brand": chunk.brand,
                    "brand_name": chunk.brand  # Use slug as name for now
                })
                # Mark as detected (expires in 7 days to allow re-detection)
                await self._redis_client.set(competitors_key, "1", ex=7 * 24 * 3600)
            else:
                logger.debug(f"Competitor detection already run for {chunk.brand}, skipping.")
        except Exception as e:
            logger.warning(f"Auto competitor detection failed for {chunk.brand}: {e}")

        return result

    async def generate_suggestion(self, brand: str, text: str, sentiment: str) -> list[str]:
        """Generate response suggestions via LLM."""
        return await self._llm_adapter.generate_response_suggestion(text, sentiment)

    # _preprocess moved to pipeline.preprocessor.PipelinePreprocessor
    # _clean_text moved to pipeline.preprocessor.PipelinePreprocessor (static)

    async def _generate_embeddings(self, chunk: Chunk, mentions: list[Mention]) -> tuple[np.ndarray, float]:
        start = time.perf_counter()
        embeddings = await self._embedding_adapter.embed(
            [m.text for m in mentions],
            brand=chunk.brand,
            chunk_id=chunk.chunk_id,
        )
        duration = (time.perf_counter() - start) * 1000
        return embeddings, duration

    async def _perform_clustering(self, chunk: Chunk, embeddings: np.ndarray) -> ClusteringOutput:
        return await self._clusterer.cluster(embeddings, brand=chunk.brand, chunk_id=chunk.chunk_id)

    async def _analyze_clusters(
        self,
        chunk: Chunk,
        mentions: list[Mention],
        clustering_output: ClusteringOutput,
        metrics: ChunkMetrics,
        analysis_map: dict[str, AnalysisResult] = None, # New
    ) -> list[ClusterResult]:
        from .domain_types import EnhancedAnalysis, Emotions
        
        brand = chunk.brand
        chunk_id = chunk.chunk_id
        clusters: list[ClusterResult] = []
        llm_total_ms = 0.0
        spike_total_ms = 0.0


        
        for grouping in clustering_output.clusters:
            cluster_mentions = [mentions[idx] for idx in grouping.indices]
            texts = [mention.text for mention in cluster_mentions]
            examples = [mention.text for mention in cluster_mentions[: self._settings.preprocessing_examples]]

            cluster_start = time.perf_counter()
            # Summarize cluster
            try:
                summary = await self._llm_adapter.summarize(texts)
            except Exception as e:
                logger.error(f"Cluster summary failed: {e}")
                # Fallback: Use concatenated representative texts
                summary = " ".join(texts[:3])
            
            try:
                sentiment = await self._llm_adapter.sentiment(texts)
            except Exception as e:
                logger.error(f"Cluster sentiment failed: {e}")
                sentiment = {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
            
            # Perform enhanced analysis
            # Pass actual mention texts (or examples to limit tokens) for entity/feature extraction
            _enhanced_analysis_dict = {} # Initialize with empty dict
            try:
                # analyze_enhanced expects a list of strings - use actual texts for better extraction
                # Use examples (limited set of representative mentions) to control token usage
                analysis_texts = examples if examples else texts[:5]
                _enhanced_analysis_dict = await self._llm_adapter.analyze_enhanced(analysis_texts)
            except Exception as e:
                logger.error(f"Cluster enhanced analysis failed: {e}")
                # _enhanced_analysis_dict remains empty, which will lead to default values below
            
            enhanced_analysis = EnhancedAnalysis(
                is_sarcastic=_enhanced_analysis_dict.get("is_sarcastic", False),
                urgency=_enhanced_analysis_dict.get("urgency", "low"),
                emotions=Emotions(**_enhanced_analysis_dict.get("emotions", {})),
                topics=_enhanced_analysis_dict.get("topics", []),
                entities=_enhanced_analysis_dict.get("entities", {"people": [], "companies": [], "products": []}),
                language=_enhanced_analysis_dict.get("language", "en"),
                # New Business Fields
                feature_requests=_enhanced_analysis_dict.get("feature_requests", []),
                pain_points=_enhanced_analysis_dict.get("pain_points", []),
                churn_risks=_enhanced_analysis_dict.get("churn_risks", []),
                recommended_actions=_enhanced_analysis_dict.get("recommended_actions", []),
                lead_score=_enhanced_analysis_dict.get("lead_score", 0),
            )
            
            # DEBUG: Log what LLM returned for Advanced Intelligence
            logger.info(f"[LLM_ENHANCED] Brand: {brand} | Cluster: {grouping.cluster_id} | "
                       f"Entities: {enhanced_analysis.entities} | "
                       f"FeatureRequests: {len(enhanced_analysis.feature_requests)} | "
                       f"PainPoints: {len(enhanced_analysis.pain_points)}")
            
            llm_total_ms += (time.perf_counter() - cluster_start) * 1000

            spike_start = time.perf_counter()
            spike_result = await self._spike_detector.detect(brand, grouping.cluster_id, len(cluster_mentions))
            spike_total_ms += (time.perf_counter() - spike_start) * 1000

            clusters.append(
                ClusterResult(
                    cluster_id=grouping.cluster_id,
                    count=len(cluster_mentions),
                    examples=examples,
                    summary=summary,
                    spike=spike_result.is_spike,
                    sentiment=sentiment,
                    topics=enhanced_analysis.topics,
                    enhanced_analysis=enhanced_analysis,
                )
            )

        metrics.llm_time_ms = llm_total_ms
        metrics.spike_detection_time_ms = spike_total_ms
        return clusters

    @staticmethod
    def _clean_text(text: str) -> str:
        text = CLEAN_URL_RE.sub("", text)
        text = CLEAN_WHITESPACE_RE.sub(" ", text)
        text = text.strip().lower()
        return text

    async def process_lead_intent(self, task: dict) -> None:
        """Process a single mention for sales intent."""
        mention_id = task.get("mention_id")
        text = task.get("text")
        if not text:
            return
        
        # Analyze
        analysis = await self._llm_adapter.analyze_commercial_intent(text)
        
        if analysis.get("sales_intent", False):
            score = analysis.get("confidence", 0.0)
            if score > 0.6:
                payload = {
                    "type": "lead",
                    "mentionId": mention_id,
                    "monitorId": task.get("monitor_id"),
                    "userId": task.get("user_id"),
                    "salesIntentScore": score,
                    "intentType": analysis.get("intent_type", "other"),
                    "confidence": score,
                    "painPoint": analysis.get("pain_point"),
                    "sourcePlatform": task.get("source_platform"),
                    "sourceText": text,
                    "sourceAuthor": task.get("source_author"),
                    "sourceUrl": task.get("source_url")
                }
                try:
                    # Use Redis instead of HTTP
                    import json
                    # 1. Work Queue (for email/notifications)
                    await self._redis_client.rpush("queue:leads", json.dumps(payload))
                    
                    # 2. PERSISTENCE: Brand-specific list for Dashboard (by brand slug)
                    brand = task.get("brand")
                    if brand:
                        brand_key = f"leads:brand:{brand}"
                        await self._redis_client.lpush(brand_key, json.dumps(payload))
                        await self._redis_client.ltrim(brand_key, 0, 99)  # Keep 100 recent
                    
                    # 3. Also store by monitor_id if available (for legacy compatibility)
                    monitor_id = task.get("monitor_id")
                    if monitor_id:
                        key = f"leads:monitor:{monitor_id}"
                        await self._redis_client.lpush(key, json.dumps(payload))
                        await self._redis_client.ltrim(key, 0, 99) # Keep 100 recent
                    
                    logger.info(f"Queued lead for mention {mention_id} via Redis (Score: {score})")
                except Exception as e:
                    logger.error(f"Failed to queue lead: {e}")

    async def process_crisis(self, task: dict) -> None:
        """Process a batch of mentions for crisis risk."""
        mentions = task.get("mentions", [])
        if not mentions:
            return
        
        # Reuse enhanced analysis to infer risk
        enhanced = await self._llm_adapter.analyze_enhanced(mentions)
        
        risk_score = 0
        severity = "normal"
        
        # Simple heuristic mapping from enhanced analysis
        neg_sentiment = abs(min(0, enhanced.get("sentiment_score", 0)))
        urgency = enhanced.get("urgency", "low")
        velocity_multiplier = task.get("velocity_multiplier", 1.0)
        
        # Calculate risk based on sentiment and urgency
        base_risk = neg_sentiment * 100
        if urgency == "high":
            base_risk += 40
        elif urgency == "medium":
            base_risk += 20
            
        risk_score = int(min(100, base_risk * max(1.0, velocity_multiplier / 2.0)))
        
        if risk_score > 75:
            severity = "critical"
        elif risk_score > 50:
            severity = "warning"
            
        if risk_score > 50 or velocity_multiplier > 3.0:
            payload = {
                "type": "crisis_event",
                "monitorId": task.get("monitor_id"),
                "riskScore": risk_score,
                "severity": severity,
                "velocityMultiplier": velocity_multiplier,
                "sentimentIntensity": neg_sentiment,
                "mentionCount": len(mentions),
                "triggeredReasons": ["high_negative_sentiment" if neg_sentiment > 0.5 else "high_velocity"],
                "recommendedAction": "Monitor closely"
            }
            try:
                # Use Redis instead of HTTP
                import json
                # 1. Push to work queue for notification worker/email service
                await self._redis_client.rpush("queue:crisis:events", json.dumps(payload))
                
                # 2. Push to brand-specific event list for dashboard display
                brand = task.get("brand")
                if brand:
                    event_key = f"crisis:events:{brand}"
                    # Add ID and timestamp if missing (datetime already imported at top)
                    import uuid
                    if "id" not in payload:
                        payload["id"] = str(uuid.uuid4())
                    if "createdAt" not in payload:
                        payload["createdAt"] = datetime.now(timezone.utc).isoformat()
                        
                    await self._redis_client.lpush(event_key, json.dumps(payload))
                    # Keep last 50 events
                    await self._redis_client.ltrim(event_key, 0, 49)
                    
                    # 3. Update realtime metrics for dashboard gauge
                    metrics_key = f"crisis:metrics:{brand}"
                    metrics_payload = {
                        "riskScore": risk_score,
                        "severity": severity,
                        "velocityMultiplier": velocity_multiplier,
                        "sentimentIntensity": neg_sentiment,
                        "mentionCount": len(mentions),
                        "reasons": payload["triggeredReasons"],
                        "updatedAt": datetime.now().isoformat()
                    }
                    await self._redis_client.set(metrics_key, json.dumps(metrics_payload))
                
                logger.info(f"Queued crisis event via Redis (Score: {risk_score})")
            except Exception as e:
                logger.error(f"Failed to queue crisis event: {e}")

    async def process_competitor_gap(self, task: dict) -> None:
        """Process competitor mentions for gaps."""
        mentions = task.get("mentions", [])
        competitor_id = task.get("competitor_id")
        competitor_name = task.get("competitor_name", "Competitor")
        
        if not mentions:
            return
        
        # Analyze each mention for complaints
        # Ideally we batch this, but for parity with Rust loop logic:
        for mention_text in mentions[:20]: # Limit to 20 to avoid timeout
            complaint = await self._llm_adapter.categorize_competitor_complaint(mention_text, competitor_name)
            
            if complaint.get("category", "other") != "other" or complaint.get("pain_level", 0) > 6:
                payload = {
                    "type": "competitor_complaint",
                    "competitorId": competitor_id,
                    "category": complaint.get("category"),
                    "specificIssue": complaint.get("specific_issue"),
                    "painLevel": complaint.get("pain_level"),
                    "sourceText": mention_text[:500],
                    "sourcePlatform": "python_worker"
                }
                try:
                    # Use Redis instead of HTTP
                    import json
                    # 1. Push to work queue for notification worker (still needed for async processing/email)
                    await self._redis_client.rpush("queue:competitors:complaints", json.dumps(payload))
                    
                    # 2. PERSISTENCE: Push to brand-specific list for Dashboard View (Non-destructive)
                    # We need to know the 'my brand' context. processor.process_competitor_gap doesn't explicitly have it passed always,
                    # but typically detailed tasks have context.
                    # Assuming we can infer or it's global for the user.
                    # For now, let's store by competitor_id as that's unique enough for retrieval.
                    key = f"competitor:complaints:{competitor_id}"
                    await self._redis_client.lpush(key, json.dumps(payload))
                    await self._redis_client.ltrim(key, 0, 99) # Keep 100 recent
                    
                    logger.info(f"Queued competitor complaint via Redis (category: {complaint.get('category')})")
                except Exception as e:
                    logger.error(f"Failed to queue complaint: {e}")

    async def process_web_scan(self, task: dict) -> None:
        """Process a web deep scan task."""
        brand = task.get("brand")
        if not brand:
            logger.error("Web scan task missing brand")
            return

        try:
            logger.info(f"Processing web scan for {brand}")
            result = await self._web_scanner.scan(brand)
            
            # Save to Redis for API to pick up
            # Key format: result:brand:{slug}:web_insights
            import json
            key = f"result:brand:{brand}:web_insights"
            await self._redis_client.set(key, json.dumps(result))
            
            # Also set a TTL of 24h
            await self._redis_client.expire(key, 86400)
            
            logger.info(f"Completed web scan for {brand}, saved to {key}")
            
        except Exception as e:
            logger.error(f"Web scan failed for {brand}: {e}")

    async def process_competitor_detection(self, task: dict) -> None:
        """Process a competitor detection task using LLM."""
        brand = task.get("brand")
        brand_name = task.get("brandName", brand)
        
        if not brand:
            logger.error("Competitor detection task missing brand")
            return

        try:
            logger.info(f"Processing competitor detection for {brand_name}")
            
            # Use LLM adapter to detect competitors
            # Note: We pass None for description/keywords as they aren't in the basic task payload yet.
            # If the task provides them later, we can extract them: task.get("description"), task.get("keywords")
            result_data = await self._llm_adapter.detect_competitors(
                brand_name=brand_name,
                brand_description=task.get("description"), # Optional, if present
                brand_keywords=task.get("keywords")        # Optional, if present
            )
            
            competitors = result_data.get("competitors", [])
            
            result = {"suggestedCompetitors": competitors}
            
            # Save to Redis for API to pick up
            key = f"result:brand:{brand}:competitors_detected"
            await self._redis_client.set(key, json.dumps(result))
            await self._redis_client.expire(key, 86400 * 7)  # 7 day TTL
            
            logger.info(f"Completed competitor detection for {brand}, found {len(competitors)} competitors")
            
        except Exception as e:
            logger.error(f"Competitor detection failed for {brand}: {e}")
