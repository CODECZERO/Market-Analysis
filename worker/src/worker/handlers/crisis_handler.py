"""Crisis Handler - Single Responsibility Principle."""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseTaskHandler


class CrisisHandler(BaseTaskHandler):
    """Handles analyze_crisis task type."""

    def __init__(self, llm_adapter):
        self._llm = llm_adapter

    @property
    def task_type(self) -> str:
        return "analyze_crisis"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mentions = payload.get("mentions", [])
        if not mentions:
            return {"status": "empty"}
        analysis = await self._llm.analyze_crisis(mentions)
        return analysis
