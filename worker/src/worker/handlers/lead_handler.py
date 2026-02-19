"""Lead Intent Handler - Single Responsibility Principle."""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseTaskHandler


class LeadIntentHandler(BaseTaskHandler):
    """Handles analyze_lead_intent task type."""

    def __init__(self, llm_adapter):
        self._llm = llm_adapter

    @property
    def task_type(self) -> str:
        return "analyze_lead_intent"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "")
        analysis = await self._llm.analyze_lead_intent(text)
        return analysis
