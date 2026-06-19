"""Event model – typed events for the Event Bus."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    MEMORY_CREATED = "memory_created"
    MEMORY_RETRIEVED = "memory_retrieved"
    TRUST_INCREASED = "trust_increased"
    STAGE_CHANGED = "stage_changed"
    GOAL_COMPLETED = "goal_completed"
    GOAL_CREATED = "goal_created"
    VOICE_GENERATED = "voice_generated"
    COUNCIL_TRIGGERED = "council_triggered"
    REFLECTION_COMPLETED = "reflection_completed"
    STREAK_UPDATED = "streak_updated"
    TIER_CHANGED = "tier_changed"
    ATTACHMENT_DETECTED = "attachment_detected"
    JOURNEY_PHASE_CHANGED = "journey_phase_changed"
    IDENTITY_EVOLVED = "identity_evolved"
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


# Factory
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
    }
    cls = mapping.get(event_type, BaseEvent)
    return cls(type=event_type, user_id=user_id, **kwargs)
