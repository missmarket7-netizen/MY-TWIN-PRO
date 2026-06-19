"""Relationship model – bond dimensions, stages, emotions."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, timezone


class RelationshipDims(BaseModel):
    trust: float = Field(default=0.0, ge=0.0, le=100.0)
    comfort: float = Field(default=0.0, ge=0.0, le=100.0)
    openness: float = Field(default=0.0, ge=0.0, le=100.0)
    attachment: float = Field(default=0.0, ge=0.0, le=100.0)
    romantic: float = Field(default=0.0, ge=0.0, le=100.0)
    humor: float = Field(default=0.0, ge=0.0, le=100.0)
    consistency: float = Field(default=0.0, ge=0.0, le=100.0)
    shared_history: float = Field(default=0.0, ge=0.0, le=100.0)
    att_style: float = Field(default=0.0, ge=0.0, le=100.0)


class RelationshipState(BaseModel):
    user_id: str
    bond_level: float = Field(default=0.0, ge=0.0, le=100.0)
    stage: str = Field(default="stranger")  # stranger → soul_twin
    dims: RelationshipDims = Field(default_factory=RelationshipDims)
    interaction_count: int = Field(default=0)
    relationship_health: float = Field(default=100.0, ge=0.0, le=100.0)
    previous_stage: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EmotionState(BaseModel):
    primary: str = Field(default="neutral")
    secondary: Optional[str] = None
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    arousal: float = Field(default=0.5, ge=0.0, le=1.0)
    trend: Optional[str] = None
    riskLevel: Optional[str] = None
    needsSupport: bool = Field(default=False)


class Intent(BaseModel):
    primary: str = Field(default="general")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    secondary: List[str] = Field(default_factory=list)
