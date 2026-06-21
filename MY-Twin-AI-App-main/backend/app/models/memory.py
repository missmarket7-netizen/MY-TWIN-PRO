"""Memory Model v2.0 – نموذج موحد للذاكرة (TCMA Layers)"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone


class RawArchive(BaseModel):
    """الطبقة 1: الأرشيف الخام"""
    id: Optional[str] = None
    user_id: str
    content: str = Field(..., max_length=5000)
    role: str = "user"  # user | twin
    emotion_primary: Optional[str] = None
    emotion_intensity: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    detected_intent: Optional[str] = None
    language: str = "ar"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EmotionalMemory(BaseModel):
    """الطبقة 4: الذاكرة العاطفية"""
    id: Optional[str] = None
    user_id: str
    expressed_text: str
    expressed_emotion: str
    real_emotion: str = "neutral"
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    trigger: Optional[str] = None
    cultural_context: Optional[str] = None
    person_links: List[Dict] = Field(default_factory=list)
    arabic_category: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReflectionInsight(BaseModel):
    """الطبقة 8: استنتاج تأملي"""
    id: Optional[str] = None
    user_id: str
    insight_type: str = "general"
    insight_text: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    related_person_id: Optional[str] = None
    related_emotion: Optional[str] = None
    occurrence_count: int = 1
    first_observed: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_observed: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GraphEdge(BaseModel):
    """الطبقة 11: حافة في الرسم البياني للذاكرة"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = Field(default=1.0)
    metadata: Dict = Field(default_factory=dict)


class PersonNode(BaseModel):
    """عقدة شخص في شبكة المعارف"""
    id: Optional[str] = None
    user_id: str
    name: str
    relationship_type: str = "unknown"
    importance_score: float = Field(default=30.0, ge=0.0, le=100.0)
    mention_count: int = 1
    emotional_associations: List[Dict] = Field(default_factory=list)
    sensitive_topics: List[str] = Field(default_factory=list)


class UserKnowledge(BaseModel):
    """حالة معرفة المستخدم (للدراسة)"""
    concept_id: str
    concept_name: str
    mastery_level: float = Field(default=0.1, ge=0.0, le=1.0)
    ease_factor: float = Field(default=2.5)
    interval_days: int = 0
    repetition_count: int = 0
    next_review_date: Optional[str] = None


class UnifiedMemory(BaseModel):
    """نموذج ذاكرة موحد – يضم كل الطبقات"""
    raw_archive: List[RawArchive] = Field(default_factory=list)
    emotional: List[EmotionalMemory] = Field(default_factory=list)
    reflections: List[ReflectionInsight] = Field(default_factory=list)
    graph_edges: List[GraphEdge] = Field(default_factory=list)
    people: List[PersonNode] = Field(default_factory=list)
    knowledge: List[UserKnowledge] = Field(default_factory=list)
