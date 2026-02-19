import asyncio
import os
import sys
import json

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
    
    brand = "google"
    # Worker storage writes to: result:brand:{brand}:chunks
    key = f"result:brand:{brand}:chunks"
    print(f"Checking key: {key}")
    
    # It's a list of JSONs (Chunks)
    items = await r._client.lrange(key, 0, 20) # Check last 20 chunks
    print(f"Found {len(items)} chunks")
    
    found_lead = False
    
    # iterate in reverse to find latest
    for i, item_str in enumerate(items):
        try:
            chunk = json.loads(item_str)
            mentions = chunk.get("mentions", [])
            # If mentions is a list of dicts
            for m in mentions:
                text = m.get("text", "")
                intent = m.get("intent", "unknown")
                if "alternative to Google" in text:
                    print(f"\n--- FOUND INJECTED LEAD (Chunk {i}) ---")
                    print(f"Text: {text[:100]}...")
                    print(f"Intent: {intent}")
                    print(f"Strategic Tag: {m.get('strategic_tag')}")
                    print(f"Sentiment: {m.get('sentiment_score')}")
                    found_lead = True
        except Exception as e:
            print(f"Error parsing chunk {i}: {e}")
            
    if not found_lead:
        print("\nInjected mention NOT found in top 20 chunks.")

    await r.close()

if __name__ == "__main__":
    asyncio.run(main())
