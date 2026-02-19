"""Competitor Gap Handler - Single Responsibility Principle."""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseTaskHandler


class CompetitorGapHandler(BaseTaskHandler):
    """Handles analyze_competitor_gap task type."""

    def __init__(self, llm_adapter):
        self._llm = llm_adapter

    @property
    def task_type(self) -> str:
        return "analyze_competitor_gap"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mentions = payload.get("mentions", [])
        if not mentions:
            return {"status": "empty"}
        analysis = await self._llm.analyze_competitor_gap(mentions)
        return analysis
