"""
Smart Nudge Engine v2.0 – محرك التحفيز الذكي
===============================================
يولد تحديات يومية وأسبوعية بناءً على TCMA (العواطف، الهوية، الأهداف).
يتكامل مع التوصيات الموحدة ومحرك الاستباقية.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

try:
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response
    from app.memory.identity.identity_model import get_identity
    from app.memory.relationship.person_node import get_person_network
    from app.infrastructure.database.supabase_client import get_db
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

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
}

async def get_daily_challenge(user_id: str, lang: str = "ar") -> Optional[Dict[str, str]]:
    phase = "introduction"  # افتراضي
    
    if TCMA_AVAILABLE:
        try:
            # 1. تحديد المرحلة من العاطفة والهوية
            emotional = await get_emotional_state_for_response(user_id, "")
            emotion = emotional.get("current_emotion", "neutral") if emotional else "neutral"
            
            identity = await get_identity(user_id)
            traits = identity.get("traits", []) if identity else []
            
            # 2. منطق ذكي لتحديد المرحلة
            if emotion in ["joy", "confident"]:
                phase = "growth"
            elif emotion in ["sadness", "fear"]:
                phase = "trust_building"
            elif len(traits) > 3:
                phase = "deepening"
            
            # 3. تخصيص التحدي حسب الشبكة الاجتماعية
            network = await get_person_network(user_id, min_importance=50)
            if network and phase == "trust_building":
                person = network[0]
                return {
                    "title": f"تواصل مع {person['name']} اليوم واسأل عنه" if lang == "ar" else f"Reach out to {person['name']} today",
                    "phase": phase,
                    "personalized": True
                }
        except Exception as e:
            logger.error(f"TCMA challenge failed: {e}")
    
    # 4. اختيار عشوائي من المجموعة المناسبة
    import random
    today = datetime.now(timezone.utc).date().isoformat()
    pool = CHALLENGE_POOL.get(phase, CHALLENGE_POOL["introduction"])
    seed = hash(f"{user_id}:{today}") % len(pool)
    challenge = pool[seed]
    
    return {
        "title": challenge.get(lang, challenge.get("ar", "")),
        "phase": phase,
        "type": "daily"
    }

async def get_weekly_challenge(user_id: str, lang: str = "ar") -> Optional[Dict[str, str]]:
    """تحدي أسبوعي مبني على الأهداف النشطة"""
    if not TCMA_AVAILABLE:
        return None
    
    try:
        db = get_db()
        goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").limit(1).execute()
        if goals.data:
            goal = goals.data[0]
            return {
                "title": f"خطوة واحدة نحو: {goal.get('title', 'هدفك')}" if lang == "ar" else f"One step toward: {goal.get('title', 'your goal')}",
                "type": "weekly",
                "goal_id": goal["id"]
            }
    except Exception as e:
        logger.error(f"Weekly challenge failed: {e}")
    
    return None

logger.info("✅ Smart Nudge Engine v2.0 initialized")
