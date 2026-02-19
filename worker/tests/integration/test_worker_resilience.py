
import unittest
from unittest.mock import MagicMock, AsyncMock
import sys
import os
import logging
from datetime import datetime
import numpy as np

# Adjust path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from worker.processor import ChunkProcessor
from worker.domain_types import Chunk, Mention
from worker.llm_adapter import InstrumentedLLMAdapter, LangChainLLMAdapter
from worker.storage import ResultStorage
from worker.embeddings import InstrumentedEmbeddingAdapter
import worker.llm_adapter

class TestWorkerResilience(unittest.IsolatedAsyncioTestCase):
    """
    Integration tests for Worker resilience.
    Verifies that the worker handles LLM failures gracefully using fallback mechanisms.
    Uses REAL worker components with MOCKED external I/O (LLM/Redis).
    """

    async def asyncSetUp(self):
        # 1. Mock Low-Level LLM Invocation Functions
        # Force exceptions to simulate total API failure
        worker.llm_adapter.invoke_sentiment = AsyncMock(side_effect=Exception("Simulated LLM Timeout"))
        worker.llm_adapter.invoke_strategic = AsyncMock(side_effect=Exception("Simulated 500 Error"))
        worker.llm_adapter.invoke_competitor_analysis = AsyncMock(side_effect=Exception("Simulated Failure"))
        worker.llm_adapter.invoke_general = AsyncMock(side_effect=Exception("Simulated Failure"))
        worker.llm_adapter.invoke_response_suggestion = AsyncMock(side_effect=Exception("Simulated Failure"))

        # 2. Setup Real Adapters
        # We use the real InstrumentedLLMAdapter to ensure fallback logic (try/except) is executed
        self.real_langchain_adapter = LangChainLLMAdapter(
            primary=None, 
            fallback=None, 
            max_tokens=1000, 
            timeout=10, 
            worker_id="test-worker"
        )
        self.real_llm_adapter = InstrumentedLLMAdapter(self.real_langchain_adapter)

        # 3. Mock Storage & Embeddings
        self.mock_storage = MagicMock(spec=ResultStorage)
        self.mock_storage.push_mention_stats = AsyncMock()
        self.mock_storage.update_brand_summary = AsyncMock()
        self.mock_storage.store_processed_chunk = AsyncMock()

        self.mock_embeddings = MagicMock(spec=InstrumentedEmbeddingAdapter)
        self.mock_embeddings.embed.return_value = np.zeros((3, 768)) # Valid numpy array

        # 4. Mock Redis
        self.mock_redis = MagicMock()
        self.mock_redis.get_spike_history = AsyncMock(return_value=[])
        self.mock_redis.record_spike_check = AsyncMock()
        self.mock_redis.append_spike_history = AsyncMock()
        self.mock_redis.publish = AsyncMock()
        self.mock_redis.get = AsyncMock()
        self.mock_redis.set = AsyncMock()

        # 5. Initialize Processor with Real Adapter
        self.processor = ChunkProcessor(
            worker_id="test-worker",
            redis_client=self.mock_redis,
            storage=self.mock_storage
        )
        
        # Monkeypatch internals to inject our Real Adapter + Mocks
        self.processor._llm_adapter = self.real_llm_adapter
        self.processor._embedding_adapter = self.mock_embeddings
        if hasattr(self.processor, "_analyzer"):
            self.processor._analyzer._llm = self.real_llm_adapter

    async def test_fallback_logic_emotion_detection(self):
        """test_fallback_logic_emotion_detection
        
        Scenario: LLM APIs are down.
        Input: Mentions with specific keywords ("terrified", "wow").
        Expected: 
          - Processor does not crash.
          - Regex/Keyword fallback detects correct emotions (Fear, Surprise).
          - Data is persisted to Redis.
        """
        now = datetime.now()
        chunk = Chunk(
            brand="test-brand",
            chunkId="chk-integration-1",
            createdAt=now,
            mentions=[
                Mention(text="I am terrified about this security breach! Unsafe!", source="twitter", id="m1", created_at=now),
                Mention(text="Wow! Surprisingly good results. OMG.", source="reddit", id="m2", created_at=now),
                Mention(text="Just a random comment about the weather.", source="web", id="m3", created_at=now)
            ]
        )

        # Execute
        result = await self.processor.process_chunk(chunk, envelope={"id": "dummy"}, fetch_time_ms=10.0)

        # Assertions
        self.assertIsNotNone(result, "Processor returned None")
        
        # Verify Emotions (Fallback Logic)
        cluster = result.clusters[0]
        emotions = cluster.enhanced_analysis.emotions
        
        # "terrified" -> Fear
        self.assertGreater(emotions.fear, 0, f"Expected Fear > 0, got {emotions.fear}")
        
        # "Wow" -> Surprise
        self.assertGreater(emotions.surprise, 0, f"Expected Surprise > 0, got {emotions.surprise}")
        
        # Verify Persistence
        self.assertEqual(self.mock_storage.push_mention_stats.call_count, 1, "Expected 1 batch push to storage")
        
        # Verify call data
        call_args = self.mock_storage.push_mention_stats.call_args[0]
        batch_mentions = call_args[1] # (brand, mentions)
        self.assertEqual(len(batch_mentions), 3)

if __name__ == "__main__":
    unittest.main()
