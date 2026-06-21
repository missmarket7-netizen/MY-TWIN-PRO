"""Relationship model v2.0 – متكامل مع TCMA"""
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
    stage: str = Field(default="stranger")
    dims: RelationshipDims = Field(default_factory=RelationshipDims)
    interaction_count: int = Field(default=0)
    relationship_health: float = Field(default=100.0, ge=0.0, le=100.0)
    previous_stage: Optional[str] = None
    attachment_style: Optional[str] = None  # جديد: من TCMA
    trust_velocity: float = Field(default=0.0)  # جديد: سرعة تغير الثقة
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EmotionState(BaseModel):
    primary: str = Field(default="neutral")
    secondary: Optional[str] = None
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    arousal: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)  # جديد: ثقة التحليل
    method: str = Field(default="local")  # جديد: tcma_arabic_engine أو local
    trend: Optional[str] = None
    risk_level: Optional[str] = None  # low, medium, high
    needs_support: bool = Field(default=False)


class Intent(BaseModel):
    primary: str = Field(default="general")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    secondary: List[str] = Field(default_factory=list)
    all_scores: Dict[str, float] = Field(default_factory=dict)  # جديد: كل النوايا المحتملة


class AttachmentProfile(BaseModel):
    """ملف التعلق – متوافق مع TCMA Attachment Model"""
    style: str = Field(default="unknown")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    description: str = ""
    metrics: Dict[str, float] = Field(default_factory=dict)
    recommendation: str = ""


class MemoryGraphNode(BaseModel):
    """عقدة في الرسم البياني للذاكرة"""
    memory_id: str
    memory_type: str
    content_summary: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryGraphEdge(BaseModel):
    """حافة بين ذكرَيين"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = Field(default=1.0)
    metadata: Dict = Field(default_factory=dict)
