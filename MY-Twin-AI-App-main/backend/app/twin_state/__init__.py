"""
Twin State – خدمات حالة التوأم والعلاقة (متوافقة مع TCMA)
==============================================================
- attachment_service: كشف نمط التعلق
- personality_state: حالة التوأم الداخلية
- user_service: نموذج المستخدم الموحد
- relationship_service: حالة العلاقة
- intent_service: كشف نية المستخدم
- journey_service: مراحل رحلة المستخدم
- identity_service: هوية التوأم
- emotional_service: تحليل المشاعر
- emotional_timeline: الخط الزمني للمشاعر
"""
from .attachment_service import detect as detect_attachment, get_adjustments
from .personality_state import (
    load as load_personality,
    reflect as reflect_personality,
    add_objective,
    get_objectives,
    update_profile,
    get_profile,
    get_state_summary,
)
from .user_service import user_model
from .relationship_service import (
    load as load_relationship,
    update as update_relationship,
    detect_intent,
)
from .intent_service import intent_engine
from .journey_service import (
    get_phase,
    get_current_phase,
    get_behavior,
    get_daily_message,
    get_recommendation,
    calculate_score,
)
from .identity_service import (
    get_identity as get_twin_identity,
    evolve as evolve_twin_identity,
    get_traits as get_twin_traits,
)
from .emotional_service import emotional_service
from .emotional_timeline import emotional_timeline

__all__ = [
    # Attachment
    "detect_attachment", "get_adjustments",
    # Personality
    "load_personality", "reflect_personality", "add_objective", "get_objectives",
    "update_profile", "get_profile", "get_state_summary",
    # User
    "user_model",
    # Relationship
    "load_relationship", "update_relationship", "detect_intent",
    # Intent
    "intent_engine",
    # Journey
    "get_phase", "get_current_phase", "get_behavior", "get_daily_message",
    "get_recommendation", "calculate_score",
    # Identity
    "get_twin_identity", "evolve_twin_identity", "get_twin_traits",
    # Emotional
    "emotional_service", "emotional_timeline",
]
