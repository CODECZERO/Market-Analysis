"""Retry utilities for worker with exponential backoff.

Handles Render free tier cold starts with 5x retry and 3s base delay.
"""
from __future__ import annotations

import asyncio
import functools
import logging
import time
from typing import TypeVar, Callable, ParamSpec, Any

logger = logging.getLogger(__name__)

# Constants for cold start handling
MAX_RETRIES = 5
BASE_DELAY_SECONDS = 3.0

P = ParamSpec('P')
R = TypeVar('R')


def retry_sync(
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY_SECONDS,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Synchronous retry decorator with exponential backoff."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"[Retry] {func.__name__} failed, retry {attempt + 1}/{max_retries} in {delay:.1f}s: {e}"
                        )
                        time.sleep(delay)
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed after {max_retries} retries")
        
        return wrapper
    return decorator


def retry_async(
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY_SECONDS,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Async retry decorator with exponential backoff."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"[Retry] {func.__name__} failed, retry {attempt + 1}/{max_retries} in {delay:.1f}s: {e}"
                        )
                        await asyncio.sleep(delay)
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed after {max_retries} retries")
        
        return wrapper  # type: ignore
    return decorator


async def with_retry_async(
    coro: Any,
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY_SECONDS,
    label: str = "operation",
) -> Any:
    """Execute a coroutine with retry logic."""
    last_exception: Exception | None = None
    
    for attempt in range(max_retries + 1):
        try:
            return await coro
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"[Retry] {label} failed, retry {attempt + 1}/{max_retries} in {delay:.1f}s: {e}")
                await asyncio.sleep(delay)
    
    if last_exception:
        raise last_exception
    raise RuntimeError(f"{label} failed after {max_retries} retries")
