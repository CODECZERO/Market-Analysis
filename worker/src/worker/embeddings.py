"""Embeddings provider with instrumentation."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np

from .config import get_settings
from .logger import get_logger, log_with_context
from .metrics import worker_embedding_time_seconds

logger = get_logger(__name__)

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    SentenceTransformer = None  # type: ignore

try:
    from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
except ImportError:
    NVIDIAEmbeddings = None


class EmbeddingAdapter(ABC):
    """Abstract embedding adapter interface."""

    @abstractmethod
    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        raise NotImplementedError


class LocalEmbeddingAdapter(EmbeddingAdapter):
    """Embedding adapter using a local sentence-transformers model with graceful fallback."""

    _model: SentenceTransformer | None = None

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", fallback_dim: int = 384) -> None:
        self._model_name = model_name
        self._dim = fallback_dim
        self._use_fallback = SentenceTransformer is None
        if self._use_fallback:
            log_with_context(
                logger,
                level=logging.WARNING,
                message="sentence-transformers not installed, using hash-based embedding fallback",
                context={"model": model_name},
            )

    async def _load_model(self) -> SentenceTransformer | None:
        if self._use_fallback:
            return None
        if self._model is None:
            loop = asyncio.get_running_loop()
            self._model = await loop.run_in_executor(None, SentenceTransformer, self._model_name)
        return self._model

    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        if self._use_fallback:
            return self._hash_embed(texts)
        model = await self._load_model()
        assert model is not None  # for mypy
        loop = asyncio.get_running_loop()
        func = lambda: model.encode(list(texts), show_progress_bar=False, convert_to_numpy=True)
        return await loop.run_in_executor(None, func)

    def _hash_embed(self, texts: Sequence[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self._dim), dtype=float)
        for idx, text in enumerate(texts):
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            repeat_factor = (self._dim + len(digest) - 1) // len(digest)
            repeated = (digest * repeat_factor)[: self._dim]
            vectors[idx] = np.frombuffer(repeated, dtype=np.uint8) / 255.0
        return vectors



class GeminiEmbeddingAdapter(EmbeddingAdapter):
    """Embedding adapter using Google's Gemini API."""

    def __init__(self, api_key: str, model: str = "models/text-embedding-004") -> None:
        self._api_key = api_key
        self._model = model

    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        if not texts:
            return np.array([])

        # Batching is handled by caller (processor) usually, but we ensure safety here
        # Gemini API limits: check documentation (usually 100 per batch or similar)
        # We will iterate if needed, but processor sends chunks of ~10-20 mentions usually.
        
        
        import aiohttp
        
        url = f"https://generativelanguage.googleapis.com/v1beta/{self._model}:batchEmbedContents?key={self._api_key}"
        
        requests_payload = {
            "requests": [
                {
                    "model": self._model,
                    "content": {"parts": [{"text": text}]}
                } for text in texts
            ]
        }
        
        logger.info(f"Sending embeddings request to Gemini: {len(texts)} texts, model={self._model}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=requests_payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    log_with_context(
                        logger,
                        logging.ERROR,
                        "Gemini Embeddings API failed",
                        context={"status": response.status, "error": error_text, "brand": brand}
                    )
                    # Fallback to zeros to prevent crash
                    return np.zeros((len(texts), 768))

                data = await response.json()
                
                embeddings = []
                for entry in data.get("embeddings", []):
                     if "values" in entry:
                         embeddings.append(entry["values"])
                     else:
                         # Handle missing values failure case
                         embeddings.append([0.0] * 768)

                # Ensure we match input length (API might drop failed ones?)
                # Gemini batch response order matches request order.
                if len(embeddings) != len(texts):
                     logger.warning(f"Gemini returned {len(embeddings)} embeddings for {len(texts)} texts. Padding with zeros.")
                     while len(embeddings) < len(texts):
                         embeddings.append([0.0] * 768)
                
                return np.array(embeddings)




class InstrumentedEmbeddingAdapter(EmbeddingAdapter):
    """Wraps an embedding adapter to emit metrics and structured logs."""

    def __init__(self, delegate: EmbeddingAdapter, worker_id: str) -> None:
        self._delegate = delegate
        self._worker_id = worker_id

    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        start = time.perf_counter()
        embeddings = await self._delegate.embed(texts, brand=brand, chunk_id=chunk_id)
        duration = time.perf_counter() - start
        worker_embedding_time_seconds.labels(self._worker_id, brand).observe(duration)
        log_with_context(
            logger,
            level=logging.INFO,
            message="Embeddings generated",
            context={
                "worker_id": self._worker_id,
                "brand": brand,
                "chunk_id": chunk_id,
                "texts": len(texts),
            },
            metrics={"embedding_time_ms": duration * 1000},
        )
        return embeddings


