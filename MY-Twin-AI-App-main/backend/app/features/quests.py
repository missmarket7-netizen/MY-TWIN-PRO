"""Quests – long-term growth missions."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.repositories.goals_repository import get_active, get_completed, create
from app.models.goal import Goal

logger = logging.getLogger("quests")

QUEST_TEMPLATES = {
    "introduction": [
        {"ar": "تحدث مع توأمك 7 أيام متتالية", "en": "Talk with your twin 7 consecutive days", "days": 7},
        {"ar": "شارك 5 مشاعر مختلفة مع توأمك", "en": "Share 5 different emotions with your twin", "days": 14},
    ],
    "trust_building": [
        {"ar": "أخبر توأمك عن 3 ذكريات مهمة", "en": "Tell your twin about 3 important memories", "days": 10},
        {"ar": "حقق 3 أهداف صغيرة مع توأمك", "en": "Achieve 3 small goals with your twin", "days": 21},
    ],
    "deepening": [
        {"ar": "شارك حلماً واحداً مع توأمك لتحليله", "en": "Share one dream with your twin for analysis", "days": 7},
        {"ar": "تأمل في علاقتك مع توأمك واكتب عنها", "en": "Reflect on your relationship with your twin", "days": 5},
    ],
    "growth": [
        {"ar": "حدد هدفاً كبيراً واعمل عليه 30 يوماً", "en": "Set a big goal and work on it for 30 days", "days": 30},
        {"ar": "تعلم مهارة جديدة وشارك تقدمك", "en": "Learn a new skill and share your progress", "days": 21},
    ],
    "mature": [
        {"ar": "كن مرشداً لنفسك ولمن حولك", "en": "Be a mentor to yourself and others", "days": 60},
        {"ar": "ابنِ إرثاً شخصياً وشاركه مع توأمك", "en": "Build a personal legacy and share it with your twin", "days": 90},
    ],
}


async def suggest_quests(user_id: str, lang: str = "ar", max_quests: int = 3) -> List[Dict[str, str]]:
    from app.twin_state.relationship_service import load as load_relationship
    from app.twin_state.journey_service import get_phase
    from app.repositories.profile_repository import get_profile

    profile, relationship = await _gather(get_profile(user_id), load_relationship(user_id))
    if not profile or not relationship:
        return []

    active_goals = await get_active(user_id)
    completed_goals = await get_completed(user_id)

    # Don't suggest if user already has many active goals
    if len(active_goals) >= 5:
        return []

    phase = await get_phase(relationship.bond_level)
    pool = QUEST_TEMPLATES.get(phase, QUEST_TEMPLATES["introduction"])
    suggestions = []
    today = datetime.now(timezone.utc).date().isoformat()

    for template in pool[:max_quests]:
        # Check if similar quest already exists
        title = template.get(lang, template.get("ar", ""))
        if any(g.title == title for g in active_goals + completed_goals):
            continue

        suggestions.append({
            "title": title,
            "phase": phase,
            "estimated_days": template["days"],
        })

    return suggestions[:max_quests]


async def start_quest(user_id: str, title: str) -> Optional[str]:
    goal = Goal(user_id=user_id, title=title, progress=0.0, priority=2, status="active")
    goal_id = await create(goal)
    if goal_id:
        logger.info(f"🏁 Quest started: {title} ({goal_id})")
    return goal_id


async def _gather(*coros):
    import asyncio
    results = await asyncio.gather(*coros, return_exceptions=True)
    return [r if not isinstance(r, Exception) else None for r in results]
