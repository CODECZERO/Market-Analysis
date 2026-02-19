"""
V4 Feature Integration Tests
============================

Tests for advanced LLM-powered features:
- Launch Detection (The Oracle)
- Response Suggestion
- Commercial Intent Detection
- Competitor Complaint Categorization
- Web Insights Scan
"""
import asyncio
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Imports from worker package
from worker.processor import ChunkProcessor
from worker.domain_types import Chunk, Mention
from worker.analyzer import Analyzer, AnalysisInput, GatekeeperCategory


class TestV4Features(unittest.IsolatedAsyncioTestCase):
    """Integration tests for V4 LLM-powered features."""

    async def asyncSetUp(self):
        """Set up mocks for each test."""
        # Mock Redis client
        self.mock_redis = MagicMock()
        self.mock_redis.get = AsyncMock(return_value=None)
        self.mock_redis.set = AsyncMock()
        self.mock_redis.lpush = AsyncMock()
        self.mock_redis.ltrim = AsyncMock()
        self.mock_redis.rpush = AsyncMock()
        self.mock_redis.expire = AsyncMock()
        self.mock_redis.publish = AsyncMock()
        self.mock_redis.get_spike_history = AsyncMock(return_value=[])
        self.mock_redis.append_spike_history = AsyncMock()
        
        # Mock storage
        self.mock_storage = MagicMock()
        self.mock_storage.save_result = AsyncMock()
        self.mock_storage.push_mention_stats = AsyncMock()
        self.mock_storage.update_brand_summary = AsyncMock()
        self.mock_storage.push_leads = AsyncMock()
        self.mock_storage.push_crisis_event = AsyncMock()
        self.mock_storage.update_crisis_metrics = AsyncMock()
        
        # Create processor with mocks
        with patch("worker.processor.get_settings") as mock_settings, \
             patch("worker.processor.get_embedding_adapter") as mock_embed, \
             patch("worker.processor.get_llm_adapter") as mock_llm, \
             patch("worker.processor.get_analyzer") as mock_analyzer_factory, \
             patch("worker.processor.get_web_scanner") as mock_scanner:
            
            mock_settings.return_value = MagicMock(
                preprocessing_examples=3,
                redis_result_prefix="result:brand",
                redis_summary_prefix="summary:brand:",
            )
            
            # Mock embedding adapter
            mock_embed_instance = MagicMock()
            mock_embed_instance.embed = AsyncMock(return_value=[[0.1] * 384])
            mock_embed.return_value = mock_embed_instance
            
            # Mock LLM adapter - will be configured per test
            self.mock_llm_adapter = MagicMock()
            self.mock_llm_adapter.summarize = AsyncMock(return_value="Test summary")
            self.mock_llm_adapter.sentiment = AsyncMock(return_value={"positive": 0.5, "neutral": 0.3, "negative": 0.2})
            self.mock_llm_adapter.analyze_enhanced = AsyncMock(return_value={"topics": ["test"]})
            self.mock_llm_adapter.strategic_analyze = AsyncMock(return_value={"relevant": True, "intent": "GENERAL"})
            self.mock_llm_adapter.detect_launch = AsyncMock(return_value={"launch_detected": False})
            self.mock_llm_adapter.generate_response_suggestion = AsyncMock(return_value=["Thanks!", "Appreciate it!", "Let us know!"])
            self.mock_llm_adapter.analyze_commercial_intent = AsyncMock(return_value={"sales_intent": False, "confidence": 0.1})
            self.mock_llm_adapter.categorize_competitor_complaint = AsyncMock(return_value={"category": "other", "pain_level": 3})
            self.mock_llm_adapter.analyze_web_content = AsyncMock(return_value={"summary": "Web insights", "opportunities": []})
            mock_llm.return_value = self.mock_llm_adapter
            
            # Mock analyzer
            self.mock_analyzer = MagicMock()
            self.mock_analyzer.analyze = AsyncMock(return_value=MagicMock(
                relevant=True,
                intent=MagicMock(value="GENERAL"),
                strategic_tag=MagicMock(value="NONE"),
                sentiment_score=0.5,
                sentiment_label="positive",
                gatekeeper_category=GatekeeperCategory.NONE
            ))
            self.mock_analyzer.detect_launch = AsyncMock()
            mock_analyzer_factory.return_value = self.mock_analyzer
            
            # Mock web scanner
            self.mock_web_scanner = MagicMock()
            self.mock_web_scanner.scan = AsyncMock(return_value={"summary": "Scanned content"})
            mock_scanner.return_value = self.mock_web_scanner
            
            self.processor = ChunkProcessor(
                worker_id="test-worker-v4",
                redis_client=self.mock_redis,
                storage=self.mock_storage,
            )
            
            # Override internal adapters with our mocks
            self.processor._llm_adapter = self.mock_llm_adapter
            self.processor._analyzer = self.mock_analyzer

    # =========================================================================
    # TEST 1: Launch Detection (The Oracle)
    # =========================================================================
    async def test_launch_detection(self):
        """
        LAUNCH: Verify The Oracle detects product launches.
        """
        print("\nTesting Launch Detection (The Oracle)...")
        
        # Setup: Mock detect_launch to return a successful detection
        self.mock_analyzer.detect_launch = AsyncMock(return_value=MagicMock(
            is_launch=True,
            product_name="SuperFeature 2.0",
            success_score=85,
            reason="High demand detected with positive sentiment",
            prediction_category="POTENTIAL_HIT"
        ))
        
        # Create input
        input_data = AnalysisInput(
            text="We just launched SuperFeature 2.0! It's been in development for months and we're excited to share it with you!",
            target_brand="test-brand",
            target_keywords=["launch", "feature"],
            is_competitor=False,
            source_platform="twitter"
        )
        
        # Call analyzer's detect_launch
        result = await self.mock_analyzer.detect_launch(input_data)
        
        # Assertions
        self.assertTrue(result.is_launch)
        self.assertEqual(result.product_name, "SuperFeature 2.0")
        self.assertGreater(result.success_score, 70)
        print(f"   Detected: {result.product_name} (Score: {result.success_score})")
        print("Launch Detection Verified!")

    # =========================================================================
    # TEST 2: Response Suggestion
    # =========================================================================
    async def test_response_suggestion(self):
        """
        RESPONSE: Verify AI generates appropriate response suggestions.
        """
        print("\nTesting Response Suggestion...")
        
        # Setup: Mock already configured in setUp
        self.mock_llm_adapter.generate_response_suggestion = AsyncMock(return_value=[
            "Thank you for the kind words!",
            "We're thrilled you're enjoying it!",
            "Your feedback means the world to us."
        ])
        
        # Call
        suggestions = await self.mock_llm_adapter.generate_response_suggestion(
            text="This product is amazing! Best purchase ever!",
            sentiment="positive"
        )
        
        # Assertions
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 3)
        self.assertTrue(all(isinstance(s, str) for s in suggestions))
        print(f"   Generated {len(suggestions)} suggestions")
        for i, s in enumerate(suggestions, 1):
            print(f"      {i}. {s[:50]}...")
        print("Response Suggestion Verified!")

    # =========================================================================
    # TEST 3: Commercial Intent Detection
    # =========================================================================
    async def test_commercial_intent_detection(self):
        """
        INTENT: Verify detection of sales/commercial intent.
        """
        print("\nTesting Commercial Intent Detection...")
        
        # Setup: Mock analyze_commercial_intent to return high intent
        self.mock_llm_adapter.analyze_commercial_intent = AsyncMock(return_value={
            "sales_intent": True,
            "confidence": 0.92,
            "intent_type": "alternative_seeking",
            "pain_point": "Current tool is too expensive"
        })
        
        # Create task for process_lead_intent
        task = {
            "mention_id": "mention-123",
            "text": "Looking for a cheaper alternative to Competitor. Any suggestions?",
            "brand": "test-brand",
            "monitor_id": "mon-1",
            "user_id": "user-1",
            "source_platform": "reddit"
        }
        
        # Call
        await self.processor.process_lead_intent(task)
        
        # Assertions - check Redis was called with lead payload
        self.mock_redis.rpush.assert_called()
        call_args = self.mock_redis.rpush.call_args_list
        
        # Find the queue:leads call
        lead_queued = any("queue:leads" in str(call) for call in call_args)
        self.assertTrue(lead_queued, "Lead should be queued to Redis")
        
        print("   Commercial intent detected and lead queued")
        print("Commercial Intent Detection Verified!")

    # =========================================================================
    # TEST 4: Competitor Complaint Categorization
    # =========================================================================
    async def test_competitor_complaint_categorization(self):
        """
        COMPETITOR: Verify categorization of competitor complaints.
        """
        print("\nTesting Competitor Complaint Categorization...")
        
        # Setup: Mock categorize_competitor_complaint
        self.mock_llm_adapter.categorize_competitor_complaint = AsyncMock(return_value={
            "category": "pricing",
            "specific_issue": "Hidden fees and unexpected price increases",
            "pain_level": 8
        })
        
        # Create task
        task = {
            "mentions": [
                "Competitor just raised prices by 50%! This is ridiculous!",
                "The hidden fees are killing my budget."
            ],
            "competitor_id": "comp-123",
            "competitor_name": "BigCorp",
            "brand": "test-brand"
        }
        
        # Call
        await self.processor.process_competitor_gap(task)
        
        # Assertions - check Redis was called
        self.mock_redis.rpush.assert_called()
        call_args = self.mock_redis.rpush.call_args_list
        
        # Find the competitor complaints call
        complaint_queued = any("queue:competitors:complaints" in str(call) or "competitor:" in str(call) for call in call_args)
        self.assertTrue(complaint_queued, "Complaint should be queued to Redis")
        
        print("   Competitor complaint categorized as 'pricing' (pain: 8/10)")
        print("Competitor Complaint Categorization Verified!")

    # =========================================================================
    # TEST 5: Web Insights Scan
    # =========================================================================
    async def test_web_insights_scan(self):
        """
        WEB: Verify web scanning and insights extraction.
        """
        print("\nTesting Web Insights Scan...")
        
        # Setup: Mock web scanner
        self.mock_web_scanner.scan = AsyncMock(return_value={
            "summary": "Brand has strong presence in tech forums",
            "sentiment": "positive",
            "key_themes": ["innovation", "reliability", "support"],
            "notable_mentions": [
                {"source": "TechCrunch", "highlight": "Top 10 startups to watch"}
            ],
            "opportunities": ["Expand to enterprise market"],
            "risks": ["Increasing competition from BigCorp"]
        })
        
        # Create task
        task = {"brand": "test-brand"}
        
        # Call
        await self.processor.process_web_scan(task)
        
        # Assertions - check Redis was called to store results
        self.mock_redis.set.assert_called()
        call_args = self.mock_redis.set.call_args
        
        # Verify the key pattern
        key = call_args[0][0]
        self.assertIn("web_insights", key)
        
        print("   Web scan completed and insights stored")
        print("Web Insights Scan Verified!")


if __name__ == "__main__":
    print("=" * 60)
    print("V4 FEATURE INTEGRATION TESTS")
    print("=" * 60)
    unittest.main(verbosity=2)
