import asyncio
import logging
import json
import time
from typing import Any, List

from .logger import get_logger, log_with_context
from .config import get_settings
from .utils import safe_json_loads
from .queue_consumer import extract_brand_from_queue
from .metrics import worker_chunks_processed_total, worker_processing_time_seconds

logger = get_logger(__name__)

class QueueWorker:
    """Handles the infinite loops for processing, retries, and heartbeats."""

    def __init__(
        self,
        worker_id: str,
        settings: Any,
        redis_client,
        queue_consumer,
        processor,
        batch_processor,
        storage
    ) -> None:
        self._worker_id = worker_id
        self._settings = settings
        self._redis = redis_client
        self._queue_consumer = queue_consumer
        self._processor = processor
        self._batch_processor = batch_processor
        self._storage = storage
        self._stop_event = asyncio.Event()
        self._tasks: List[asyncio.Task[Any]] = []

    async def start(self) -> None:
        await self._redis.ensure_connection()
        self._stop_event.clear()
        self._tasks = [
            asyncio.create_task(self._heartbeat_loop(), name="heartbeat"),
            asyncio.create_task(self._processing_loop(), name="processing"),
            asyncio.create_task(self._failed_retry_loop(), name="failed_retry"),
        ]
        log_with_context(
            logger,
            level=logging.INFO,
            message="QueueWorker started",
            context={"worker_id": self._worker_id},
        )

    async def stop(self) -> None:
        self._stop_event.set()
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        # Flush pending results
        if self._storage:
            await self._storage.close()
            
        await self._redis.close()
        log_with_context(
            logger,
            level=logging.INFO,
            message="QueueWorker stopped",
            context={"worker_id": self._worker_id},
        )

    async def _heartbeat_loop(self) -> None:
        interval = max(self._settings.heartbeat_interval_sec, 1)
        try:
            while not self._stop_event.is_set():
                await self._redis.set_heartbeat(self._worker_id, interval)
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=interval)
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            raise
        except Exception as exc: 
            logger.exception("Heartbeat loop error", extra={"context_error": str(exc)})

    async def _processing_loop(self) -> None:
        concurrency = self._settings.llm_max_concurrency
        sem = asyncio.Semaphore(concurrency)
        active_tasks: set[asyncio.Task] = set()
        
        log_with_context(
            logger, 
            level=logging.INFO, 
            message=f"Worker processing loop started with concurrency={concurrency}",
            context={"worker_id": self._worker_id}
        )

        async def _process_task(q_key: str, p_loads: list[str], f_time: float):
            try:
                await self._handle_batch(q_key, p_loads, f_time)
            except Exception as e:
                logger.error(f"Task processing error: {e}")
            finally:
                sem.release()

        try:
            while not self._stop_event.is_set():
                await sem.acquire()
                
                try:
                    fetch = await self._queue_consumer.fetch()
                    if fetch is None:
                        sem.release()
                        continue
                        
                    queue_key, payloads, fetch_time_ms = fetch
                    
                    task = asyncio.create_task(_process_task(queue_key, payloads, fetch_time_ms))
                    active_tasks.add(task)
                    task.add_done_callback(active_tasks.discard)
                    
                except Exception as e:
                    sem.release()
                    logger.error(f"Fetch loop error: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Processing loop cancelled, waiting for active tasks...")
            if active_tasks:
                await asyncio.gather(*active_tasks, return_exceptions=True)
            raise
        except Exception as exc: 
            logger.exception("Processing loop error", extra={"context_error": str(exc)})

    async def _handle_batch(self, queue_key: str, payloads: list[str], fetch_time_ms: float) -> None:
        # 1. Special queues
        if queue_key == "tasks:priority":
            for payload in payloads:
                try:
                    task = safe_json_loads(payload)
                    task_type = task.get("type")
                    if task_type == "analyze_lead_intent":
                        await self._processor.process_lead_intent(task)
                    elif task_type == "analyze_crisis":
                        await self._processor.process_crisis(task)
                    elif task_type == "analyze_competitor_gap":
                        await self._processor.process_competitor_gap(task)
                    elif task_type == "competitor_detection":
                        await self._processor.process_competitor_detection(task)
                    else:
                        logger.warning(f"Unknown task type in priority queue: {task_type}")
                except Exception as exc:
                    logger.error(f"Failed to process priority task: {exc}", extra={"payload": payload})
            return

        if queue_key == "tasks:web_scan":
            for payload in payloads:
                try:
                    task = safe_json_loads(payload)
                    await self._processor.process_web_scan(task)
                except Exception as exc:
                    logger.error(f"Failed to process web scan task: {exc}", extra={"payload": payload})
            return

        if queue_key == "queue:competitor_detection":
            for payload in payloads:
                try:
                    task = safe_json_loads(payload)
                    logger.info(f"Processing auto competitor detection for brand: {task.get('brand')}")
                    await self._processor.process_competitor_detection(task)
                except Exception as exc:
                    logger.error(f"Failed to process competitor detection task: {exc}", extra={"payload": payload})
            return

        # 2. Mention Queues - Batching
        brand_hint = extract_brand_from_queue(queue_key)
        chunk = await self._batch_processor.process_batch(brand_hint, payloads)
        
        if not chunk:
            return

        # NEW: Push mention stats immediately for Live Mentions view
        try:
            await self._storage.push_mention_stats(
                brand_hint, 
                [m.model_dump(mode='json') for m in chunk.mentions]
            )
        except Exception as e:
            logger.error(f"Failed to push mention stats: {e}")

        try:
            result = await self._processor.process_chunk(chunk, fetch_time_ms=fetch_time_ms, envelope={"batch": True})
            push_time_ms = await self._storage.push_result(brand_hint, result)
            result.metrics.io_time_ms += push_time_ms
            worker_processing_time_seconds.labels(self._worker_id, brand_hint).observe(
                result.metrics.total_task_time_ms / 1000
            )
            worker_chunks_processed_total.labels(self._worker_id, brand_hint).inc()
        except Exception as exc:
            logger.error(f"Batch processing failed: {exc}")
            pass

    async def _failed_retry_loop(self) -> None:
        MAX_RETRIES = 5
        RETRY_INTERVAL = 30
        
        try:
            while not self._stop_event.is_set():
                pattern = "failed:brand:*"
                cursor = 0
                failed_keys = []
                
                try:
                    while True:
                        cursor, keys = await self._redis.client.scan(cursor=cursor, match=pattern, count=100)
                        failed_keys.extend(keys)
                        if cursor == 0:
                            break
                except Exception as e:
                    logger.error(f"Failed to scan failed queues: {e}")
                    await asyncio.sleep(RETRY_INTERVAL)
                    continue
                
                if failed_keys:
                    logger.info(f"Found {len(failed_keys)} failed queues to retry: {failed_keys[:5]}")
                
                for failed_key in failed_keys:
                    try:
                        raw_item = await self._redis.client.rpop(failed_key)
                        if not raw_item:
                            continue
                        
                        try:
                            failure_record = json.loads(raw_item)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON in failed queue: {raw_item[:100]}")
                            continue
                        
                        retry_count = failure_record.get("_retry_count", 0) + 1
                        brand = failure_record.get("brand", "unknown")
                        original_payload = failure_record.get("payload", "{}")
                        
                        if retry_count > MAX_RETRIES:
                            logger.warning(f"Max retries ({MAX_RETRIES}) exceeded for {brand}, discarding item")
                            continue
                        
                        backoff = 2 ** (retry_count - 1)
                        logger.info(f"Retrying failed item for {brand} (attempt {retry_count}/{MAX_RETRIES}) after {backoff}s backoff")
                        
                        await asyncio.sleep(backoff)
                        
                        data_queue = f"queue:brand:{brand}:raw_mentions"
                        
                        try:
                            payload_data = json.loads(original_payload)
                            payload_data["_retry_count"] = retry_count
                            await self._redis.client.lpush(data_queue, json.dumps(payload_data))
                            logger.info(f"Re-queued failed item to {data_queue}")
                        except Exception as e:
                            logger.error(f"Failed to re-queue: {e}")
                            failure_record["_retry_count"] = retry_count
                            await self._redis.client.lpush(failed_key, json.dumps(failure_record))
                        
                    except Exception as e:
                        logger.error(f"Error processing failed queue {failed_key}: {e}")
                
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=RETRY_INTERVAL)
                except asyncio.TimeoutError:
                    continue
                    
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Failed retry loop error", extra={"context_error": str(exc)})
