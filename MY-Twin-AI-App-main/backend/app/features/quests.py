"""
Quests v2.0 – مهام النمو طويلة المدى (متكاملة مع TCMA)
===========================================================
تستخدم الذاكرة العاطفية ونموذج الهوية لتوليد مهام مخصصة.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response
    from app.memory.identity.identity_model import get_identity
    from app.memory.relationship.relationship_memory import get_relationship_insights
    from app.infrastructure.database.supabase_client import get_db
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

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
}

async def get_relationship_phase(user_id: str) -> str:
    """تحديد مرحلة العلاقة من TCMA"""
    phase = "introduction"
    if not TCMA_AVAILABLE:
        return phase
    
    try:
        emotional = await get_emotional_state_for_response(user_id, "")
        emotion = emotional.get("current_emotion", "neutral") if emotional else "neutral"
        
        identity = await get_identity(user_id)
        traits = identity.get("traits", []) if identity else []
        
        rel = await get_relationship_insights(user_id)
        trust = rel.get("trust_level", 0) if rel else 0
        
        if trust > 70:
            phase = "growth"
        elif trust > 40:
            phase = "deepening"
        elif trust > 20:
            phase = "trust_building"
    except Exception as e:
        logger.error(f"Phase detection failed: {e}")
    
    return phase

async def suggest_quests(user_id: str, lang: str = "ar", max_quests: int = 3) -> List[Dict[str, str]]:
    """اقتراح مهام نمو طويلة المدى"""
    if not TCMA_AVAILABLE:
        return []

    try:
        db = get_db()
        active_goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
        if active_goals.data and len(active_goals.data) >= 5:
            return []

        phase = await get_relationship_phase(user_id)
        pool = QUEST_TEMPLATES.get(phase, QUEST_TEMPLATES["introduction"])
        
        suggestions = []
        for template in pool[:max_quests]:
            title = template.get(lang, template.get("ar", ""))
            suggestions.append({
                "title": title,
                "phase": phase,
                "estimated_days": template["days"],
            })

        return suggestions[:max_quests]
    except Exception as e:
        logger.error(f"Quest suggestion failed: {e}")
        return []

async def start_quest(user_id: str, title: str, days: int = 7) -> Optional[str]:
    """بدء مهمة نمو جديدة"""
    try:
        db = get_db()
        due = (datetime.now(timezone.utc) + __import__('datetime').timedelta(days=days)).isoformat()
        result = db.table("goals").insert({
            "user_id": user_id, "title": title, "progress": 0.0,
            "priority": 2, "status": "active", "due_date": due,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        if result.data:
            logger.info(f"🏁 Quest started: {title}")
            return result.data[0]["id"]
    except Exception as e:
        logger.error(f"Quest creation failed: {e}")
    return None

logger.info("✅ Quests v2.0 initialized")
