"""
Models – نماذج بيانات MyTwin (متوافقة مع TCMA وجميع الميزات)
=============================================================
- profile: الملف الشخصي وإعدادات الصوت
- relationship: أبعاد العلاقة والعواطف والنوايا
- memory: نموذج الذاكرة الموحد (جميع طبقات TCMA)
- goal: الأهداف والمهام
- tier: باقات الاشتراك والميزات
- event: أحداث النظام (Event Bus)
- voice: إعدادات الصوت (ذكوري/أنثوي)
"""
from .profile import UserProfile, VoiceConfig, TierConfig
from .relationship import (
    RelationshipDims,
    RelationshipState,
    EmotionState,
    Intent,
    AttachmentProfile,
    MemoryGraphNode,
    MemoryGraphEdge,
)
from .memory import (
    RawArchive,
    EmotionalMemory,
    ReflectionInsight,
    GraphEdge,
    PersonNode,
    UserKnowledge,
    UnifiedMemory,
)
from .goal import Goal
from .tier import TIER_CONFIGS, get_tier_config
from .event import (
    EventType,
    BaseEvent,
    create_event,
    MessageEvent,
    MemoryEvent,
    TrustEvent,
    StageChangeEvent,
    GoalEvent,
    AttachmentEvent,
    ReflectionEvent,
    StudySessionEvent,
    BusinessIdeaEvent,
    CodeGenerationEvent,
    DreamAnalysisEvent,
    ProactiveEvent,
    TaskEvent,
)
from .voice import (
    VoiceConfig as VoiceModelConfig,
    get_voice_personality,
    get_default_voice_id,
    get_gender_voice_options,
    DEFAULT_VOICES,
)

__all__ = [
    # Profile
    "UserProfile", "VoiceConfig", "TierConfig",
    # Relationship
    "RelationshipDims", "RelationshipState", "EmotionState", "Intent",
    "AttachmentProfile", "MemoryGraphNode", "MemoryGraphEdge",
    # Memory (TCMA)
    "RawArchive", "EmotionalMemory", "ReflectionInsight", "GraphEdge",
    "PersonNode", "UserKnowledge", "UnifiedMemory",
    # Goal
    "Goal",
    # Tier
    "TIER_CONFIGS", "get_tier_config",
    # Events
    "EventType", "BaseEvent", "create_event", "MessageEvent", "MemoryEvent",
    "TrustEvent", "StageChangeEvent", "GoalEvent", "AttachmentEvent",
    "ReflectionEvent", "StudySessionEvent", "BusinessIdeaEvent",
    "CodeGenerationEvent", "DreamAnalysisEvent", "ProactiveEvent", "TaskEvent",
    # Voice
    "VoiceModelConfig", "get_voice_personality", "get_default_voice_id",
    "get_gender_voice_options", "DEFAULT_VOICES",
]
