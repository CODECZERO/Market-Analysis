"""Application entry point orchestrating the worker service."""
from __future__ import annotations

import asyncio
import logging
import signal
import socket
import sys
import pathlib

from typing import Any

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response
from uvicorn import Config, Server

try:
    from . import metrics  # noqa: F401 ensure metric registration
    from .config import get_settings
    from .health import router as health_router
    from .logger import configure_logging, get_logger, log_with_context
    from .processor import ChunkProcessor
    from .queue_consumer import QueueConsumer
    from .redis_client import RedisClient
    from .storage import ResultStorage
    from .batch_processor import BatchProcessor
    from .queue_worker import QueueWorker
    from .spike_detector import SpikeDetector
except ImportError:
    # Fallback for running as script
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

    from worker import metrics  # type: ignore
    from worker.config import get_settings  # type: ignore
    from worker.health import router as health_router  # type: ignore
    from worker.logger import configure_logging, get_logger, log_with_context  # type: ignore
    from worker.processor import ChunkProcessor  # type: ignore
    from worker.queue_consumer import QueueConsumer  # type: ignore
    from worker.redis_client import RedisClient  # type: ignore
    from worker.storage import ResultStorage  # type: ignore
    from worker.batch_processor import BatchProcessor
    from worker.queue_worker import QueueWorker

logger = get_logger(__name__)

# Global instance for API access
queue_worker_instance: QueueWorker | None = None

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- COMPOSITION ROOT ---
    global queue_worker_instance
    
    settings = get_settings()
    configure_logging(settings.log_level)
    
    # 1. Infrastructure
    worker_id = settings.effective_worker_id
    redis_client = RedisClient(settings.redis_url)
    
    from .services.brand_service import BrandService
    brand_service = BrandService(redis_client)
    
    import os
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = settings.mongo_url or os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongo_client = AsyncIOMotorClient(mongo_url)

    # 2. Services
    storage = ResultStorage(redis_client, worker_id, mongo_client=mongo_client)
    queue_consumer = QueueConsumer(redis_client, brand_service, worker_id)
    batch_processor = BatchProcessor(redis_client, brand_service)
    
    # 3. Domain Services
    spike_detector = SpikeDetector(brand_service, worker_id)
    
    # 4. Processor (DI)
    processor = ChunkProcessor(
        worker_id, 
        redis_client, 
        storage=storage,
        spike_detector=spike_detector
    )
    
    # 5. Queue Worker (Orchestrator)
    queue_worker_instance = QueueWorker(
        worker_id=worker_id,
        settings=settings,
        redis_client=redis_client,
        queue_consumer=queue_consumer,
        processor=processor,
        batch_processor=batch_processor,
        storage=storage
    )
    
    # Start Worker Loops via background task
    # We must start it as a task so lifespan completes
    worker_task = asyncio.create_task(queue_worker_instance.start())
    
    logger.info("Worker started.")
    
    yield
    
    logger.info("Stopping worker...")
    await queue_worker_instance.stop()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("Worker stopped.")


def create_app() -> FastAPI:
    app = FastAPI(title="Worker Service", lifespan=lifespan)
    app.include_router(health_router)

    @app.get("/metrics")
    async def metrics_view() -> Response:
        payload = generate_latest()
        return Response(content=payload, media_type=CONTENT_TYPE_LATEST)

    from pydantic import BaseModel

    class SuggestionRequest(BaseModel):
        brand: str
        text: str
        sentiment: str = "neutral"

    @app.post("/v1/suggestion")
    async def generate_suggestion_endpoint(req: SuggestionRequest):
        if not queue_worker_instance or not queue_worker_instance._processor:
            return Response(status_code=503)
        suggestions = await queue_worker_instance._processor.generate_suggestion(req.brand, req.text, req.sentiment)
        return {"suggestions": suggestions}

    @app.post("/v1/retry/{brand}")
    async def retry_failed_endpoint(brand: str):
        if not queue_worker_instance or not queue_worker_instance._queue_consumer:
            return Response(status_code=503)
        
        count = await queue_worker_instance._queue_consumer.retry_failed(brand)
        return {"status": "ok", "retried": count, "brand": brand}

    return app


def run() -> None:
    """Entry point for running via script (retains backward compatibility if needed)."""
    import uvicorn
    settings = get_settings()
    uvicorn.run("src.worker.app:app", host=settings.http_host, port=settings.http_port, reload=False)


if __name__ == "__main__":
    run()

# Export for uvicorn
app = create_app()
