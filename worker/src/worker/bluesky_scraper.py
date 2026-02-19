"""
Bluesky Firehose Scraper - Real-time AT Protocol Integration

DEPRECATED: This module is deprecated as of Phase 15.
The canonical Bluesky data source implementation is now in:
  aggregator/src/modules/aggregator/providers/bluesky.provider.ts

Workers should NOT fetch data from sources directly. Data flows:
  Aggregator -> Redis -> Orchestrator -> Workers

This file is kept for reference only.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Callable

import aiohttp

from .logger import get_logger

logger = get_logger(__name__)

# Bluesky AT Protocol endpoints
BLUESKY_FIREHOSE_URL = "wss://bsky.network/xrpc/com.atproto.sync.subscribeRepos"
BLUESKY_API_BASE = "https://public.api.bsky.app/xrpc"


@dataclass
class BlueskyPost:
    """Represents a Bluesky post."""
    uri: str
    cid: str
    author_did: str
    author_handle: str
    text: str
    created_at: datetime
    reply_to: str | None = None
    embed_url: str | None = None
    likes: int = 0
    reposts: int = 0


class BlueskyFirehoseScraper:
    """
    Scrapes Bluesky posts for brand mentions.
    
    Can operate in two modes:
    1. Firehose mode: Real-time streaming of all posts
    2. Search mode: Periodic polling of search API
    """

    def __init__(
        self,
        brand_keywords: list[str] | None = None,
        on_mention: Callable[[BlueskyPost], None] | None = None,
    ) -> None:
        self.brand_keywords = [kw.lower() for kw in (brand_keywords or [])]
        self.on_mention = on_mention
        self._session: aiohttp.ClientSession | None = None
        self._running = False

    async def __aenter__(self) -> "BlueskyFirehoseScraper":
        self._session = aiohttp.ClientSession(
            headers={"User-Agent": "BrandTracker/1.0 Bluesky Scraper"},
        )
        return self

    async def __aexit__(self, *args) -> None:
        if self._session:
            await self._session.close()
        self._running = False

    async def search_posts(
        self,
        query: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> tuple[list[BlueskyPost], str | None]:
        """
        Search for posts containing a query string.
        Uses the public Bluesky search API.
        """
        if not self._session:
            raise RuntimeError("Use as async context manager")

        url = f"{BLUESKY_API_BASE}/app.bsky.feed.searchPosts"
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, 100),
        }
        if cursor:
            params["cursor"] = cursor

        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Bluesky search failed: {response.status}")
                    return [], None

                data = await response.json()
                posts = self._parse_search_results(data.get("posts", []))
                next_cursor = data.get("cursor")

                return posts, next_cursor

        except aiohttp.ClientError as e:
            logger.warning(f"Bluesky API error: {e}")
            return [], None
        except Exception as e:
            logger.error(f"Unexpected error in Bluesky search: {e}")
            return [], None

    def _parse_search_results(self, posts_data: list[dict]) -> list[BlueskyPost]:
        """Parse posts from the search API response."""
        posts: list[BlueskyPost] = []

        for post_data in posts_data:
            try:
                record = post_data.get("record", {})
                author = post_data.get("author", {})
                
                # Parse created_at
                created_str = record.get("createdAt", "")
                try:
                    created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                except ValueError:
                    created_at = datetime.utcnow()

                # Extract embed URL if present
                embed_url = None
                embed = record.get("embed", {})
                if embed.get("$type") == "app.bsky.embed.external":
                    embed_url = embed.get("external", {}).get("uri")

                # Check for reply
                reply_to = None
                reply = record.get("reply", {})
                if reply:
                    parent = reply.get("parent", {})
                    reply_to = parent.get("uri")

                posts.append(BlueskyPost(
                    uri=post_data.get("uri", ""),
                    cid=post_data.get("cid", ""),
                    author_did=author.get("did", ""),
                    author_handle=author.get("handle", "unknown"),
                    text=record.get("text", "")[:2000],
                    created_at=created_at,
                    reply_to=reply_to,
                    embed_url=embed_url,
                    likes=post_data.get("likeCount", 0),
                    reposts=post_data.get("repostCount", 0),
                ))
            except Exception as e:
                logger.debug(f"Error parsing post: {e}")
                continue

        return posts

    async def search_for_brands(
        self,
        brands: list[str],
        limit_per_brand: int = 50,
    ) -> dict[str, list[BlueskyPost]]:
        """Search for multiple brands and return posts by brand."""
        results: dict[str, list[BlueskyPost]] = {}

        for brand in brands:
            posts, _ = await self.search_posts(brand, limit=limit_per_brand)
            results[brand] = posts
            logger.info(f"Found {len(posts)} Bluesky posts for '{brand}'")
            await asyncio.sleep(0.5)  # Rate limiting

        return results

    def filter_by_keywords(self, posts: list[BlueskyPost]) -> list[BlueskyPost]:
        """Filter posts that match any of the configured brand keywords."""
        if not self.brand_keywords:
            return posts

        matching: list[BlueskyPost] = []
        for post in posts:
            text_lower = post.text.lower()
            if any(kw in text_lower for kw in self.brand_keywords):
                matching.append(post)

        return matching

    def to_mention_format(self, post: BlueskyPost, brand_id: str) -> dict[str, Any]:
        """Convert Bluesky post to mention format for the pipeline."""
        return {
            "brandId": brand_id,
            "source": "bluesky",
            "sourceUrl": f"https://bsky.app/profile/{post.author_handle}/post/{post.uri.split('/')[-1]}",
            "content": post.text,
            "author": f"@{post.author_handle}",
            "publishedAt": post.created_at.isoformat(),
            "externalId": hashlib.md5(post.uri.encode()).hexdigest(),
            "metadata": {
                "platform": "bluesky",
                "author_did": post.author_did,
                "uri": post.uri,
                "cid": post.cid,
                "likes": post.likes,
                "reposts": post.reposts,
                "is_reply": post.reply_to is not None,
            },
        }

    async def poll_mentions(
        self,
        brands: list[str],
        interval_seconds: int = 300,
        callback: Callable[[list[dict]], None] | None = None,
    ) -> None:
        """
        Continuously poll for brand mentions at specified interval.
        Calls callback with new mentions found.
        """
        self._running = True
        seen_uris: set[str] = set()

        logger.info(f"Starting Bluesky polling for brands: {brands}")

        while self._running:
            try:
                results = await self.search_for_brands(brands, limit_per_brand=25)
                
                new_mentions: list[dict] = []
                for brand, posts in results.items():
                    for post in posts:
                        if post.uri not in seen_uris:
                            seen_uris.add(post.uri)
                            mention = self.to_mention_format(post, brand)
                            new_mentions.append(mention)

                if new_mentions and callback:
                    callback(new_mentions)
                    logger.info(f"Found {len(new_mentions)} new Bluesky mentions")

                # Trim seen_uris to prevent memory growth
                if len(seen_uris) > 10000:
                    seen_uris = set(list(seen_uris)[-5000:])

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Error in Bluesky polling: {e}")
                await asyncio.sleep(60)  # Wait before retry

    def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False


async def demo():
    """Demo the Bluesky scraper."""
    async with BlueskyFirehoseScraper() as scraper:
        # Search for some tech terms
        posts, cursor = await scraper.search_posts("startup", limit=10)
        print(f"Found {len(posts)} posts about 'startup'")
        
        for post in posts[:3]:
            print(f"\n@{post.author_handle}: {post.text[:100]}...")
            print(f"  Likes: {post.likes}, Reposts: {post.reposts}")

        # Search for multiple brands
        results = await scraper.search_for_brands(["vercel", "nextjs"], limit_per_brand=5)
        for brand, brand_posts in results.items():
            print(f"\n{brand}: {len(brand_posts)} posts")


if __name__ == "__main__":
    asyncio.run(demo())
