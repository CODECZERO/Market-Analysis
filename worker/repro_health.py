
import asyncio
from unittest.mock import MagicMock
import asyncio
from unittest.mock import MagicMock
from worker.health_score import HealthScoreCalculator
from worker.domain_types import EnhancedAnalysis, Emotions

async def test():
    # Mock Redis
    redis = MagicMock()
    redis.get.return_value = None # simulate no previous score
    
    # Mock Analysis Result based on summary.json observations
    # "dominantTopics" had a long string, so topics probably has 1 item
    # "sentiment" was 0.8
    analysis = EnhancedAnalysis(
        sentiment_score=0.8,
        sentiment_label="positive",
        emotions=Emotions(),
        is_sarcastic=False,
        urgency="low",
        topics=["Key Findings: Google is promoting..."],
        entities={"people": [], "companies": [], "products": []},
        language="en"
    )

    calc = HealthScoreCalculator(redis, "test-worker")
    
    # Test with 1 item
    score = await calc.calculate("google", [analysis])
    print(f"Score with 1 item: {score}")

    # Test with default item (failure case)
    default_analysis = EnhancedAnalysis()
    score_default = await calc.calculate("google", [default_analysis])
    print(f"Score with default item: {score_default}")

    # Test with empty list
    score_empty = await calc.calculate("google", [])
    print(f"Score with empty list: {score_empty}")

if __name__ == "__main__":
    asyncio.run(test())
