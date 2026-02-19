"""
Competitor Discovery Service
Uses web scraping + LLM to discover and analyze competitors for a brand.

Flow:
1. Scrape competitor review sites (G2, Capterra, Google)
2. Pass scraped content to LLM for competitor extraction
3. Return structured competitor data
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus

from .web_scraper import scrape_url, scrape_urls, ScrapedContent
from .llm_adapter import get_llm_adapter
from .logger import get_logger

logger = get_logger(__name__)

# Pre-defined list of major tech competitors (for fast detection without scraping)
KNOWN_TECH_COMPANIES = frozenset([
    # Big Tech
    "google", "microsoft", "apple", "amazon", "meta", "facebook", "openai",
    "anthropic", "nvidia", "ibm", "oracle", "salesforce", "adobe", "intel",
    "netflix", "spotify", "twitter", "x", "linkedin", "tiktok", "bytedance",
    # Cloud/SaaS
    "aws", "azure", "gcp", "heroku", "vercel", "netlify", "cloudflare",
    "datadog", "splunk", "elastic", "mongodb", "redis", "snowflake",
    "hubspot", "zendesk", "intercom", "freshdesk", "mailchimp", "sendgrid",
    # Dev Tools
    "github", "gitlab", "bitbucket", "jira", "atlassian", "notion", "slack",
    "zoom", "teams", "discord", "figma", "canva", "miro", "asana", "trello",
    # AI/ML
    "chatgpt", "claude", "gemini", "copilot", "midjourney", "stability ai",
    "huggingface", "cohere", "perplexity", "jasper", "grammarly",
    # Payments/Fintech
    "stripe", "paypal", "square", "shopify", "plaid", "braintree",
])

# URLs to scrape for competitor discovery
COMPETITOR_DISCOVERY_URLS = {
    "g2_alternatives": "https://www.g2.com/search?utf8=%E2%9C%93&query={brand}+alternatives",
    "google_competitors": "https://www.google.com/search?q={brand}+competitors",
    "capterra_alternatives": "https://www.capterra.com/search/?search={brand}",
}


@dataclass
class Competitor:
    """Discovered competitor."""
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    strengths: List[str] = None
    weaknesses: List[str] = None
    confidence: float = 0.0
    source: str = "unknown"
    
    def __post_init__(self):
        self.strengths = self.strengths or []
        self.weaknesses = self.weaknesses or []


@dataclass  
class CompetitorDiscoveryResult:
    """Result from competitor discovery."""
    brand: str
    competitors: List[Competitor]
    sources_scraped: int
    total_content_words: int
    summary: str


class CompetitorDiscovery:
    """Discovers competitors using web scraping + LLM analysis."""
    
    def __init__(self, worker_id: str):
        self._worker_id = worker_id
        self._llm = get_llm_adapter(worker_id)
    
    async def discover_from_mentions(self, brand: str, mention_texts: List[str]) -> List[Competitor]:
        """
        Extract competitors from mention texts without web scraping.
        Uses regex + LLM hybrid approach.
        """
        # Step 1: Quick regex-based extraction from known companies
        found_companies = set()
        combined_text = " ".join(mention_texts).lower()
        
        for company in KNOWN_TECH_COMPANIES:
            if company in combined_text and company.lower() != brand.lower():
                found_companies.add(company)
        
        logger.info(f"[CompetitorDiscovery] Found {len(found_companies)} potential competitors via regex: {list(found_companies)[:5]}")
        
        if not found_companies and not mention_texts:
            return []
        
        # Step 2: Pass to LLM for deeper analysis
        try:
            prompt = f"""Analyze these social media mentions about "{brand}" and identify competitor companies mentioned.

MENTIONS:
{chr(10).join(mention_texts[:10])}

ALREADY DETECTED (via pattern matching): {list(found_companies)}

Return a JSON object with:
{{
    "competitors": [
        {{
            "name": "Company Name",
            "industry": "Industry/Category",
            "is_competitor": true,
            "relationship": "direct_competitor" | "indirect_competitor" | "partner" | "supplier",
            "mentioned_context": "Brief context of how they were mentioned",
            "confidence": 0.0-1.0
        }}
    ]
}}

