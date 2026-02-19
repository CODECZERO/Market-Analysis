
import sys
import os
import asyncio

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'worker', 'src'))

# Mock env vars
os.environ["LLM_PROVIDER"] = "mock"

async def test_init():
    print("Testing imports...")
    try:
        from worker.analyzer import AnalysisResult, AnalysisInput, Intent
        from worker.llm_adapter import get_llm_adapter, RateLimiter
        from worker.storage import ResultStorage
        from worker.processor import ChunkProcessor
        print("Imports successful.")
    except ImportError as e:
        print(f"Import failed: {e}")
        return

    print("Testing RateLimiter...")
    limiter = RateLimiter(10, 60)
    await limiter.acquire()
    print("RateLimiter acquired.")

    print("Testing Analyzer init...")
    # This requires LLM adapter which requires settings
    # We mocked LLM_PROVIDER=mock so it should work
    try:
        from worker.analyzer import get_analyzer
        analyzer = get_analyzer("test-worker")
        print("Analyzer initialized.")
    except Exception as e:
        print(f"Analyzer init failed: {e}")

    print("Testing Storage init...")
    try:
        # Pass None for redis/mongo clients just to check init logic doesn't crash immediately on type checks if loose
        # Actually storage expects RedisClient, let's mock it
        class MockRedis:
            pass
        storage = ResultStorage(MockRedis(), "test-worker", mongo_client=None)
        print("Storage initialized.")
    except Exception as e:
        print(f"Storage init failed: {e}")

    print("Verification complete.")

if __name__ == "__main__":
    asyncio.run(test_init())
