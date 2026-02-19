"""Configuration handling for the Service 3 worker."""
from __future__ import annotations

import uuid
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URI")
    mongo_url: str | None = Field(default=None, description="MongoDB connection URI")
    worker_id: str | None = Field(default=None, description="Unique worker identifier")
    chunk_batch_size: int = Field(default=5, ge=1, description="Process 5-10 mentions per batch to avoid large data chunks")
    embeddings_provider: Literal["local", "ollama", "nvidia"] = "nvidia"
    llm_provider: Literal["ollama", "nvidia", "openrouter"] = "nvidia"  # Now supports nvidia, openrouter

    @model_validator(mode="after")
    def _validate_llm_configuration(self) -> "Settings":
        if self.llm_provider == "nvidia" and not self.nvidia_api_key:
             pass 
        if self.llm_provider == "openrouter" and not self.openrouter_api_key:
             pass
        if self.llm_provider not in ["ollama", "nvidia", "openrouter"]:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.llm_provider}")
        if self.embeddings_provider not in ["local", "ollama", "nvidia"]:
            raise ValueError("Only 'local', 'ollama' or 'nvidia' supported for EMBEDDINGS_PROVIDER")
        return self
    
    # NVIDIA Configuration
    nvidia_api_key: str | None = Field(default=None, description="NVIDIA API Key")
    nvidia_model: str = Field(default="meta/llama-3.3-70b-instruct", description="NVIDIA Model Name")

    # OpenRouter Configuration
    openrouter_api_key: str | None = Field(default=None, description="OpenRouter API Key")
    openrouter_model: str = Field(default="openai/gpt-4o", description="OpenRouter Model Name")

    # Groq Configuration
    groq_api_key: str | None = Field(default=None, description="Groq API Key")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq Model Name")

    # Local LLM (Ollama) Configuration
    use_local_llm: bool = Field(default=True, description="Use local LLM (Ollama) instead of cloud providers")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server base URL")
    ollama_model: str = Field(default="llama3.2", description="Ollama model name to use")
    
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_base: float = Field(default=0.5, ge=0.0)
    prometheus_port: int = Field(default=9090, ge=1)
    http_host: str = Field(default="0.0.0.0", description="HTTP Host")
    http_port: int = Field(default=8001, ge=1)
    log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"
    heartbeat_interval_sec: int = Field(default=30, ge=1)
    blpop_timeout_sec: int = Field(default=5, ge=1)
    redis_queue_prefix: str = Field(default="queue:brand:", description="Prefix for brand queues")
    redis_result_prefix: str = Field(default="result:brand:", description="Prefix for result queues")
    redis_failed_prefix: str = Field(default="failed:brand:", description="Prefix for failure queues")
    redis_summary_prefix: str = Field(default="summary:brand:", description="Prefix for brand summary")
    redis_spike_prefix: str = Field(default="spike:", description="Prefix for spike history")
    spike_history_ttl_sec: int = Field(default=3600, ge=60)
    llm_summary_max_tokens: int = Field(default=256, ge=16)
    llm_timeout_sec: int = Field(default=180, ge=1)
    
    # Training Data Collection
    training_data_path: str = Field(default="data/training_data.jsonl", description="Path to save LLM interactions for fine-tuning")
    
    @field_validator("llm_timeout_sec")
    @classmethod
    def _enforce_min_timeout(cls, v: int) -> int:
        if v < 120:
            return 120
        return v

    llm_min_delay_sec: float = Field(default=1.0, ge=0.0, description="Minimum 1 second between LLM calls")
    embeddings_batch_size: int = Field(default=32, ge=1)
    metrics_wait_log_interval_sec: int = Field(default=60, ge=1)
    preprocessing_examples: int = Field(default=5, ge=1)
    llm_max_concurrency: int = Field(default=1, ge=1, description="Process 1 LLM request at a time (lower for local Ollama)")
    llm_rate_limit_rpm: int = Field(default=40, ge=1, description="Rate limit (RPM) for LLM calls - 40 per minute")

    model_config = SettingsConfigDict(
        # Load from project root .env (parents: config.py -> worker -> src -> worker_dir -> root)
        # Update: config.py is in src/worker.
        # parents[0] = src/worker
        # parents[1] = src
        # parents[2] = worker output dir (if running from there?) NO.
        # file: worker/src/worker/config.py
        # parents[0]=worker/src/worker
        # parents[1]=worker/src
        # parents[2]=worker
        # parents[3]=Brand-Mention-Reputation-Tracker (Root)
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_prefix="",
        case_sensitive=False,
        extra="ignore"  # Allow extra environment variables
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (env_settings, dotenv_settings, init_settings, file_secret_settings)

    def __init__(self, **data):
        super().__init__(**data)
        self._generated_worker_id: str | None = None

    @property
    def effective_worker_id(self) -> str:
        if self.worker_id:
            return self.worker_id
        if self._generated_worker_id is None:
            self._generated_worker_id = f"worker-{uuid.uuid4()}"
        return self._generated_worker_id


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
