"""
Rituals v2.0 – طقوس صباحية ومسائية (متكاملة مع TCMA)
=========================================================
تستخدم ذاكرة العلاقات والحالة العاطفية لتخصيص الطقوس.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

try:
    from app.memory.relationship.relationship_memory import get_relationship_insights
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response
    from app.memory.identity.identity_model import get_identity
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("rituals")

MORNING_RITUALS = {
    "introduction": [
        {"ar": "صباح الخير! ما هو مزاجك اليوم؟", "en": "Good morning! How's your mood today?"},
        {"ar": "صباح النور! هل نمت جيداً؟", "en": "Good morning! Did you sleep well?"},
    ],
    "trust_building": [
        {"ar": "صباح الخير! ما خطتك لليوم؟", "en": "Good morning! What's your plan today?"},
        {"ar": "صباح الفل! جاهز نبدأ يومنا معاً؟", "en": "Good morning! Ready to start our day together?"},
    ],
    "deepening": [
        {"ar": "صباح الحب! فكرت فيك وأنا متحمس ليومنا", "en": "Good morning! Thought of you, excited for our day"},
        {"ar": "صباح الورد! ما أكثر شيء متحمس له اليوم؟", "en": "Good morning! What are you most excited about today?"},
    ],
    "growth": [
        {"ar": "صباح العزيمة! تذكر هدفك وابدأ يومك بقوة", "en": "Good morning! Remember your goal and start strong"},
        {"ar": "صباح التحدي! خطوة واحدة تقربك من حلمك اليوم", "en": "Good morning! One step closer to your dream today"},
    ],
}

EVENING_RITUALS = {
    "introduction": [
        {"ar": "كيف كان يومك؟", "en": "How was your day?"},
        {"ar": "ما أجمل شيء حدث اليوم؟", "en": "What was the best thing today?"},
    ],
    "trust_building": [
        {"ar": "كيف كان يومك؟ شاركني التفاصيل", "en": "How was your day? Share the details"},
        {"ar": "ما الذي تعلمته اليوم؟", "en": "What did you learn today?"},
    ],
    "deepening": [
        {"ar": "تصبح على خير. ما أكثر شعور رافقك اليوم؟", "en": "Good night. What feeling stayed with you today?"},
        {"ar": "قبل النوم، ما أكثر شيء تشعر بالامتنان له؟", "en": "Before sleep, what are you most grateful for?"},
    ],
    "growth": [
        {"ar": "أحسنت اليوم! هل اقتربت من هدفك؟", "en": "Well done today! Did you get closer to your goal?"},
        {"ar": "فخور بك! كيف كان تقدمك اليوم؟", "en": "Proud of you! How was your progress today?"},
    ],
}

async def get_relationship_phase(user_id: str) -> str:
    """تحديد مرحلة العلاقة من TCMA"""
    if not TCMA_AVAILABLE:
        return "introduction"
    try:
        rel = await get_relationship_insights(user_id)
        trust = rel.get("trust_level", 0) if rel else 0
        if trust > 60: return "growth"
        elif trust > 35: return "deepening"
        elif trust > 15: return "trust_building"
        return "introduction"
    except:
        return "introduction"

async def get_morning_ritual(user_id: str, lang: str = "ar") -> Optional[str]:
    phase = await get_relationship_phase(user_id)
    pool = MORNING_RITUALS.get(phase, MORNING_RITUALS["introduction"])
    today = datetime.now(timezone.utc).date().isoformat()
    seed = hash(f"morning:{user_id}:{today}") % len(pool)
    return pool[seed].get(lang, pool[seed].get("ar", ""))

async def get_evening_ritual(user_id: str, lang: str = "ar") -> Optional[str]:
    phase = await get_relationship_phase(user_id)
    pool = EVENING_RITUALS.get(phase, EVENING_RITUALS["introduction"])
    today = datetime.now(timezone.utc).date().isoformat()
    seed = hash(f"evening:{user_id}:{today}") % len(pool)
    return pool[seed].get(lang, pool[seed].get("ar", ""))

logger.info("✅ Rituals v2.0 initialized")
