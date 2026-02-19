"""Service for collecting and saving LLM training data."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .config import get_settings
from .logger import get_logger

logger = get_logger(__name__)

class TrainingExample(BaseModel):
    """Schema for a single training example (Unsloth/OpenAI compatible)."""
    
    timestamp: str = Field(..., description="ISO 8601 timestamp of data capture")
    worker_id: str = Field(..., description="ID of the capturing worker")
    brand: str = Field(..., description="Brand context")
    operation: str = Field(..., description="Type of operation (e.g., summary, sentiment)")
    
    # Core Training Data
    input_text: str = Field(..., description="The prompt or input text provided to the LLM")
    output_json: str = Field(..., description="The structured output received from the LLM (Serialized JSON)")
    
    # Metadata for filtering/quality control
    model_used: str = Field(..., description="Name of the model that generated this")
    latency_ms: float = Field(default=0.0, description="Response time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class TrainingDataCollector:
    """Collects and persists LLM interactions for future fine-tuning."""

    def __init__(self, worker_id: str):
        self._settings = get_settings()
        self._worker_id = worker_id
        self._file_path = self._settings.training_data_path
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the data directory exists."""
        try:
            directory = os.path.dirname(self._file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create training data directory: {e}")

    def collect(
        self,
        input_text: str,
        output_data: Any,
        brand: str,
        operation: str,
        model: str,
        latency_ms: float = 0.0,
        extra_metadata: Dict[str, Any] = None
    ) -> None:
        """
        Record a training example. 
        Fire-and-forget: Scheduled on the event loop to avoid blocking main execution.
        """
        try:
            # Ensure output is always a string (serialized JSON if it's a dict/list)
            # This prevents mixed-type errors in 'datasets' library
            if isinstance(output_data, (dict, list)):
                final_output = json.dumps(output_data, ensure_ascii=False)
            else:
                final_output = str(output_data)

            example = TrainingExample(
                timestamp=datetime.now().isoformat(),
                worker_id=self._worker_id,
                brand=brand,
                operation=operation,
                input_text=input_text,
                output_json=final_output,
                model_used=model,
                latency_ms=latency_ms,
                metadata=extra_metadata or {}
            )
            
            # Run file I/O in thread pool to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, self._append_to_file, example)
            
        except Exception as e:
            # Never crash the worker for logging failure
            logger.warning(f"Failed to queue training data collection: {e}")

    def _append_to_file(self, example: TrainingExample) -> None:
        """Synchronous file append (runs in thread)."""
        try:
            # JSONL format: One valid JSON object per line
            line = example.model_dump_json() + "\n"
            
            # Atomic append on POSIX (mostly safe for this volume)
            with open(self._file_path, "a", encoding="utf-8") as f:
                f.write(line)
                
        except Exception as e:
            logger.error(f"Failed to write to training data file {self._file_path}: {e}")
