
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os
import logging
from datetime import datetime, timezone
import numpy as np
import json

# Adjust path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from worker.processor import ChunkProcessor
from worker.domain_types import Chunk, Mention, Emotions
from worker.llm_adapter import InstrumentedLLMAdapter, LangChainLLMAdapter
from worker.storage import ResultStorage
from worker.embeddings import InstrumentedEmbeddingAdapter
import worker.llm_adapter

# Configure verbose logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AdvancedIntegrationTest")

class TestWorkerAdvanced(unittest.IsolatedAsyncioTestCase):
    """
    Advanced Integration Tests for Brand Reputation Worker.
    Covers:
    1. Happy Path (Full Success Pipeline)
    2. Money Mode (Commercial Intent Detection)
    3. Resilience (Fallback Logic)
    """

    async def asyncSetUp(self):

        


        # 1. Manual Monkeypatching of worker.llm_adapter imports
        # This is more reliable than 'patch' strings given complex imports
        self.original_funcs = {
            'invoke_sentiment': worker.llm_adapter.invoke_sentiment,
            'invoke_general': worker.llm_adapter.invoke_general,
            'invoke_strategic': worker.llm_adapter.invoke_strategic,
            'invoke_competitor_analysis': worker.llm_adapter.invoke_competitor_analysis,
            'invoke_response_suggestion': worker.llm_adapter.invoke_response_suggestion,
            'invoke_commercial_intent': getattr(worker.llm_adapter, 'invoke_commercial_intent', None) # Might not exist if not imported
        }
        
        # Create Mocks - valid for all tests, side_effects customized per test
        self.mock_invoke_sentiment = AsyncMock()
        self.mock_invoke_general = AsyncMock()
        self.mock_invoke_strategic = AsyncMock()
        self.mock_invoke_competitor = AsyncMock()
        self.mock_invoke_response = AsyncMock()
        
        # Apply Mocks
        worker.llm_adapter.invoke_sentiment = self.mock_invoke_sentiment
        worker.llm_adapter.invoke_general = self.mock_invoke_general
        worker.llm_adapter.invoke_strategic = self.mock_invoke_strategic
        worker.llm_adapter.invoke_competitor_analysis = self.mock_invoke_competitor
        worker.llm_adapter.invoke_response_suggestion = self.mock_invoke_response
        
        # 2. Setup Real Adapters
        self.real_langchain_adapter = LangChainLLMAdapter(
            primary=None,fallback=None, max_tokens=1000, timeout=10, worker_id="test-worker"
        )
        self.real_llm_adapter = InstrumentedLLMAdapter(self.real_langchain_adapter)

        # 3. Mock Storage
        self.mock_storage = MagicMock(spec=ResultStorage)
        self.mock_storage.push_mention_stats = AsyncMock()
        self.mock_storage.update_brand_summary = AsyncMock()
        self.mock_storage.store_processed_chunk = AsyncMock()

        # 4. Mock Embeddings (Success by default)
        self.mock_embeddings = MagicMock(spec=InstrumentedEmbeddingAdapter)
        def embed_side_effect(texts, **kwargs):
            return np.random.rand(len(texts), 768)
        self.mock_embeddings.embed.side_effect = embed_side_effect
        
        # Patch ChatNVIDIA to prevent network init if possible (still good practice)
        patcher = patch('langchain_nvidia_ai_endpoints.ChatNVIDIA')
        self.mock_chat = patcher.start()
        self.addCleanup(patcher.stop)

        # 5. Mock Redis
        self.mock_redis = MagicMock()
        self.mock_redis.get_spike_history = AsyncMock(return_value=[])
        self.mock_redis.record_spike_check = AsyncMock()
        self.mock_redis.append_spike_history = AsyncMock()
        self.mock_redis.publish = AsyncMock()
        self.mock_redis.get = AsyncMock()
        self.mock_redis.set = AsyncMock()

        # 6. Initialize Processor
        self.processor = ChunkProcessor(
            worker_id="test-worker",
            redis_client=self.mock_redis,
            storage=self.mock_storage
        )
        
        # Monkeypatch internals
        self.processor._llm_adapter = self.real_llm_adapter
        self.processor._embedding_adapter = self.mock_embeddings
        if hasattr(self.processor, "_analyzer"):
            self.processor._analyzer._llm = self.real_llm_adapter

    async def asyncTearDown(self):
        # Restore original functions
        worker.llm_adapter.invoke_sentiment = self.original_funcs['invoke_sentiment']
        worker.llm_adapter.invoke_general = self.original_funcs['invoke_general']
        worker.llm_adapter.invoke_strategic = self.original_funcs['invoke_strategic']
        worker.llm_adapter.invoke_competitor_analysis = self.original_funcs['invoke_competitor_analysis']
        worker.llm_adapter.invoke_response_suggestion = self.original_funcs['invoke_response_suggestion']


    async def test_happy_path_full_pipeline(self):
        """
        HAPPY PATH: Verify the worker correctly processes a chunk when LLM returns VALID data.
        """
        print("Testing Happy Path: Full Processing with valid LLM responses...")

        # Configure Mock Returns
        self.mock_invoke_sentiment.return_value = {"positive": 0.9, "neutral": 0.1, "negative": 0.0}
        
        enhanced_json = {
            "sentiment_score": 0.9,
            "sentiment_label": "positive",
            "emotions": {"joy": 0.9, "surprise": 0.5},
            "topics": ["performance", "speed"],
            "is_sarcastic": False,
            "urgency": "low",
            "entities": {"people": ["Elon"], "companies": ["Tesla"], "products": ["Model 3"]}
        }
        
        async def general_side_effect(*args, **kwargs):
            operation = kwargs.get('operation')
            if not operation and len(args) >= 5:
                    operation = args[4]

            if operation == 'enhanced_analysis':
                return enhanced_json
            elif operation == 'summary':
                return "This is a concise summary."
            elif operation == "commercial_intent":
                return {"sales_intent": False, "confidence": 0.1, "intent_type": "none"}
            return {}
        
        self.mock_invoke_general.side_effect = general_side_effect
        
        self.mock_invoke_strategic.return_value = {
            "relevant": True, 
            "strategic_tag": "BRAND_AMBASSADOR", 
            "confidence": 0.95,
            "summary": "User loves the product."
        }

        # Input Data
        now = datetime.now(timezone.utc)
        chunk = Chunk(
            brand="tesla",
            chunkId="chk-happy-1",
            createdAt=now,
            mentions=[
                Mention(text="I absolutely love the new acceleration update! It's mind-blowing.", source="twitter", id="m1", created_at=now),
                Mention(text="The speed is incredible compared to the competition.", source="reddit", id="m2", created_at=now)
            ]
        )

        # Execute
        result = await self.processor.process_chunk(chunk, envelope={"id": "evt-1"}, fetch_time_ms=15.0)

        # Assertions
        self.assertIsNotNone(result)
        cluster = result.clusters[0]
        
        print(f"   Cluster Summary: {cluster.summary}")
        print(f"   Emotions: {cluster.enhanced_analysis.emotions}")
        
        self.assertGreater(cluster.enhanced_analysis.emotions.joy, 0.8)
        self.assertIn("performance", cluster.enhanced_analysis.topics)
        self.assertEqual(cluster.sentiment['positive'], 0.9)
        self.mock_storage.push_mention_stats.assert_called_once()
        print("Happy Path Verified!")

    async def test_money_mode_commercial_intent(self):
        """
        MONEY MODE: Verify detection of High Commercial Intent (Hot Leads).
        """
        print("\nTesting Money Mode: Commercial Intent Detection...")

        self.mock_invoke_sentiment.return_value = {"positive": 0.1, "neutral": 0.8, "negative": 0.1}
        self.mock_invoke_strategic.return_value = {"relevant": True, "strategic_tag": "OPPORTUNITY_TO_STEAL", "confidence": 0.9}

        async def intent_side_effect(*args, **kwargs):
            operation = kwargs.get('operation')
            if not operation and len(args) >= 5:
                    operation = args[4]
            
            if operation == 'commercial_intent':
                return {
                    "sales_intent": True,
                    "confidence": 0.98,
                    "intent_type": "comparison_shopping",
                    "pain_point": "pricing"
                }
            if operation == 'enhanced_analysis':
                return {"emotions": {}, "topics": ["pricing"], "lead_score": 95}
            if operation == 'summary': return "User looking for pricing."
            return {}
        
        self.mock_invoke_general.side_effect = intent_side_effect

        now = datetime.now(timezone.utc)
        chunk = Chunk(
            brand="saas-tool", 
            chunkId="chk-money-1", 
            createdAt=now,
            mentions=[
                Mention(text="Looking for an alternative to Jira that is cheaper. Ready to buy now.", source="linkedin", id="lead1", created_at=now),
                Mention(text="I need a better project management tool.", source="twitter", id="lead2", created_at=now)
            ]
        )

        # Force Clustering Success (Mock Clusterer)
        # Random embeddings often result in noise (no clusters) for DBSCAN
        from worker.clustering import ClusteringOutput, ClusterGrouping
        mock_cluster_output = ClusteringOutput(
            clusters=[
                ClusterGrouping(
                    cluster_id=0,
                    indices=[0, 1], # Both mentions in one cluster
                    method="mock"
                )
            ],
            method="mock",
            duration_ms=0.0
        )
        self.processor._clusterer = MagicMock()
        self.processor._clusterer.cluster = AsyncMock(return_value=mock_cluster_output)

        # Execute
        await self.processor.process_chunk(chunk, envelope={"id": "evt-2"}, fetch_time_ms=10.0)

        # Assertions
        self.mock_storage.push_mention_stats.assert_called_once()
        call_args = self.mock_storage.push_mention_stats.call_args[0]
        mentions_stored = call_args[1]
        lead_mention = mentions_stored[0]
        
        print(f"   Lead Analysis: Intent={lead_mention.get('intent')} Tag={lead_mention.get('strategic_tag')}")
        
        # Verify Strategic Tag is populated (from our mock return)
        self.assertEqual(lead_mention.get('strategic_tag'), "OPPORTUNITY_TO_STEAL")
        
        # NEW: Verify push_leads was called
        # This confirms the data flow to the "Money Feed" frontend
        self.mock_storage.push_leads.assert_called_once()
        print("   push_leads called (Money Feed connected)")
        
        print("Money Mode Verified!")

    async def test_resilience_fallback_mode(self):
        """
        RESILIENCE: Verify Fallback logic when ALL LLM calls fail.
        Expected: Regex fallbacks for Sentiment, Emotion, and Intent.
        """
        print("\nTesting Resilience: Total System Failure Fallback...")
        
        # Force Exceptions on ALL invokes
        self.mock_invoke_sentiment.side_effect = Exception("Timeout")
        self.mock_invoke_general.side_effect = Exception("500 Error")
        self.mock_invoke_strategic.side_effect = Exception("API Down")
        
        now = datetime.now(timezone.utc)
        chunk = Chunk(
            brand="resilience-test",
            chunkId="chk-fail-1",
            createdAt=now,
            mentions=[
                Mention(text="Simply amazing! I am so happy with this.", source="twitter", id="m1", created_at=now), # Should be joy/positive
                Mention(text="I hate this garbage. It's broken.", source="reddit", id="m2", created_at=now) # Should be anger/negative
            ]
        )

        result = await self.processor.process_chunk(chunk, envelope={"id": "evt-3"}, fetch_time_ms=10.0)
        
        self.assertIsNotNone(result)
        cluster = result.clusters[0]
        
        # Verify Fallback Emotions (Regex based)
        emotions = cluster.enhanced_analysis.emotions
        print(f"   Fallback Emotions: {emotions}")
        
        self.assertGreater(emotions.joy, 0.0, "Fallback failed to detect Joy")
        print("Resilience Verified!")

    async def test_crisis_scenario(self):
        """
        CRISIS: Verify Crisis Detection triggers on keywords + negative sentiment.
        """
        print("\nTesting Crisis Scenario...")
        
        # MOCK CLUSTERER to ensure we have a cluster to analyze
        from worker.clustering import ClusteringOutput, ClusterGrouping
        mock_cluster_output = ClusteringOutput(
            clusters=[ClusterGrouping(cluster_id=0, indices=[0, 1], method="mock")],
            method="mock", duration_ms=0.0
        )
        self.processor._clusterer = MagicMock()
        self.processor._clusterer.cluster = AsyncMock(return_value=mock_cluster_output)
        
        # Mock LLM Logic
        async def crisis_side_effect(*args, **kwargs):
            operation = kwargs.get('operation')
            if not operation and len(args) >= 5:
                    operation = args[4]
            
            if operation == 'enhanced_analysis':
                return {
                    "sentiment_score": -0.9,
                    "sentiment_label": "negative",
                    "emotions": {"anger": 0.9, "fear": 0.8},
                    "urgency": "high",
                    "topics": ["security", "breach"],
                    "entities": {}
                }
            if operation == 'summary': return "Data breach reported."
            if operation == 'sentiment': return {"positive": 0.0, "neutral": 0.1, "negative": 0.9}
            return {}
            
        self.mock_invoke_general.side_effect = crisis_side_effect
        self.mock_invoke_sentiment.return_value = {"positive": 0.0, "neutral": 0.1, "negative": 0.9}
        self.mock_invoke_strategic.return_value = {
            "relevant": True, 
            "gatekeeper_category": "general", 
            "confidence": 0.99,
            "strategic_tag": "CRITICAL_ALERT"
        }
        
        now = datetime.now(timezone.utc)
        chunk = Chunk(
            brand="crisis-brand",
            chunkId="chk-crisis-1",
            createdAt=now,
            mentions=[
                Mention(text="Massive data breach! Millions exposed!", source="twitter", id="c1", created_at=now),
                Mention(text="I am furious about this hack.", source="reddit", id="c2", created_at=now)
            ]
        )
        
        # Mock storage.push_crisis_event to verify it's called
        self.mock_storage.push_crisis_event = AsyncMock()
        
        await self.processor.process_chunk(chunk, envelope={"id": "evt-crisis"}, fetch_time_ms=10.0)
        
        # Assertions
        self.mock_storage.push_crisis_event.assert_called_once()
        call_args = self.mock_storage.push_crisis_event.call_args[0]
        event = call_args[1]
        
        print(f"   Crisis Event Severity: {event.get('severity')}")
        self.assertEqual(event.get('severity'), 'critical')
        print("Crisis Scenario Verified!")

    async def test_spike_handling(self):
        """
        SPIKE: Verify Spike Detection flags the chunk.
        """
        print("\nTesting Spike Handling...")
        
        # MOCK CLUSTERER
        from worker.clustering import ClusteringOutput, ClusterGrouping
        mock_cluster_output = ClusteringOutput(
            clusters=[ClusterGrouping(cluster_id=0, indices=[0], method="mock")],
            method="mock", duration_ms=0.0
        )
        self.processor._clusterer = MagicMock()
        self.processor._clusterer.cluster = AsyncMock(return_value=mock_cluster_output)

        # Mock SpikeDetector to return True
        from worker.spike_detector import SpikeResult
        self.processor._spike_detector.detect = AsyncMock(return_value=SpikeResult(
            is_spike=True,
            historical_average=5.0,
            current_count=50
        ))
        
        # MOCK LLM (Validation Fix)
        # Without this, EnhancedAnalysis fails validation on MagicMock inputs
        self.mock_invoke_sentiment.return_value = {"positive": 0.5, "neutral": 0.5, "negative": 0.0}
        self.mock_invoke_strategic.return_value = {"relevant": True, "gatekeeper_category": "valid", "confidence": 0.9}
        async def dummy_general(*args, **kwargs):
            operation = kwargs.get('operation')
            if not operation and len(args) >= 5: operation = args[4]
            if operation == 'enhanced_analysis': return {"topics": ["viral"]}
            if operation == 'summary': return "Viral summary."
            return {}
        self.mock_invoke_general.side_effect = dummy_general
        
        # Standard input
        now = datetime.now(timezone.utc)
        chunk = Chunk(
            brand="spike-brand",
            chunkId="chk-spike-1",
            createdAt=now,
            mentions=[Mention(text="Viral post!", source="twitter", id="s1", created_at=now)]
        )
        
        await self.processor.process_chunk(chunk, envelope={"id": "evt-spike"}, fetch_time_ms=10.0)
        
        # Verify persistence of spike status
        # update_brand_summary(brand, result, ...) matches signature
        # result is ChunkResult
        self.mock_storage.update_brand_summary.assert_called()
        chunk_result = self.mock_storage.update_brand_summary.call_args[0][1]
        
        print(f"   Spike Detected: {chunk_result.spikeDetected}")
        self.assertTrue(chunk_result.spikeDetected)
        print("Spike Handling Verified!")

if __name__ == "__main__":
    unittest.main(verbosity=2)
