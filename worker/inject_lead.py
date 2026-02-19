import asyncio
import os
import sys
import json
import uuid

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from worker.redis_client import RedisClient
from worker.config import get_settings

async def main():
    settings = get_settings()
    url = settings.redis_url
    print(f"Connecting to {url}")
    
    r = RedisClient(url)
    await r.ensure_connection()
    
    # Create a task that looks like what Aggregator sends
    # Or inject directly into 'queue:brand:google:chunks' if I can mimic chunk structure
    # But queue_consumer handles "tasks:priority" too.
    
    # Simpler: Create a chunk manually and push to brand queue
    # Format: Chunk model model_dump_json()
    
    brand = "google"
    chunk_id = f"manual-test-{uuid.uuid4()}"
    
    payload = {
        "chunkId": chunk_id,
        "brand": brand,
        "createdAt": "2025-01-01T10:00:00Z",
        "mentions": [
            {
                "id": str(uuid.uuid4()),
                "source": "manual_test",
                "text": "I am urgently looking for an alternative to Google Cloud because the pricing is too high and support is terrible. Need to switch ASAP.",
                "created_at": "2025-01-01T10:00:00Z",
                "metadata": {
                    "platform": "twitter",
                    "author": "angry_ceo"
                }
            }
        ],
        "meta": {"totalChunks": 1, "chunkIndex": 0}
    }
    
    key = f"queue:brand:{brand}:chunks"
    print(f"Pushing manual lead to {key}")
    await r._client.rpush(key, json.dumps(payload))
    
    print("Done. Check worker logs.")
    await r.close()

if __name__ == "__main__":
    asyncio.run(main())