class OllamaEmbeddingAdapter(EmbeddingAdapter):
    """Embedding adapter using local/remote Ollama instance."""

    def __init__(self, base_url: str, model: str = "llama3.2") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        if not texts:
            return np.array([])

        import aiohttp
        
        # Ollama /api/embeddings endpoint (one text at a time usually, checking docs)
        # Ollama API v0.1.30 supports /api/embeddings.
        # It takes {"model": "name", "prompt": "text"}. Returns {"embedding": [...]}.
        # It does NOT support batching by default in all versions, so we loop or check concurrency.
        # For safety and compatibility, we execute concurrently.
        
        url = f"{self._base_url}/api/embeddings"
        
        async def fetch_one(session, text):
            try:
                async with session.post(url, json={"model": self._model, "prompt": text}) as response:
                    if response.status != 200:
                        logger.error(f"Ollama embedding failed: {response.status}")
                        return [0.0] * 768 # Fallback size? Llama embeddings might be 4096 or 768. 
                        # We should ideally know the dimension. Llama 3 is usually 4096. 
                        # mxbai-embed-large is 1024. 
                        # We'll just return zeros and let numpy handle the shape mismatch if it happens,
                        # or better, force list and convert at the end.
                    data = await response.json()
                    return data.get("embedding", [])
            except Exception as e:
                logger.error(f"Ollama connection error: {e}")
                return []

        embeddings = []
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_one(session, text) for text in texts]
            results = await asyncio.gather(*tasks)
            embeddings = results

        # Determine dimensions from first successful result
        dim = 768
        for emb in embeddings:
            if emb and len(emb) > 0:
                dim = len(emb)
                break
        
        # Pad failures
        final_embeddings = []
        for emb in embeddings:
            if not emb:
                final_embeddings.append([0.0] * dim)
            else:
                final_embeddings.append(emb)

        return np.array(final_embeddings)


class NVIDIAEmbeddingAdapter(EmbeddingAdapter):
    """Embedding adapter using NVIDIA AI Endpoints with Ollama fallback."""

    def __init__(self, api_key: str, model: str = "nvidia/nv-embed-v1", fallback_adapter: EmbeddingAdapter | None = None) -> None:
        self._api_key = api_key
        self._model = model
        self._fallback = fallback_adapter
        if NVIDIAEmbeddings:
            self._client = NVIDIAEmbeddings(
                model=self._model, 
                api_key=self._api_key, 
                base_url="https://integrate.api.nvidia.com/v1",
                truncate="END"
            )
        else:
            self._client = None
            logger.warning("langchain_nvidia_ai_endpoints not installed, will force fallback")

    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        if not texts:
            return np.array([])
            
        try:
            if not self._client:
                raise ImportError("NVIDIA client not initialized")
            
            # NVIDIA Embeddings (Synchronous call usually in langchain, so run in executor)
            loop = asyncio.get_running_loop()
            embeddings = await loop.run_in_executor(None, self._client.embed_documents, list(texts))
            return np.array(embeddings)
            
        except Exception as e:
            logger.warning(f"NVIDIA embeddings failed: {e}. Switching to fallback.")
            if self._fallback:
                 return await self._fallback.embed(texts, brand=brand, chunk_id=chunk_id)
            else:
                 logger.error("No fallback available for embeddings.")
                 return np.zeros((len(texts), 1024)) # Default to zeros if no fallback

class RemoteEmbeddingAdapter(EmbeddingAdapter):
    """Fallback/Mock adapter for when configured provider is unavailable."""

    def __init__(self, provider_name: str) -> None:
        self._provider_name = provider_name
        logger.warning(f"Using RemoteEmbeddingAdapter (Mock) for provider: {provider_name}")

    async def embed(self, texts: Sequence[str], *, brand: str, chunk_id: str) -> np.ndarray:
        if not texts:
            return np.array([])
        
        # Return random or zero embeddings to prevent crash
        # Zeros are safer as they won't create artificial clusters
        return np.zeros((len(texts), 768))


def get_embedding_adapter(worker_id: str) -> InstrumentedEmbeddingAdapter:
    settings = get_settings()
    provider = settings.embeddings_provider

    if provider == "local":
        delegate: EmbeddingAdapter = LocalEmbeddingAdapter()
    elif provider == "gemini":
        if not settings.gemini_api_key:
             logger.warning("Gemini API key missing, falling back to local/zeros")
             delegate = RemoteEmbeddingAdapter("missing_gemini_key")
        else:
             delegate = GeminiEmbeddingAdapter(settings.gemini_api_key, model=settings.gemini_model)
    elif provider == "ollama":
        delegate = OllamaEmbeddingAdapter(settings.ollama_base_url, model=settings.ollama_model)
    elif provider == "nvidia":
        # Create fallback first
        fallback = OllamaEmbeddingAdapter(settings.ollama_base_url, model=settings.ollama_model)
        delegate = NVIDIAEmbeddingAdapter(
            api_key=settings.nvidia_api_key or "",
            model="nvidia/nv-embed-v1", # Reliable general purpose model
            fallback_adapter=fallback
        )
    else:
        delegate = RemoteEmbeddingAdapter(provider)

    return InstrumentedEmbeddingAdapter(delegate, worker_id)
