"""
Personality State v2.0 – متكامل مع TCMA و Supabase
=====================================================
يستخدم Reflection Engine للتأملات، و Supabase للأهداف.
يتزامن مع Emotional Memory لتحديث الحالة الداخلية.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from app.memory.reflection.reflection_engine import store_reflection, get_user_insights
    TCMA_REFLECTION_AVAILABLE = True
except ImportError:
    TCMA_REFLECTION_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response
    TCMA_EMOTION_AVAILABLE = True
except ImportError:
    TCMA_EMOTION_AVAILABLE = False

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger("personality_state")

# ذاكرة مؤقتة خفيفة للجلسة الحالية فقط
_user_cache: Dict[str, Dict[str, Any]] = {}

def _default_state() -> Dict[str, Any]:
    return {
        "internal_state": {
            "mood": "neutral", "energy": 0.7, "curiosity": 0.5,
            "last_thought_ar": "", "last_thought_en": "",
            "interaction_count": 0
        },
        "active_objectives": [],
    }

def _get_cache(user_id: str) -> Dict[str, Any]:
    if user_id not in _user_cache:
        _user_cache[user_id] = _default_state()
    return _user_cache[user_id]

async def load(user_id: str) -> Dict[str, Any]:
    """تحميل حالة المستخدم (من TCMA + ذاكرة الجلسة)"""
    state = _get_cache(user_id)

    # 1. تحديث المزاج من الذاكرة العاطفية
    if TCMA_EMOTION_AVAILABLE:
        try:
            emotional = await get_emotional_state_for_response(user_id, "")
            if emotional:
                current = emotional.get("current_emotion", "neutral")
                state["internal_state"]["mood"] = current
                if current == "joy":
                    state["internal_state"]["energy"] = 0.9
                elif current in ["sadness", "fear"]:
                    state["internal_state"]["energy"] = 0.4
        except Exception as e:
            logger.warning(f"Emotion sync failed: {e}")

    # 2. جلب الأهداف النشطة من Supabase
    if DB_AVAILABLE:
        try:
            db = get_db()
            goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").order("created_at", desc=True).limit(5).execute()
            if goals.data:
                state["active_objectives"] = [
                    {"title": g.get("title", ""), "progress": g.get("progress", 0),
                     "created_at": g.get("created_at", "")}
                    for g in goals.data
                ]
        except Exception as e:
            logger.warning(f"Goals fetch failed: {e}")

    # 3. جلب آخر فكرة تأملية من TCMA
    if TCMA_REFLECTION_AVAILABLE:
        try:
            insights = await get_user_insights(user_id, min_confidence=0.5)
            if insights and insights.get("insights"):
                last = insights["insights"][0]
                state["internal_state"]["last_thought_ar"] = last.get("text", "")
        except Exception as e:
            logger.warning(f"Reflection fetch failed: {e}")

    return state

async def reflect(user_id: str, summary: str, twin_name: str = "MyTwin", lang: str = "ar") -> Optional[Dict]:
    """تأمل – يخزن في TCMA Reflection Engine"""
    if not summary.strip():
        return None

    state = _get_cache(user_id)
    reflection = {
        "summary": summary[:200], "lang": lang,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # تخزين في TCMA
    if TCMA_REFLECTION_AVAILABLE:
        try:
            await store_reflection(
                user_id=user_id, insight_type="twin_reflection",
                insight_text=summary[:200], confidence=0.9,
                language=lang
            )
        except Exception as e:
            logger.warning(f"TCMA reflection failed: {e}")

    # تحديث الكاش المحلي
    if lang == "en":
        state["internal_state"]["last_thought_en"] = summary[:200]
    else:
        state["internal_state"]["last_thought_ar"] = summary[:200]
    state["internal_state"]["interaction_count"] += 1

    logger.info(f"✅ Reflection: {user_id}")
    return reflection

async def add_objective(user_id: str, title: str) -> Optional[Dict]:
    """إضافة هدف – يخزن في Supabase"""
    if not DB_AVAILABLE:
        return None
    try:
        db = get_db()
        result = db.table("goals").insert({
            "user_id": user_id, "title": title, "progress": 0.0,
            "status": "active", "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        if result.data:
            return {"id": result.data[0]["id"], "title": title}
    except Exception as e:
        logger.warning(f"Objective creation failed: {e}")
    return None

async def get_objectives(user_id: str) -> List[Dict]:
    """جلب الأهداف النشطة من Supabase"""
    if not DB_AVAILABLE:
        return []
    try:
        db = get_db()
        goals = db.table("goals").select("*").eq("user_id", user_id).eq("status", "active").order("created_at", desc=True).execute()
        return goals.data or []
    except:
        return []

async def update_profile(user_id: str, data: Dict) -> None:
    """تحديث الملف الشخصي (يحفظ في Supabase)"""
    if not DB_AVAILABLE:
        return
    try:
        db = get_db()
        db.table("profiles").update({
            **data, "last_updated": datetime.now(timezone.utc).isoformat()
        }).eq("id", user_id).execute()
    except Exception as e:
        logger.warning(f"Profile update failed: {e}")

async def get_profile(user_id: str) -> Dict:
    """جلب الملف الشخصي من Supabase"""
    if not DB_AVAILABLE:
        return {}
    try:
        db = get_db()
        result = db.table("profiles").select("*").eq("id", user_id).single().execute()
        return result.data or {}
    except:
        return {}

async def get_state_summary(user_id: str) -> Dict[str, Any]:
    """ملخص حالة التوأم (للتصدير)"""
    state = await load(user_id)
    return {
        "mood": state["internal_state"]["mood"],
        "energy": state["internal_state"]["energy"],
        "curiosity": state["internal_state"]["curiosity"],
        "active_objectives": [o["title"] for o in state.get("active_objectives", [])],
        "last_thought_ar": state["internal_state"]["last_thought_ar"],
        "last_thought_en": state["internal_state"]["last_thought_en"],
    }

logger.info("✅ Personality State v2.0 with TCMA + DB persistence")
