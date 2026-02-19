"""Web scraper module for extracting content from URLs using Playwright.

Features:
- Full browser automation (handles JS, single-page apps)
- Stealth techniques (random user agents, viewport)
- Rate limiting (1 second delay between requests)
- Caching (1 hour TTL)
- Retry with exponential backoff
- Content extraction using trafilatura
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import random
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Error as PlaywrightError
from fake_useragent import UserAgent
import trafilatura

from .retry_utils import retry_async, with_retry_async
from .logger import get_logger

logger = get_logger(__name__)

# Rate limiting: 2 seconds between requests to be safer
RATE_LIMIT_DELAY = 2.0

# Cache TTL: 1 hour
CACHE_TTL_SECONDS = 3600

# Request timeout
REQUEST_TIMEOUT = 45000  # 45 seconds

# Browser instance (singleton)
_browser_instance: Optional[Browser] = None
_playwright_instance: Any = None


@dataclass
class ScrapedContent:
    """Represents scraped content from a URL."""
    url: str
    title: str
    text: str
    source_name: str
    scraped_at: str
    word_count: int
    success: bool
    error: Optional[str] = None


class ContentCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, ttl_seconds: int = CACHE_TTL_SECONDS):
        self._cache: Dict[str, tuple[ScrapedContent, float]] = {}
        self._ttl = ttl_seconds
    
    def _key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[ScrapedContent]:
        key = self._key(url)
        if key in self._cache:
            content, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                logger.debug(f"Cache hit for {url}")
                return content
            else:
                del self._cache[key]
        return None
    
    def set(self, url: str, content: ScrapedContent) -> None:
        key = self._key(url)
        self._cache[key] = (content, time.time())
    
    def clear_expired(self) -> int:
        """Remove expired entries. Returns count of removed items."""
        now = time.time()
        expired = [k for k, (_, ts) in self._cache.items() if now - ts >= self._ttl]
        for k in expired:
            del self._cache[k]
        return len(expired)


# Global cache instance
_cache = ContentCache()
_last_request_time = 0.0


async def _rate_limit():
    """Ensure rate limiting between requests."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


async def _get_browser() -> Browser:
    """Get or create global browser instance."""
    global _browser_instance, _playwright_instance
    if _browser_instance is None:
        logger.info("Launching Playwright browser...")
        _playwright_instance = await async_playwright().start()
        _browser_instance = await _playwright_instance.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certifcate-errors",
                "--ignore-certifcate-errors-spki-list",
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )
    return _browser_instance


def _get_random_user_agent() -> str:
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


async def _extract_content_page(page: Page, url: str) -> tuple[str, str, str]:
    """Extract content using Trafilatura on the page HTML."""
    html = await page.content()
    
    # Use trafilatura for robust extraction
    extracted = trafilatura.extract(
        html,
        include_links=False,
        include_images=False,
        include_tables=False,
        no_fallback=False
    )
    
    title = await page.title()
    text = extracted if extracted else ""
    
    # Fallback if trafilatura fails
    if not text:
        text = await page.evaluate("""() => {
            return document.body.innerText;
        }""")
    
    # Extract source name
    from urllib.parse import urlparse
    parsed = urlparse(url)
    source_name = parsed.netloc.replace("www.", "")
    
    # Clean up
    if text:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)
        if len(text) > 10000:
            text = text[:10000] + "..."
            
    return title, text, source_name


@retry_async(max_retries=2, base_delay=3.0, exceptions=(PlaywrightError, TimeoutError, Exception))
async def scrape_url(url: str, **kwargs) -> ScrapedContent:
    """Scrape a single URL using Playwright with stealth settings."""
    # Check cache first
    cached = _cache.get(url)
    if cached:
        return cached
    
    # Rate limit
    await _rate_limit()
    
    context = None
    page = None
    
    try:
        browser = await _get_browser()
        
        # Create stealthy context
        user_agent = _get_random_user_agent()
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            java_script_enabled=True,
        )
        
        # Add stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        # Navigate with safer timeout strategy
        logger.info(f"Navigating to {url}...")
        await page.goto(url, timeout=REQUEST_TIMEOUT, wait_until="domcontentloaded")
        
        # Wait a bit for dynamic content (random 1-3s)
        await page.wait_for_timeout(random.randint(1000, 3000))
        
        title, text, source_name = await _extract_content_page(page, url)
        
        content = ScrapedContent(
            url=url,
            title=title or "Untitled",
            text=text,
            source_name=source_name,
            scraped_at=datetime.utcnow().isoformat(),
            word_count=len(text.split()),
            success=True,
        )
        
        if content.word_count > 50:  # Only cache if we actually got some content
            _cache.set(url, content)
            logger.info(f"Scraped {url}: {content.word_count} words")
        else:
            logger.warning(f"Scraped {url} but got low word count ({content.word_count})")
        
        return content
        
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ScrapedContent(
            url=url,
            title="",
            text="",
            source_name="",
            scraped_at=datetime.utcnow().isoformat(),
            word_count=0,
            success=False,
            error=str(e),
        )
    finally:
        if page:
            await page.close()
        if context:
            await context.close()


async def scrape_urls(urls: List[str], max_concurrent: int = 3) -> List[ScrapedContent]:
    """Scrape multiple URLs with concurrency control.
    
    Args:
        urls: List of URLs to scrape
        max_concurrent: Maximum concurrent browser contexts (default 3)
    
    Returns:
        List of ScrapedContent objects
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_with_semaphore(url: str) -> ScrapedContent:
        async with semaphore:
            return await scrape_url(url)
    
    tasks = [scrape_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=False)

