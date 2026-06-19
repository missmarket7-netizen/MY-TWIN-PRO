"""Rituals – morning & evening rituals with the twin."""
import logging, random
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.twin_state.journey_service import get_phase, get_behavior
from app.repositories.profile_repository import get_profile
from app.twin_state.relationship_service import load as load_relationship

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
    "mature": [
        {"ar": "صباح الحكمة! يوم جديد مليء بالفرص", "en": "Good morning! A new day full of opportunities"},
        {"ar": "صباح الامتنان! ما أكثر شيء ممتن له اليوم؟", "en": "Good morning! What are you most grateful for today?"},
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
    "mature": [
        {"ar": "مساء الخير. تأمل في يومك بهدوء", "en": "Good evening. Reflect on your day calmly"},
        {"ar": "وقت التأمل. ما الدرس الذي خرجت به اليوم؟", "en": "Reflection time. What lesson did you take away today?"},
    ],
}


async def get_morning_ritual(user_id: str, lang: str = "ar") -> Optional[str]:
    profile, relationship = await _gather(get_profile(user_id), load_relationship(user_id))
    if not profile or not relationship:
        return None

    phase = await get_phase(relationship.bond_level)
    pool = MORNING_RITUALS.get(phase, MORNING_RITUALS["introduction"])
    today = datetime.now(timezone.utc).date().isoformat()
    seed = hash(f"morning:{user_id}:{today}") % len(pool)
    return pool[seed].get(lang, pool[seed].get("ar", ""))


async def get_evening_ritual(user_id: str, lang: str = "ar") -> Optional[str]:
    profile, relationship = await _gather(get_profile(user_id), load_relationship(user_id))
    if not profile or not relationship:
        return None

    phase = await get_phase(relationship.bond_level)
    pool = EVENING_RITUALS.get(phase, EVENING_RITUALS["introduction"])
    today = datetime.now(timezone.utc).date().isoformat()
    seed = hash(f"evening:{user_id}:{today}") % len(pool)
    return pool[seed].get(lang, pool[seed].get("ar", ""))


async def _gather(*coros):
    import asyncio
    results = await asyncio.gather(*coros, return_exceptions=True)
    return [r if not isinstance(r, Exception) else None for r in results]