ONLY include companies that are actual competitors to {brand}, not partners or suppliers.
Return ONLY valid JSON."""

            result = await self._llm.analyze_competitor_mentions(prompt)
            
            competitors = []
            for comp_data in result.get("competitors", []):
                if comp_data.get("is_competitor", True) and comp_data.get("confidence", 0) >= 0.6:
                    competitors.append(Competitor(
                        name=comp_data.get("name", ""),
                        industry=comp_data.get("industry"),
                        confidence=comp_data.get("confidence", 0.8),
                        source="mention_analysis"
                    ))
            
            # Add regex-detected companies that weren't in LLM response
            llm_names = {c.name.lower() for c in competitors}
            for company in found_companies:
                if company.lower() not in llm_names:
                    competitors.append(Competitor(
                        name=company.title(),
                        confidence=0.7,
                        source="regex_detection"
                    ))
            
            logger.info(f"[CompetitorDiscovery] Total competitors found for {brand}: {len(competitors)}")
            return competitors
            
        except Exception as e:
            logger.warning(f"[CompetitorDiscovery] LLM analysis failed: {e}")
            # Return regex-only results
            return [Competitor(name=c.title(), confidence=0.6, source="regex_only") for c in found_companies]
    
    async def discover_from_web(self, brand: str) -> CompetitorDiscoveryResult:
        """
        Discover competitors by scraping web pages and analyzing with LLM.
        """
        logger.info(f"[CompetitorDiscovery] Starting web-based discovery for: {brand}")
        
        # Build URLs to scrape
        urls_to_scrape = []
        for url_template in COMPETITOR_DISCOVERY_URLS.values():
            url = url_template.format(brand=quote_plus(brand))
            urls_to_scrape.append(url)
        
        # Scrape URLs
        scraped_contents: List[ScrapedContent] = []
        try:
            scraped_contents = await scrape_urls(urls_to_scrape, max_concurrent=2)
        except Exception as e:
            logger.error(f"[CompetitorDiscovery] Web scraping failed: {e}")
        
        # Filter successful scrapes
        successful_scrapes = [s for s in scraped_contents if s.success and s.word_count > 50]
        total_words = sum(s.word_count for s in successful_scrapes)
        
        logger.info(f"[CompetitorDiscovery] Scraped {len(successful_scrapes)}/{len(urls_to_scrape)} URLs, {total_words} words total")
        
        if not successful_scrapes:
            return CompetitorDiscoveryResult(
                brand=brand,
                competitors=[],
                sources_scraped=0,
                total_content_words=0,
                summary="Failed to scrape any competitor information from the web."
            )
        
        # Combine scraped content
        combined_text = "\n\n---\n\n".join([
            f"SOURCE: {s.source_name}\n{s.text[:3000]}" 
            for s in successful_scrapes
        ])
        
        # Pass to LLM for analysis
        try:
            prompt = f"""Analyze this scraped web content about "{brand}" competitors and alternatives.

SCRAPED CONTENT:
{combined_text[:8000]}

Extract all competitor companies mentioned and return a JSON object:
{{
    "summary": "Brief summary of the competitive landscape",
    "competitors": [
        {{
            "name": "Company Name",
            "industry": "Industry category",
            "website": "company.com (if found)",
            "is_direct_competitor": true/false,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "confidence": 0.0-1.0
        }}
    ]
}}

Focus on actual competitors to {brand}, sort by relevance. Return ONLY valid JSON."""

            result = await self._llm.analyze_competitor_web_content(prompt)
            
            competitors = []
            for comp_data in result.get("competitors", []):
                competitors.append(Competitor(
                    name=comp_data.get("name", ""),
                    industry=comp_data.get("industry"),
                    website=comp_data.get("website"),
                    strengths=comp_data.get("strengths", []),
                    weaknesses=comp_data.get("weaknesses", []),
                    confidence=comp_data.get("confidence", 0.8),
                    source="web_scrape"
                ))
            
            return CompetitorDiscoveryResult(
                brand=brand,
                competitors=competitors,
                sources_scraped=len(successful_scrapes),
                total_content_words=total_words,
                summary=result.get("summary", "Competitor analysis complete.")
            )
            
        except Exception as e:
            logger.error(f"[CompetitorDiscovery] LLM analysis of scraped content failed: {e}")
            return CompetitorDiscoveryResult(
                brand=brand,
                competitors=[],
                sources_scraped=len(successful_scrapes),
                total_content_words=total_words,
                summary=f"Scraped content but LLM analysis failed: {str(e)[:100]}"
            )


def get_competitor_discovery(worker_id: str) -> CompetitorDiscovery:
    """Factory function for CompetitorDiscovery."""
    return CompetitorDiscovery(worker_id)
