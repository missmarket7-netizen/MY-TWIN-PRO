"""Event model v2.0 – جميع أحداث MyTwin (TCMA، الميزات، المحركات)"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    # الأحداث الأساسية
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    # الذاكرة (TCMA)
    MEMORY_CREATED = "memory_created"
    MEMORY_RETRIEVED = "memory_retrieved"
    REFLECTION_COMPLETED = "reflection_completed"
    EMOTIONAL_PATTERN_DETECTED = "emotional_pattern_detected"
    GRAPH_EDGE_CREATED = "graph_edge_created"
    # العلاقة
    TRUST_INCREASED = "trust_increased"
    STAGE_CHANGED = "stage_changed"
    ATTACHMENT_DETECTED = "attachment_detected"
    JOURNEY_PHASE_CHANGED = "journey_phase_changed"
    # الأهداف
    GOAL_COMPLETED = "goal_completed"
    GOAL_CREATED = "goal_created"
    # الهوية
    IDENTITY_EVOLVED = "identity_evolved"
    # الدراسة (ATHENA)
    STUDY_SESSION_STARTED = "study_session_started"
    CONCEPT_MASTERED = "concept_mastered"
    # الأعمال (GROWTH-HIVE)
    BUSINESS_IDEA_GENERATED = "business_idea_generated"
    FEASIBILITY_COMPLETED = "feasibility_completed"
    # المحتوى (CREATOR)
    CONTENT_GENERATED = "content_generated"
    BOOK_COMPLETED = "book_completed"
    # البرمجة (CODE LAB)
    CODE_GENERATED = "code_generated"
    PROJECT_SCAFFOLDED = "project_scaffolded"
    # الأحلام
    DREAM_ANALYZED = "dream_analyzed"
    # مدرب الحياة
    LIFE_COACH_SESSION = "life_coach_session"
    # المنزل الذكي
    SMART_HOME_COMMAND = "smart_home_command"
    # المهام (P.A.S.S.)
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    # الاستباقية
    PROACTIVE_MESSAGE_SENT = "proactive_message_sent"
    # الصوت
    VOICE_GENERATED = "voice_generated"
    # النظام
    COUNCIL_TRIGGERED = "council_triggered"
    STREAK_UPDATED = "streak_updated"
    TIER_CHANGED = "tier_changed"
    ENERGY_CHANGED = "energy_changed"


class BaseEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt_{int(datetime.now(timezone.utc).timestamp())}")
    type: EventType
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MessageEvent(BaseEvent):
    type: EventType = EventType.MESSAGE_RECEIVED
    content: str = ""
    intent: str = "general"
    lang: str = "ar"


class MemoryEvent(BaseEvent):
    type: EventType = EventType.MEMORY_CREATED
    memory_id: Optional[str] = None
    content: str = ""
    memory_type: str = "daily"
    importance: float = 0.5


class TrustEvent(BaseEvent):
    type: EventType = EventType.TRUST_INCREASED
    old_bond: float = 0.0
    new_bond: float = 0.0
    old_stage: str = "stranger"
    new_stage: str = "stranger"


class GoalEvent(BaseEvent):
    type: EventType = EventType.GOAL_COMPLETED
    goal_id: Optional[str] = None
    title: str = ""


class StageChangeEvent(BaseEvent):
    type: EventType = EventType.STAGE_CHANGED
    old_stage: str = "stranger"
    new_stage: str = "stranger"
    message_ar: str = ""
    message_en: str = ""


class AttachmentEvent(BaseEvent):
    type: EventType = EventType.ATTACHMENT_DETECTED
    style: str = "unknown"
    confidence: float = 0.0


class ReflectionEvent(BaseEvent):
    type: EventType = EventType.REFLECTION_COMPLETED
    summary: str = ""
    lang: str = "ar"


# ==== نماذج جديدة للميزات المطورة ====
class StudySessionEvent(BaseEvent):
    type: EventType = EventType.STUDY_SESSION_STARTED
    concept: str = ""
    age_group: str = "teen"


class BusinessIdeaEvent(BaseEvent):
    type: EventType = EventType.BUSINESS_IDEA_GENERATED
    idea: str = ""
    budget: float = 0.0


class CodeGenerationEvent(BaseEvent):
    type: EventType = EventType.CODE_GENERATED
    module: str = ""
    language: str = "Python"


class DreamAnalysisEvent(BaseEvent):
    type: EventType = EventType.DREAM_ANALYZED
    symbols: list = Field(default_factory=list)
    emotions: list = Field(default_factory=list)


class ProactiveEvent(BaseEvent):
    type: EventType = EventType.PROACTIVE_MESSAGE_SENT
    message: str = ""


class TaskEvent(BaseEvent):
    type: EventType = EventType.TASK_CREATED
    title: str = ""
    due_date: Optional[str] = None


# Factory (محدثة)
def create_event(event_type: EventType, user_id: str, **kwargs) -> BaseEvent:
    mapping = {
        EventType.MESSAGE_RECEIVED: MessageEvent,
        EventType.MEMORY_CREATED: MemoryEvent,
        EventType.TRUST_INCREASED: TrustEvent,
        EventType.STAGE_CHANGED: StageChangeEvent,
        EventType.GOAL_COMPLETED: GoalEvent,
        EventType.GOAL_CREATED: GoalEvent,
        EventType.ATTACHMENT_DETECTED: AttachmentEvent,
        EventType.REFLECTION_COMPLETED: ReflectionEvent,
        EventType.STUDY_SESSION_STARTED: StudySessionEvent,
        EventType.BUSINESS_IDEA_GENERATED: BusinessIdeaEvent,
        EventType.CODE_GENERATED: CodeGenerationEvent,
        EventType.DREAM_ANALYZED: DreamAnalysisEvent,
        EventType.PROACTIVE_MESSAGE_SENT: ProactiveEvent,
        EventType.TASK_CREATED: TaskEvent,
        EventType.TASK_COMPLETED: TaskEvent,
    }
    cls = mapping.get(event_type, BaseEvent)
    return cls(type=event_type, user_id=user_id, **kwargs)
