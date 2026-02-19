"""Pydantic models shared across the worker."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


from enum import Enum

class Intent(str, Enum):
    HOT_LEAD = "HOT_LEAD"
    CHURN_RISK = "CHURN_RISK"
    GENERAL = "GENERAL"

class StrategicTag(str, Enum):
    OPPORTUNITY_TO_STEAL = "OPPORTUNITY_TO_STEAL"
    CRITICAL_ALERT = "CRITICAL_ALERT"
    NONE = "NONE"


class Emotions(BaseModel):
    """Emotion scores from enhanced analysis."""
    joy: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    sadness: float = 0.0
    surprise: float = 0.0
    disgust: float = 0.0


class EnhancedAnalysis(BaseModel):
    """Enhanced analysis results from LLM."""
    sentiment_score: float = 0.0  # -1.0 to +1.0
    sentiment_label: str = "neutral"  # positive, neutral, negative
    emotions: Emotions = Field(default_factory=Emotions)
    is_sarcastic: bool = False
    urgency: str = "low"  # high, medium, low
    topics: list[str] = Field(default_factory=list)
    # Accept entities as either strings or dicts with 'name' field
    entities: dict[str, list[Any]] = Field(default_factory=lambda: {"people": [], "companies": [], "products": []})
    language: str = "en"
    
    # New Business Intelligence Fields
    feature_requests: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    churn_risks: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    lead_score: int = 0  # 0-100 sales priority score


class Mention(BaseModel):
    id: str
    source: str
    text: str
    author: str | None = None
    url: str | None = None
    created_at: datetime
    sentiment: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
    # Influencer stats
    author_followers: int = 0
    influence_score: float = 0.0
    # Enhanced analysis fields
    enhanced_analysis: EnhancedAnalysis | None = None
    # Business Intelligence fields for Command Center
    intent: Intent = Intent.GENERAL
    strategic_tag: StrategicTag = StrategicTag.NONE


class ChunkMeta(BaseModel):
    chunk_index: int | None = Field(default=None, alias="chunkIndex")
    total_chunks: int | None = Field(default=None, alias="totalChunks")
    keywords: list[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Chunk(BaseModel):
    brand: str
    chunk_id: str = Field(alias="chunkId")
    created_at: datetime = Field(alias="createdAt")
    mentions: list[Mention]
    meta: ChunkMeta | None = None

    class Config:
        populate_by_name = True


class ClusterResult(BaseModel):
    cluster_id: int
    count: int
    examples: list[str]
    summary: str | None
    spike: bool
    sentiment: dict[str, float]
    topics: list[str] | None = None
    # Enhanced analysis aggregates for cluster
    enhanced_analysis: EnhancedAnalysis | None = None


class ChunkMetrics(BaseModel):
    preprocessing_time_ms: float = 0.0
    embedding_time_ms: float = 0.0
    clustering_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    spike_detection_time_ms: float = 0.0
    io_time_ms: float = 0.0
    total_task_time_ms: float = 0.0


class ChunkResult(BaseModel):
    chunk_id: str
    brand: str
    timestamp: int
    clusters: list[ClusterResult]
    metrics: ChunkMetrics
    summary: str | None = None
    topics: list[str] | None = None
    spikeDetected: bool = False
    meta: dict[str, Any] | None = None
    # Business Intelligence Aggregates - Accept both strings and dicts from LLM
    entities: dict[str, list[Any]] = Field(default_factory=lambda: {"people": [], "companies": [], "products": []})
    action_suggested: str | None = None
    
    # New Business Intelligence Aggregates - Accept both strings and dicts
    feature_requests: list[Any] = Field(default_factory=list)
    pain_points: list[Any] = Field(default_factory=list)
    churn_risks: list[Any] = Field(default_factory=list)
    recommended_actions: list[Any] = Field(default_factory=list)


class FailureRecord(BaseModel):
    worker_id: str
    brand: str
    chunk_id: str
    reason: str
    payload: str
