"""Challenges – daily & weekly personalized challenges."""
import logging, random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.repositories.profile_repository import get_profile
from app.twin_state.relationship_service import load as load_relationship
from app.twin_state.journey_service import get_phase
from app.repositories.goals_repository import get_active

logger = logging.getLogger("challenges")

CHALLENGE_POOL = {
    "introduction": [
        {"ar": "شارك توأمك بشيء واحد يجعلك سعيداً اليوم", "en": "Share one thing that made you happy today"},
        {"ar": "اسأل توأمك سؤالاً شخصياً", "en": "Ask your twin a personal question"},
        {"ar": "اكتب 3 أشياء تشعر بالامتنان لها", "en": "Write 3 things you're grateful for"},
    ],
    "trust_building": [
        {"ar": "أخبر توأمك عن ذكرى الطفولة المفضلة", "en": "Tell your twin your favorite childhood memory"},
        {"ar": "شارك شيئاً يقلقك هذا الأسبوع", "en": "Share something worrying you this week"},
        {"ar": "حدد هدفاً صغيراً للغد", "en": "Set a small goal for tomorrow"},
    ],
    "deepening": [
        {"ar": "تأمل في مشاعرك اليوم وشاركها", "en": "Reflect on your feelings today and share them"},
        {"ar": "اكتب عن علاقة مهمة في حياتك", "en": "Write about an important relationship in your life"},
        {"ar": "جرب تمرين تنفس مع توأمك", "en": "Try a breathing exercise with your twin"},
    ],
    "growth": [
        {"ar": "خطط لخطوة واحدة نحو هدفك الأكبر", "en": "Plan one step toward your biggest goal"},
        {"ar": "شارك إنجازاً حديثاً", "en": "Share a recent achievement"},
        {"ar": "تحدى نفسك بشيء جديد اليوم", "en": "Challenge yourself with something new today"},
    ],
    "mature": [
        {"ar": "تأمل في رحلتك مع توأمك", "en": "Reflect on your journey with your twin"},
        {"ar": "اكتب رسالة لنفسك في المستقبل", "en": "Write a letter to your future self"},
        {"ar": "علم توأمك شيئاً جديداً تعلمته", "en": "Teach your twin something new you learned"},
    ],
}


async def get_daily_challenge(user_id: str, lang: str = "ar") -> Optional[Dict[str, str]]:
    profile, relationship = await _gather(get_profile(user_id), load_relationship(user_id))
    if not profile or not relationship:
        return None

    phase = await get_phase(relationship.bond_level)
    pool = CHALLENGE_POOL.get(phase, CHALLENGE_POOL["introduction"])

    # Use date as seed for consistent daily challenge
    today = datetime.now(timezone.utc).date().isoformat()
    seed = hash(f"{user_id}:{today}") % len(pool)
    challenge = pool[seed]

    return {
        "title": challenge.get(lang, challenge.get("ar", "")),
        "phase": phase,
        "type": "daily",
    }


async def get_weekly_challenge(user_id: str, lang: str = "ar") -> Optional[Dict[str, str]]:
    goals = await get_active(user_id)
    if not goals:
        return None

    goal = goals[0]
    return {
        "title": f"خطوة واحدة نحو: {goal.title}" if lang == "ar" else f"One step toward: {goal.title}",
        "type": "weekly",
        "goal_id": goal.id,
    }


async def _gather(*coros):
    import asyncio
    results = await asyncio.gather(*coros, return_exceptions=True)
    return [r if not isinstance(r, Exception) else None for r in results]
