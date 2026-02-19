"""Shared LLM client utilities (Facade).

This module delegates to the modularized LLM components in `worker.llm`.
Retains the original public API for backward compatibility.
"""
from __future__ import annotations

import logging
from typing import Any

from .llm.client import LLMClient
from .llm.prompts import (
    BRAND_ANALYSIS_PROMPT,
    SENTIMENT_ANALYSIS_PROMPT,
    STRATEGIC_INTELLIGENCE_PROMPT,
    LAUNCH_DETECTION_PROMPT,
    WEB_INSIGHTS_PROMPT,
    RESPONSE_SUGGESTION_PROMPT,
    COMPETITOR_ANALYSIS_PROMPT,
    FLEXIBLE_ANALYSIS_PROMPT
)

# =============================================================================
# PUBLIC API - Brand Reputation Analysis Functions
# =============================================================================

async def invoke_prompt_text(prompt: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Flexible prompt invocation for custom analysis tasks."""
    return await LLMClient.get_instance().execute(
        FLEXIBLE_ANALYSIS_PROMPT, 
        {"input": prompt}, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_general(data: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Brand reputation analysis with sentiment, intent, and strategic intelligence."""
    return await LLMClient.get_instance().execute(
        BRAND_ANALYSIS_PROMPT, 
        {"data": data}, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_sentiment(text: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Specialized sentiment analysis for brand mentions."""
    return await LLMClient.get_instance().execute(
        SENTIMENT_ANALYSIS_PROMPT, 
        {"text": text}, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_strategic(brand_name: str, context: str, text: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Strategic intelligence analysis for leads, crisis detection, and competitive intelligence."""
    variables = {
        "brand": brand_name,
        "context": context,
        "text": text,
    }
    return await LLMClient.get_instance().execute(
        STRATEGIC_INTELLIGENCE_PROMPT, 
        variables, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_launch_detection(prompt: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """The Oracle: Predict product launch success based on market reception signals."""
    return await LLMClient.get_instance().execute(
        LAUNCH_DETECTION_PROMPT, 
        {"prompt": prompt}, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_web_insights(text: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Analyze web content for brand research and competitive intelligence."""
    return await LLMClient.get_instance().execute(
        WEB_INSIGHTS_PROMPT, 
        {"text": text}, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_response_suggestion(brand_name: str, text: str, sentiment: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Generate response suggestions for customer success and crisis communication."""
    variables = {
        "brand": brand_name,
        "text": text,
        "sentiment": sentiment,
    }
    return await LLMClient.get_instance().execute(
        RESPONSE_SUGGESTION_PROMPT, 
        variables, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def invoke_competitor_analysis(text: str, *, timeout: int, brand: str, chunk_id: str, operation: str, format_json: bool = False) -> str:
    """Analyze competitor mentions to identify weaknesses and market opportunities."""
    return await LLMClient.get_instance().execute(
        COMPETITOR_ANALYSIS_PROMPT, 
        {"text": text}, 
        timeout=timeout, 
        brand=brand, 
        chunk_id=chunk_id, 
        operation=operation, 
        format_json=format_json
    )


async def embed_query(text: str) -> list[float]:
    """Generate embeddings for semantic search and clustering."""
    return await LLMClient.get_instance().embed_query(text)
