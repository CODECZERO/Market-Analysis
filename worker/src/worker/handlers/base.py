"""Base Task Handler - Abstract Base Class following SOLID principles."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTaskHandler(ABC):
    """
    BaseTaskHandler - Abstract Base Class for all task handlers.
    
    Follows:
    - SRP: Each handler has single responsibility
    - OCP: New handlers extend without modifying existing code
    - LSP: All handlers are substitutable
    - DIP: Depend on abstraction, not concrete implementations
    """

    @property
    @abstractmethod
    def task_type(self) -> str:
        """Return the task type identifier (e.g., 'analyze_lead_intent')."""
        pass

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task and return result."""
        pass
