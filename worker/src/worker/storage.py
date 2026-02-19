"""Storage utilities for persisting results back to Redis."""
from __future__ import annotations

import json
import logging
import time
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from .config import get_settings
from .logger import get_logger, log_with_context
from .metrics import worker_chunks_failed_total, worker_io_time_seconds
from .redis_client import RedisClient
from .domain_types import ChunkResult, ClusterResult, FailureRecord
from .utils import timer

logger = get_logger(__name__)


class ResultStorage:
    """Store chunk results and failures in Redis with instrumentation."""


    def __init__(self, redis_client: RedisClient, worker_id: str, mongo_client: Any = None) -> None:
        self._redis = redis_client
        self._settings = get_settings()
        self._worker_id = worker_id
        # Use provided client or fallback to None (graceful degradation if not configured)
        self._mongo = mongo_client
        if self._mongo:
            self._db = self._mongo.brand_tracker
            self._collection = self._db.processed_chunks
            
        # Buffering
        self._buffer: Dict[str, List[str]] = {} # brand -> list of payloads
        self._buffer_size_bytes = 0
        self._last_flush_time = time.time()
        self._flush_lock = asyncio.Lock()
        
        # Limits
        self._max_buffer_bytes = 50 * 1024 * 1024 # 50MB
        self._max_buffer_age_sec = 180 # 3 minutes

    async def close(self) -> None:
        """Flush any remaining data in the buffer."""
        await self.flush()

    async def flush(self) -> None:
        """Flush buffered results to Redis."""
        async with self._flush_lock:
            if not self._buffer:
                return

            try:
                # Use Redis pipeline for batch insertion
                # For each brand, rpush all items
                # We can't use a single pipeline for EVERYTHING if it's huge, but 50MB is manageable in chunks
                # Redis client wrapper doesn't expose pipeline directly often, check implementation
                # redis_client.py uses aioredis/redis-py which supports pipeline
                
                # We need access to raw pipeline if client encapsulation prevents it
                # Assuming _redis.client exposes it
                
                pipeline = self._redis.client.pipeline()
                
                brands_to_flush = list(self._buffer.keys())
                count = 0
                
                for brand in brands_to_flush:
                    payloads = self._buffer[brand]
                    if not payloads:
                        continue
                        
                    key = f"{self._settings.redis_result_prefix}{brand}:chunks"
                    # rpush multiple
                    pipeline.rpush(key, *payloads)
                    count += len(payloads)
                
                with timer() as timing:
                    await pipeline.execute()
                
                elapsed_ms = timing["elapsed_ms"]
                
                log_with_context(
                    logger,
                    level=logging.INFO,
                    message="Flushed result buffer",
                    context={
                        "worker_id": self._worker_id,
                        "brands": len(brands_to_flush),
                        "items": count,
                        "bytes": self._buffer_size_bytes
                    },
                    metrics={"flush_time_ms": elapsed_ms}
                )

                # Reset
                self._buffer.clear()
                self._buffer_size_bytes = 0
                self._last_flush_time = time.time()

            except Exception as e:
                log_with_context(
                    logger,
                    level=logging.ERROR,
                    message="Failed to flush buffer",
                    context={"error": str(e)}
                )

    async def save_result(self, envelope: Dict[str, Any], result_json: Dict[str, Any]) -> None:
        """Persist result to MongoDB with deduplication."""
        if not self._mongo:
            return

        import hashlib
        
        # 1. Generate Content Hash (SHA256)
        # source_url + "|" + text header for dedup
        # If specific text fields aren't present, fallback to ID to avoid collision on empty
        source_url = result_json.get("source_url", envelope.get("envelope_id", "unknown"))
        # Try to find meaningful text content
        text_candidate = result_json.get("text", "")
        if not text_candidate:
            text_candidate = result_json.get("summary", "")
        if not text_candidate:
            # Fallback to result dump if no text, making it unique per result content
            text_candidate = json.dumps(result_json, sort_keys=True)
            
        raw_sig = f"{source_url}|{text_candidate}".encode("utf-8")
        content_hash = hashlib.sha256(raw_sig).hexdigest()

        # 2. Prepare BSON doc
        # Current time
        now = datetime.now(timezone.utc)
        
        # 3. Upsert
        # $set: last_seen -> update every time
        # $setOnInsert: first_seen, content, static metadata -> only on first time
        
        filter_doc = {"content_hash": content_hash}
        update_doc = {
            "$set": {
                "last_seen": now
            },
            "$setOnInsert": {
                "batch_id": envelope.get("batch_id"),
                "org_id": envelope.get("secure_context", {}).get("org_id"),
                "chunk_id": envelope.get("envelope_id"),
                "content_hash": content_hash,
                "result": result_json,
                "first_seen": now
            }
        }
        
        try:
            with timer() as timing:
                await self._collection.update_one(filter_doc, update_doc, upsert=True)
            elapsed_ms = timing["elapsed_ms"]
            
            log_with_context(
                logger,
                level=logging.INFO,
                message="Result saved to MongoDB",
                context={
                    "worker_id": self._worker_id,
                    "content_hash": content_hash[:16],
                    "is_dedup": True # Implicitly true if logic works, we don't know if it inserted or updated without checking result return
                },
                metrics={"mongo_save_ms": elapsed_ms}
            )
        except Exception as e:
            log_with_context(
                logger,
                level=logging.ERROR,
                message="Failed to save to MongoDB",
                context={"error": str(e)}
            )

    async def push_result(self, brand: str, result: ChunkResult) -> float:
        payload = json.dumps(self._format_for_orchestrator(result), default=str)
        payload_size = len(payload)
        
        async with self._flush_lock:
            if brand not in self._buffer:
                self._buffer[brand] = []
            
            self._buffer[brand].append(payload)
            self._buffer_size_bytes += payload_size
            
            should_flush = (
                self._buffer_size_bytes >= self._max_buffer_bytes or 
                (time.time() - self._last_flush_time >= self._max_buffer_age_sec)
            )
        
        if should_flush:
            await self.flush()
            
        # Return 0 or small constant since we buffered. 
        # Real IO time happens in flush. Capturing per-item IO is accurate enough for batch.
        return 0.0


    async def push_mention_stats(self, brand: str, mentions: List[Dict[str, Any]]) -> None:
        """Push individual mention stats to Redis for dashboard aggregation."""
        if not mentions:
            return

        now = datetime.now(timezone.utc)
        day = now.strftime("%Y-%m-%d")
        hour = now.strftime("%H")
        
        # Keys expected by stats.service.ts
        keys = [
            f"data:brand:{brand}:optimized_mentions",
            f"data:brand:{brand}:{day}:{hour}"
        ]
        
        try:
            async with self._redis._lock: # Use lock if batching, or just pipeline
                pipe = self._redis.client.pipeline()
                for mention in mentions:
                    payload = json.dumps(mention, default=str)
                    for key in keys:
                        pipe.lpush(key, payload)
                        pipe.ltrim(key, 0, 999) # Keep last 1000
                        pipe.expire(key, 86400 * 30) # 30 days retention
                    
                    # Influencers Sorted Set (Top 100 by influence score)
                    # Key: data:brand:{brand}:influencers
                    # Score: influence_score
                    inf_score = mention.get("influence_score", 0)
                    if inf_score > 0:
                         inf_key = f"data:brand:{brand}:influencers"
                         pipe.zadd(inf_key, {payload: inf_score})
                         pipe.zremrangebyrank(inf_key, 0, -101) # Keep top 100
                         pipe.expire(inf_key, 86400 * 30) # 30 days retention

                    # Timeline Sorted Set (For flexible time-range queries)
                    # Key: data:brand:{brand}:timeline
                    # Score: Timestamp
                    timeline_key = f"data:brand:{brand}:timeline"
                    
                    # Try to get timestamp from created_at string or object, else use current time
                    created_at = mention.get("created_at")
                    score = 0.0
                    try:
                        if isinstance(created_at, str):
                            # Try ISO format
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            score = dt.timestamp()
                        elif isinstance(created_at, datetime):
                            score = created_at.timestamp()
                        else:
                            score = datetime.now(timezone.utc).timestamp()
                    except Exception:
                        score = datetime.now(timezone.utc).timestamp()

                    pipe.zadd(timeline_key, {payload: score})
                    # Keep last 10,000 items to control memory
                    pipe.zremrangebyrank(timeline_key, 0, -10001) 
                    pipe.expire(timeline_key, 86400 * 30) # 30 days retention

                    comp_key = "" # Init
                    
                    # Competitor Intelligence Storage
                    meta = mention.get("metadata") or {}
                    if meta.get("isCompetitor") and meta.get("competitorId"):
                        comp_id = meta.get("competitorId")
                        # 1. Store mention list
                        comp_key = f"competitor:{comp_id}:mentions"
                        pipe.lpush(comp_key, payload)
                        pipe.ltrim(comp_key, 0, 999)
                        pipe.expire(comp_key, 86400 * 30) # 30 days retention
                        
                        # 2. Increment counters for fast lookup
                        pipe.incr(f"competitor:{comp_id}:mention_count")
                        sentiment_label = mention.get("sentiment", "neutral")
                        pipe.incr(f"competitor:{comp_id}:sentiment:{sentiment_label}")
                         
                await pipe.execute()
        except Exception as e:
            logger.warning(f"Failed to push mention stats: {e}")

    async def update_brand_summary(self, brand: str, result: ChunkResult, health_score: int | float | None = None) -> None:
        """
        Update the global brand summary in Redis with the latest chunk data.
        aggregates:
        - Sentiment counts
        - Dominant topics
        - Latest summary (if meaningful)
        - Spike status
        - Health Score
        """
        key = f"{self._settings.redis_summary_prefix}{brand}"
        
        try:
            # 1. Get existing summary
            raw = await self._redis.get(key)
            if raw:
                try:
                    summary = json.loads(raw)
                except json.JSONDecodeError:
                    summary = {}
            else:
                summary = {}
            
            # Ensure defaults
            summary.setdefault("brand", brand)
            summary.setdefault("generatedAt", datetime.now(timezone.utc).isoformat())
            summary.setdefault("totalChunks", 0)
            summary.setdefault("totalMentions", 0)
            summary.setdefault("sentiment", {"positive": 0, "neutral": 0, "negative": 0, "score": 0})
            summary.setdefault("dominantTopics", [])
            summary.setdefault("clusters", [])
            summary.setdefault("spikeDetected", False)
            summary.setdefault("summary", "Waiting for enough data...")
            summary.setdefault("chunkSummaries", [])
            summary.setdefault("healthScore", 50)  # Default health score

            # Update Health Score if provided
            if health_score is not None:
                summary["healthScore"] = round(health_score)


            # 2. Update stats from this chunk
            summary["totalChunks"] += 1
            
            # Count mentions and sentiment in this chunk
            chunk_mentions_count = 0
            pos_delta = 0
            neu_delta = 0
            neg_delta = 0
            
            for cluster in result.clusters:
                count = cluster.count
                chunk_mentions_count += count
                
                # Estimate sentiment class for the group of mentions
                s = cluster.sentiment or {}
                # Classification based on dominant score (relative comparison)
                p_score = s.get("positive", 0)
                n_score = s.get("negative", 0)
                neu_score = s.get("neutral", 0)
                
                # Improved classification: assign mentions based on which sentiment is highest
                # If all are equal or too close, default to neutral
                max_score = max(p_score, n_score, neu_score)
                
                # Must have SOME sentiment signal to classify
                if max_score == 0:
                    neu_delta += count
                elif p_score >= n_score and p_score >= neu_score:
                    # Positive is dominant or tied for highest
                    pos_delta += count
                elif n_score >= p_score and n_score >= neu_score:
                    # Negative is dominant or tied for highest
                    neg_delta += count
                else:
                    # Neutral wins
                    neu_delta += count

            summary["totalMentions"] += chunk_mentions_count
            
            # Update sentiment counts
            summary["sentiment"]["positive"] += pos_delta
            summary["sentiment"]["neutral"] += neu_delta
            summary["sentiment"]["negative"] += neg_delta
            
            # Recalculate normalized score (-1 to 1)
            total = summary["sentiment"]["positive"] + summary["sentiment"]["neutral"] + summary["sentiment"]["negative"]
            if total > 0:
                score = (summary["sentiment"]["positive"] - summary["sentiment"]["negative"]) / total
                summary["sentiment"]["score"] = round(score, 2)
            
            # 3. Update Text Content
            if result.summary:
                summary["summary"] = result.summary
                summary["generatedAt"] = datetime.now(timezone.utc).isoformat()
                # Keep history of summaries? optional.
                
            if result.topics:
                # Merge topics (simple set union)
                current = set(summary["dominantTopics"])
                for t in result.topics:
                    current.add(t)
                summary["dominantTopics"] = list(current)[:10]
            
            # NEW: Aggregate entities from clusters for Advanced Intelligence
            summary.setdefault("entities", {"people": [], "companies": [], "products": []})
            for cluster in result.clusters:
                if cluster.enhanced_analysis and cluster.enhanced_analysis.entities:
                    entities = cluster.enhanced_analysis.entities
                    # Merge entities (deduplicate by name)
                    for entity_type in ["people", "companies", "products"]:
                        # Use dict keyed by name for deduplication
                        existing_by_name = {}
                        for ent in summary["entities"].get(entity_type, []):
                            if isinstance(ent, str):
                                existing_by_name[ent] = ent
                            elif isinstance(ent, dict):
                                existing_by_name[ent.get("name", "")] = ent
                        
                        new_entities = entities.get(entity_type, [])
                        for entity in new_entities:
                            if isinstance(entity, str):
                                if entity not in existing_by_name:
                                    existing_by_name[entity] = entity
                            elif isinstance(entity, dict):
                                name = entity.get("name", "")
                                if name and name not in existing_by_name:
                                    existing_by_name[name] = entity
                        
                        # Keep top 20 per type
                        summary["entities"][entity_type] = list(existing_by_name.values())[:20]
            
            # NEW: Aggregate Business Intelligence fields
            summary.setdefault("feature_requests", [])
            summary.setdefault("pain_points", [])
            summary.setdefault("churn_risks", [])
            summary.setdefault("recommended_actions", [])
            summary.setdefault("avgLeadScore", 0)
            
            lead_score_sum = 0
            lead_score_count = 0

            for cluster in result.clusters:
                if cluster.enhanced_analysis:
                    ea = cluster.enhanced_analysis
                    
                    # Aggregate lists (handle both string and dict items)
                    for field_name in ["feature_requests", "pain_points", "churn_risks", "recommended_actions"]:
                        new_items = getattr(ea, field_name, [])
                        existing = summary.get(field_name, [])
                        
                        # Use dict for deduplication with proper handling
                        seen = {}
                        for item in existing:
                            if isinstance(item, str):
                                seen[item] = item
                            elif isinstance(item, dict):
                                key = item.get("text") or item.get("name") or str(item)
                                seen[key] = item
                        
                        for item in new_items:
                            if isinstance(item, str):
                                if item not in seen:
                                    seen[item] = item
                            elif isinstance(item, dict):
                                key = item.get("text") or item.get("name") or str(item)
                                if key not in seen:
                                    seen[key] = item
                        
                        summary[field_name] = list(seen.values())[:20]  # Keep top 20 unique items
                    
                    # Aggregate lead score
                    if ea.lead_score > 0:
                        lead_score_sum += ea.lead_score
                        lead_score_count += 1
            
            # Update average lead score
            if lead_score_count > 0:
                current_avg = summary.get("avgLeadScore", 0)
                # Weighted average with history (simplified: new chunks influence 20%)
                # Actually, simplified: just store last seen average from this chunk if we treat summary as a "snapshot" or cumulative? 
                # Better: simple moving average or just replace? Let's treat it as "Latest Intelligence".
                # But summary is cumulative. Let's just average this chunk's score into the existing.
                new_chunk_avg = lead_score_sum / lead_score_count
                if current_avg == 0:
                    summary["avgLeadScore"] = round(new_chunk_avg)
                else:
                    summary["avgLeadScore"] = round((current_avg * 0.8) + (new_chunk_avg * 0.2)) # Slowly shift matches recent trend


            if result.spikeDetected:
                summary["spikeDetected"] = True

            # 4. Update Sentiment History (Rolling 30 days)
            history = summary.get("sentimentHistory", [])
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            # Find today's entry
            today_entry = next((item for item in history if item["date"] == today_str), None)
            
            if today_entry:
                today_entry["positive"] += pos_delta
                today_entry["neutral"] += neu_delta
                today_entry["negative"] += neg_delta
                # Recompute score for the day
                day_total = today_entry["positive"] + today_entry["neutral"] + today_entry["negative"]
                today_entry["score"] = round((today_entry["positive"] - today_entry["negative"]) / day_total, 2) if day_total > 0 else 0
            else:
                # Create new entry
                day_total = pos_delta + neu_delta + neg_delta
                score = round((pos_delta - neg_delta) / day_total, 2) if day_total > 0 else 0
                history.append({
                    "date": today_str,
                    "positive": pos_delta,
                    "neutral": neu_delta,
                    "negative": neg_delta,
                    "score": score
                })
            
            # Sort by date and keep last 90
            history.sort(key=lambda x: x["date"])
            summary["sentimentHistory"] = history[-90:]

            # 5. Save
            await self._redis.set(key, json.dumps(summary, default=str))
            
            # DEBUG: Log Advanced Intelligence data being saved
            entities_count = {
                "people": len(summary.get("entities", {}).get("people", [])),
                "companies": len(summary.get("entities", {}).get("companies", [])),
                "products": len(summary.get("entities", {}).get("products", []))
            }
            logger.info(f"[ADVANCED_INTELLIGENCE] Brand: {brand} | Entities: {entities_count} | "
                       f"FeatureRequests: {len(summary.get('feature_requests', []))} | "
                       f"PainPoints: {len(summary.get('pain_points', []))} | "
                       f"ChurnRisks: {len(summary.get('churn_risks', []))} | "
                       f"Actions: {len(summary.get('recommended_actions', []))}")
            
            log_with_context(
                logger, 
                logging.INFO, 
                "Updated brand summary", 
                context={"brand": brand, "mentions_added": chunk_mentions_count}
            )

        except Exception as e:
            logger.error(f"Failed to update brand summary: {e}")

    def _format_for_orchestrator(self, result: ChunkResult) -> Dict[str, Any]:
        clusters_payload = self._build_clusters(result.clusters)
        sentiment = self._aggregate_sentiment(result.clusters)
        topics = self._extract_topics(result.clusters)
        spike_detected = any(cluster.get("spike", False) for cluster in clusters_payload)
        mention_count = sum(cluster["mentionCount"] for cluster in clusters_payload)

        return {
            "chunkId": result.chunk_id,
            "brand": result.brand,
            "processedAt": datetime.now(timezone.utc).isoformat(),
            "sentiment": sentiment,
            "clusters": clusters_payload,
            "topics": topics,
            "summary": self._combine_summaries(result.clusters),
            "spikeDetected": spike_detected,
            "meta": {
                "metrics": result.metrics.model_dump(),
                "mentionCount": mention_count,
            },
        }

    def _build_clusters(self, clusters: List[ClusterResult]) -> List[Dict[str, Any]]:
        cluster_payload: List[Dict[str, Any]] = []
        for cluster in clusters:
            sentiment = cluster.sentiment or {}
            sentiment_score = float(sentiment.get("positive", 0.0)) - float(sentiment.get("negative", 0.0))
            label = self._normalize_summary_text(cluster.summary, cluster.examples, fallback_label=f"Cluster {cluster.cluster_id}")
            cluster_payload.append(
                {
                    "id": str(cluster.cluster_id),
                    "label": label,
                    "mentions": cluster.examples,
                    "sentimentScore": sentiment_score,
                    "spike": cluster.spike,
                    "mentionCount": cluster.count,
                }
            )
        return cluster_payload

    def _aggregate_sentiment(self, clusters: List[ClusterResult]) -> Dict[str, float]:
        totals = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        counted = 0
        for cluster in clusters:
            if not cluster.sentiment:
                continue
            counted += 1
            totals["positive"] += float(cluster.sentiment.get("positive", 0.0))
            totals["neutral"] += float(cluster.sentiment.get("neutral", 0.0))
            totals["negative"] += float(cluster.sentiment.get("negative", 0.0))

        if counted > 0:
            for key in totals:
                totals[key] /= counted

        totals["score"] = totals["positive"] - totals["negative"]
        return totals

    def _extract_topics(self, clusters: List[ClusterResult]) -> List[str]:
        topics: List[str] = []
        for cluster in clusters:
            normalized = self._normalize_summary_text(cluster.summary, cluster.examples)
            if normalized:
                topics.append(normalized)
            elif cluster.examples:
                topics.extend(cluster.examples[:1])
        return [topic.strip() for topic in topics if topic.strip()][:10]

    def _combine_summaries(self, clusters: List[ClusterResult]) -> str:
        lines: List[str] = []
        for cluster in clusters:
            normalized = self._normalize_summary_text(cluster.summary, cluster.examples)
            if normalized:
                lines.append(normalized)
        if not lines:
            return ""
        return " ".join(lines)

    def _normalize_summary_text(self, summary: str | None, examples: List[str], *, fallback_label: str | None = None) -> str:
        candidate = (summary or "").strip()
        if candidate.startswith("{") and candidate.endswith("}") and "positive" in candidate and "negative" in candidate:
            candidate = ""
        if not candidate and examples:
            candidate = examples[0].strip()
        if not candidate and fallback_label:
            candidate = fallback_label
        return candidate

    async def record_failure(self, brand: str, failure: FailureRecord, *, reason_label: str) -> float:
        key = f"{self._settings.redis_failed_prefix}{brand}"
        payload = failure.model_dump_json()
        with timer() as timing:
            await self._redis.record_failure(key, payload)
        elapsed_ms = timing["elapsed_ms"]
        worker_chunks_failed_total.labels(self._worker_id, brand, reason_label).inc()
        worker_io_time_seconds.labels(self._worker_id, brand, "failure").observe(elapsed_ms / 1000)
        log_with_context(
            logger,
            level=logging.WARNING,
            message="Failure recorded",
            context={
                "worker_id": self._worker_id,
                "brand": brand,
                "chunk_id": failure.chunk_id,
                "reason": failure.reason,
            },
            metrics={"failure_record_time_ms": elapsed_ms},
        )
        return elapsed_ms

    async def push_leads(self, brand: str, leads: list[ChunkResult | Any]) -> None:
        """Push high-intent leads to dedicated Redis list."""
        if not leads:
            return
            
        key = f"leads:brand:{brand}"
        
        try:
            async with self._redis._lock:
                pipe = self._redis.client.pipeline()
                for lead in leads:
                    # Format for API Gateway (matches fetchLeads expectation)
                    # Use default=str to handle datetime serialization
                    payload = json.dumps(lead, default=str)
                    pipe.lpush(key, payload)
                
                # Keep last 100 leads
                pipe.ltrim(key, 0, 99)
                pipe.expire(key, 86400 * 30) # 30 days retention
                await pipe.execute()
                
            log_with_context(logger, logging.INFO, "Pushed leads to Redis", context={"count": len(leads), "brand": brand})
        except Exception as e:
            logger.error(f"Failed to push leads: {e}")

    async def push_crisis_event(self, brand: str, event: dict) -> None:
        """Push crisis event to Redis history."""
        key = f"crisis:events:{brand}"
        try:
            payload = json.dumps(event, default=str)
            await self._redis.client.lpush(key, payload)
            await self._redis.client.ltrim(key, 0, 49) # Keep last 50 events
            await self._redis.client.expire(key, 86400 * 30)
        except Exception as e:
            logger.error(f"Failed to push crisis event: {e}")

    async def update_crisis_metrics(self, brand: str, metrics: dict) -> None:
        """Update current crisis status metrics."""
        key = f"crisis:metrics:{brand}"
        try:
            await self._redis.set(key, json.dumps(metrics, default=str), ex=86400) # 24h TTL
        except Exception as e:
            logger.error(f"Failed to update crisis metrics: {e}")

    async def push_spike_timeline(self, brand: str, spike_event: dict) -> None:
        """Push spike event to spike:brand:{brand} list for API Gateway to read."""
        key = f"spike:brand:{brand}"
        try:
            payload = json.dumps(spike_event, default=str)
            await self._redis.client.lpush(key, payload)
            await self._redis.client.ltrim(key, 0, 99)  # Keep last 100 spikes
            await self._redis.client.expire(key, 86400 * 7)  # 7 day TTL
            log_with_context(logger, logging.INFO, "Pushed spike event", context={"brand": brand})
        except Exception as e:
            logger.error(f"Failed to push spike event: {e}")

    async def push_launch_prediction(self, brand: str, prediction: dict, is_competitor: bool = False) -> None:
        """Push launch prediction (The Oracle) to Redis for API Gateway to read."""
        key_suffix = "competitor" if is_competitor else "my"
        key = f"launch:brand:{brand}:{key_suffix}"
        try:
            payload = json.dumps(prediction, default=str)
            await self._redis.set(key, payload, ex=86400 * 30)  # 30 day TTL
            log_with_context(logger, logging.INFO, "Pushed launch prediction", context={"brand": brand, "is_competitor": is_competitor})
        except Exception as e:
            logger.error(f"Failed to push launch prediction: {e}")

