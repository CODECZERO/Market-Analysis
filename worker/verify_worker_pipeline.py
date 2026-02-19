
import asyncio
import sys
import os
import logging
from unittest.mock import MagicMock, AsyncMock

# Setup path
sys.path.append(os.path.join(os.getcwd(), "src"))

# Import worker modules
from worker.processor import ChunkProcessor
from worker.domain_types import Chunk, Mention
from worker.llm_adapter import InstrumentedLLMAdapter, LangChainLLMAdapter
from worker.storage import ResultStorage
from worker.embeddings import InstrumentedEmbeddingAdapter
from datetime import datetime

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ValidatonTest")

async def test_worker_fallback_pipeline():
    print("\nStarting Worker Pipeline Test (LLM Failure Simulation)\n")

    # 1. Mock Dependencies
    import worker.llm_adapter
    
    # Mock low-level invoke functions to force exceptions inside the real adapter logic
    worker.llm_adapter.invoke_sentiment = AsyncMock(side_effect=Exception("Simulated LLM Timeout"))
    worker.llm_adapter.invoke_strategic = AsyncMock(side_effect=Exception("Simulated 500 Error"))
    worker.llm_adapter.invoke_competitor_analysis = AsyncMock(side_effect=Exception("Simulated Failure"))
    worker.llm_adapter.invoke_general = AsyncMock(side_effect=Exception("Simulated Failure"))
    worker.llm_adapter.invoke_response_suggestion = AsyncMock(side_effect=Exception("Simulated Failure"))
    # Note: invoke_general is used by summarize, analyze_enhanced, and analyze_commercial_intent
    
    # Use REAL adapters
    real_langchain_adapter = LangChainLLMAdapter(
        primary=None, 
        fallback=None, 
        max_tokens=1000, 
        timeout=10, 
        worker_id="test-worker"
    )
    real_llm_adapter = InstrumentedLLMAdapter(real_langchain_adapter)

    mock_storage = MagicMock(spec=ResultStorage)
    # ... (rest of storage mocks)
    mock_storage.push_mention_stats = AsyncMock()
    mock_storage.update_brand_summary = AsyncMock()
    mock_storage.store_processed_chunk = AsyncMock()

    mock_embeddings = MagicMock(spec=InstrumentedEmbeddingAdapter)
    # Embeddings must be numpy array
    mock_embeddings.embed.return_value = np.zeros((3, 768))
    
    # Mock Redis client (needed for initialization)
    mock_redis = MagicMock()
    mock_redis.get_spike_history = AsyncMock(return_value=[])
    mock_redis.record_spike_check = AsyncMock()
    mock_redis.append_spike_history = AsyncMock()
    mock_redis.publish = AsyncMock()
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()

    # 2. Initialize Processor

    # 2. Initialize Processor
    # Dependencies are created internally, so we must monkeypatch them
    processor = ChunkProcessor(
        worker_id="test-worker",
        redis_client=mock_redis,
        storage=mock_storage
    )
    
    # Monkeypatch internals
    processor._llm_adapter = real_llm_adapter
    processor._embedding_adapter = mock_embeddings
    
    # Monkeypatch Analyzer's LLM as well (since Analyzer is what calls proper LLM methods)
    if hasattr(processor, "_analyzer"):
        processor._analyzer._llm = real_llm_adapter

    # 3. Create Test Data
    # specific_mention: Matches "pain" regex (hate, broken) -> Gatekeeper PAIN
    # general_mention: Matches nothing -> Gatekeeper NONE -> Should Pass via Fallback
    now = datetime.now()
    chunk = Chunk(
        brand="test-brand",
        chunkId="chk-123",
        createdAt=now,
        mentions=[
            Mention(text="I am terrified about this security breach! Unsafe!", source="twitter", id="m1", created_at=now),
            Mention(text="Wow! Surprisingly good results. OMG.", source="reddit", id="m2", created_at=now),
            Mention(text="Just a random comment about the weather.", source="web", id="m3", created_at=now)
        ]
    )

    print("Processing Chunk with 3 mentions...")
    result = await processor.process_chunk(chunk, envelope={"id": "dummy"}, fetch_time_ms=10.0)

    # 4. Assertions
    print("\nVerifying Results:")
    
    # Check if we got a result
    assert result is not None, "Processor returned None"
    print("Processor returned result")
    
    # Use internal stats to verify cluster analysis (which uses analyze_enhanced_fallback)
    # The first cluster should contain our mentions
    cluster = result.clusters[0]
    enhanced_analysis = cluster.enhanced_analysis
    
    print(f"   Cluster Analysis: Emotions={enhanced_analysis.emotions}")
    
    # Check specifically for FEAR (from m1) and SURPRISE (from m2)
    # Note: Mentions are clustered together, so cluster emotions should reflect mixed or dominant emotions
    # "terrified", "unsafe" -> Fear
    # "Wow", "Surprisingly", "OMG" -> Surprise
    
    assert enhanced_analysis.emotions.fear > 0, f"Expected FEAR > 0, got {enhanced_analysis.emotions.fear}"
    print(f"Detected FEAR ({enhanced_analysis.emotions.fear}) from 'terrified/security/unsafe'")
    
    assert enhanced_analysis.emotions.surprise > 0, f"Expected SURPRISE > 0, got {enhanced_analysis.emotions.surprise}"
    print(f"Detected SURPRISE ({enhanced_analysis.emotions.surprise}) from 'Wow/OMG'")

    # Verify Persistence
    call_count = mock_storage.push_mention_stats.call_count
    print(f"Storage.push_mention_stats called {call_count} times")
    assert call_count == 1, "Expected 1 batch call"

    print("\nALL TESTS PASSED! Fallback mechanisms are working correctly.")

if __name__ == "__main__":
    asyncio.run(test_worker_fallback_pipeline())
