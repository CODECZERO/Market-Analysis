"""
Handler Registry - Open/Closed Principle.

New handlers can be registered without modifying existing code.
Uses factory pattern for dependency injection.
"""
from __future__ import annotations

from typing import Dict, Optional, Type

from .base import BaseTaskHandler
from .lead_handler import LeadIntentHandler
from .crisis_handler import CrisisHandler
from .competitor_handler import CompetitorGapHandler


class HandlerRegistry:
    """
    Registry for task handlers following Dependency Inversion.
    """

    def __init__(self):
        self._handlers: Dict[str, BaseTaskHandler] = {}

    def register(self, handler: BaseTaskHandler) -> None:
        """Register a handler instance."""
        self._handlers[handler.task_type] = handler

    def get(self, task_type: str) -> Optional[BaseTaskHandler]:
        """Get handler for task type, or None if not found."""
        return self._handlers.get(task_type)

    def has(self, task_type: str) -> bool:
        """Check if handler exists for task type."""
        return task_type in self._handlers


def create_default_registry(llm_adapter) -> HandlerRegistry:
    """
    Factory function to create registry with default handlers.
    
    Args:
        llm_adapter: LLM adapter instance for AI tasks.
    
    Returns:
        Configured HandlerRegistry with all handlers registered.
    """
    registry = HandlerRegistry()
    
    # Register all handlers (OCP: add new handlers here)
    registry.register(LeadIntentHandler(llm_adapter))
    registry.register(CrisisHandler(llm_adapter))
    registry.register(CompetitorGapHandler(llm_adapter))
    
    return registry


__all__ = [
    "BaseTaskHandler",
    "HandlerRegistry",
    "create_default_registry",
    "LeadIntentHandler",
    "CrisisHandler",
    "CompetitorGapHandler",
]
