"""LLM Client for handling provider initialization and execution."""
import asyncio
import logging
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser

from ..config import get_settings
from ..logger import get_logger, log_with_context
from .resilience import GlobalRateLimiter, CircuitBreaker, ConcurrencyTracker
from ..training_data_collector import TrainingDataCollector

logger = get_logger(__name__)

class LLMClient:
    """Handles LLM provider initialization, rate limiting, and execution."""
    
    _instance = None
    
    def __init__(self):
        self._chat_model = None
        self._embeddings_model = None
        self._concurrency_tracker = None
        self._rate_limiter = None
        self._circuit_breaker = None
        self._min_delay = 0.0
        self._parser = StrOutputParser()
        self._collector = None

    @classmethod
    def get_instance(cls) -> 'LLMClient':
        if cls._instance is None:
            cls._instance = LLMClient()
        return cls._instance

    def _ensure_clients(self):
        """Initialize chat and embeddings models with rate limiting."""
        if self._chat_model is not None and self._concurrency_tracker is not None:
             return

        settings = get_settings()
        
        # Initialize Training Data Collector
        if self._collector is None:
            self._collector = TrainingDataCollector(settings.effective_worker_id)
        
        # Initialize Chat Model
        if settings.llm_provider == "nvidia":
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            self._chat_model = ChatNVIDIA(
                model=settings.nvidia_model,
                api_key=settings.nvidia_api_key,
                base_url="https://integrate.api.nvidia.com/v1",
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
            )
        elif settings.llm_provider == "openrouter":
            if not settings.openrouter_api_key:
                logger.warning("OPENROUTER_API_KEY not set!")
            
            from langchain_openai import ChatOpenAI
            self._chat_model = ChatOpenAI(
                model=settings.openrouter_model,
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.2,
                max_tokens=1024,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Brand Reputation Tracker",
                }
            )
        else:
            # Default to Ollama
            try:
                from langchain_ollama import ChatOllama
                self._chat_model = ChatOllama(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_model,
                    temperature=0.3,
                )
            except ImportError:
                 from langchain_community.chat_models import ChatOllama
                 self._chat_model = ChatOllama(
                     base_url=settings.ollama_base_url,
                     model=settings.ollama_model,
                     temperature=0.3,
                 )
        
        # Initialize Embeddings
        emb_provider = getattr(settings, "embeddings_provider", "local")
        
        if settings.llm_provider == "nvidia" and emb_provider == "local":
             emb_provider = "nvidia"

        if emb_provider == "nvidia":
            from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
            self._embeddings_model = NVIDIAEmbeddings(
                model="nvidia/nv-embed-v1",
                api_key=settings.nvidia_api_key,
                truncate="END"
            )
        elif emb_provider == "openai" or emb_provider == "openrouter":
             from langchain_openai import OpenAIEmbeddings
             self._embeddings_model = OpenAIEmbeddings(
                 model="text-embedding-3-small", 
                 api_key=settings.openrouter_api_key or settings.nvidia_api_key
             )
        else:
            try:
                from langchain_ollama import OllamaEmbeddings
            except ImportError:
                from langchain_community.embeddings import OllamaEmbeddings
                
            self._embeddings_model = OllamaEmbeddings(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
            )

        self._concurrency_tracker = ConcurrencyTracker(settings.llm_max_concurrency)
        self._min_delay = max(0.0, settings.llm_min_delay_sec)
        
        self._rate_limiter = GlobalRateLimiter(limit_rpm=settings.llm_rate_limit_rpm)
        self._circuit_breaker = CircuitBreaker(threshold=5, cooldown_secs=30)
        
        log_with_context(
            logger,
            level=logging.INFO,
            message=f"Initialized LLM client",
            context={
                "provider": settings.llm_provider,
                "embeddings": emb_provider,
                "model": settings.nvidia_model if settings.llm_provider == "nvidia" else settings.ollama_model,
                "concurrency": settings.llm_max_concurrency
            },
        )

    async def execute(self, prompt_template, variables: Dict[str, Any], *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> Any:
        """Execute LLM prompt with rate limiting, circuit breaker, retry logic, and PROVIDER FALLBACK."""
        self._ensure_clients()
        settings = get_settings()
        
        primary_chat = self._chat_model
        if format_json:
            primary_chat = primary_chat.bind(format="json")
        
        chain = prompt_template | primary_chat | self._parser
        
        async def _run_attempt(target_chain):
            if self._rate_limiter:
                await self._rate_limiter.acquire()
                
            async with self._concurrency_tracker.acquire_slot() as slot_id:
                logger.info(f"[Thread {slot_id}] Starting LLM call ({operation})...")
                loop = asyncio.get_running_loop()
                def _invoke():
                    return target_chain.invoke(variables)
                return await asyncio.wait_for(loop.run_in_executor(None, _invoke), timeout=timeout)

        try:
            if self._circuit_breaker and await self._circuit_breaker.is_open():
                 logger.warning("Circuit breaker open for primary provider")
                 raise RuntimeError("Circuit breaker open")

            result = await _run_attempt(chain)
            
            # Record Training Data
            end_time = asyncio.get_running_loop().time()
            # We don't have start time here directly, but we can estimate or pass it. 
            # Actually, `_run_attempt` has the timing. Let's just use 0.0 or move recording inside logic if precise latency needed.
            # Simplified: capture what we have.
            if self._collector:
                # Need to convert result to JSON/Dict if it's a string that looks like JSON?
                # The collector takes Any.
                self._collector.collect(
                    input_text=prompt_template.invoke(variables).to_string() if hasattr(prompt_template, "invoke") else str(variables),
                    output_data=result,
                    brand=brand,
                    operation=operation,
                    model=settings.nvidia_model if settings.llm_provider == "nvidia" else settings.ollama_model,
                    latency_ms=0.0 # TODO: Pass actual latency
                )

            response_preview = str(result)[:150]
            logger.info(f"LLM Response ({operation}): '{response_preview}...'")
            return result
            
        except Exception as exc:
            import traceback
            logger.warning(f"Primary LLM ({settings.llm_provider}) failed: {exc}\nTraceback:\n{traceback.format_exc()}")
            
            fallbacks = []
            if settings.llm_provider == "nvidia":
                if settings.groq_api_key:
                    fallbacks.append("groq")
                fallbacks.append("ollama")
            elif settings.llm_provider == "openrouter":
                if settings.groq_api_key:
                    fallbacks.append("groq")
                fallbacks.append("ollama")
            
            for provider in fallbacks:
                logger.info(f"Attempting fallback to {provider}...")
                try:
                    fallback_chat = None
                    if provider == "groq":
                        try:
                            from langchain_groq import ChatGroq
                        except ImportError:
                            logger.error("langchain_groq not installed. Skipping Groq fallback.")
                            continue

                        fallback_chat = ChatGroq(
                            model=settings.groq_model,
                            api_key=settings.groq_api_key,
                            temperature=0.2,
                            max_tokens=512,
                        )
                    elif provider == "ollama":
                        try:
                            from langchain_ollama import ChatOllama
                        except ImportError:
                            from langchain_community.chat_models import ChatOllama
                            
                        fallback_chat = ChatOllama(
                            base_url=settings.ollama_base_url,
                            model=settings.ollama_model,
                            temperature=0.3,
                        )

                    if format_json and fallback_chat:
                        if provider == "groq":
                             fallback_chat = fallback_chat.bind(response_format={"type": "json_object"})
                        else:
                             fallback_chat = fallback_chat.bind(format="json")
                    
                    if fallback_chat:
                        fallback_chain = prompt_template | fallback_chat | self._parser
                        return await _run_attempt(fallback_chain)
                
                except Exception as fallback_exc:
                    logger.error(f"Fallback {provider} also failed: {fallback_exc}")
                    continue
            
            raise exc

    async def embed_query(self, text: str) -> list[float]:
        self._ensure_clients()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embeddings_model.embed_query, text)
