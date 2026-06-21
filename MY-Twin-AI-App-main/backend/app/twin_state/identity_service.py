"""
Twin Identity Service v2.0 – هوية التوأم (متكاملة مع TCMA و Supabase)
========================================================================
تخزّن هوية التوأم (سماته، مرحلة تطوره) في Supabase.
تتكامل مع نموذج هوية المستخدم من TCMA لتخصيص وصف التوأم.
"""
import logging
from typing import Dict, Any, List, Optional

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.memory.identity.identity_model import get_identity as get_user_identity
    TCMA_IDENTITY_AVAILABLE = True
except ImportError:
    TCMA_IDENTITY_AVAILABLE = False

logger = logging.getLogger("identity_service")

DEFAULT_TRAITS = ["متفهم", "صبور", "ذكي", "دافئ", "مرح", "حكيم"]

IDENTITY_TEMPLATES = {
    "ar": "أنا {twin_name}، رفيق رقمي {traits_desc}. أتعلم من تفاعلاتنا وأنمو معك كل يوم.",
    "en": "I am {twin_name}, a {traits_desc} digital companion. I learn from our interactions and grow with you daily.",
}

# ذاكرة مؤقتة خفيفة للجلسة الحالية فقط
_twin_cache: Dict[str, Dict[str, Any]] = {}

async def _load_from_db(user_id: str) -> Optional[Dict[str, Any]]:
    """تحميل هوية التوأم من Supabase"""
    if not DB_AVAILABLE:
        return None
    try:
        db = get_db()
        result = db.table("twin_states").select("*").eq("user_id", user_id).single().execute()
        return result.data if result.data else None
    except Exception as e:
        logger.warning(f"Failed to load twin state: {e}")
        return None

async def _save_to_db(user_id: str, state: Dict[str, Any]) -> None:
    """حفظ هوية التوأم إلى Supabase"""
    if not DB_AVAILABLE:
        return
    try:
        db = get_db()
        existing = await _load_from_db(user_id)
        if existing:
            db.table("twin_states").update(state).eq("user_id", user_id).execute()
        else:
            state["user_id"] = user_id
            db.table("twin_states").insert(state).execute()
    except Exception as e:
        logger.warning(f"Failed to save twin state: {e}")

async def _build_state(user_id: str, twin_name: str = "MyTwin") -> Dict[str, Any]:
    """بناء حالة التوأم (من DB أو افتراضية)"""
    # محاولة التحميل من الذاكرة المؤقتة
    if user_id in _twin_cache:
        return _twin_cache[user_id]
    
    # محاولة التحميل من Supabase
    saved = await _load_from_db(user_id)
    if saved:
        state = {
            "traits": saved.get("traits", DEFAULT_TRAITS[:]),
            "evolution_stage": saved.get("evolution_stage", 0),
            "twin_name": saved.get("twin_name", twin_name),
            "interaction_count": saved.get("interaction_count", 0),
        }
    else:
        state = {
            "traits": DEFAULT_TRAITS[:],
            "evolution_stage": 0,
            "twin_name": twin_name,
            "interaction_count": 0,
        }
        await _save_to_db(user_id, state)
    
    # تخصيص الوصف بناءً على هوية المستخدم
    if TCMA_IDENTITY_AVAILABLE:
        try:
            user_identity = await get_user_identity(user_id)
            if user_identity and user_identity.get("traits"):
                # إضافة صفات تكميلية للتوأم بناءً على صفات المستخدم
                user_traits = user_identity.get("traits", [])
                if "طموح" in user_traits:
                    state["traits"] = list(set(state["traits"] + ["محفز", "ملهم"]))
                if "مبدع" in user_traits:
                    state["traits"] = list(set(state["traits"] + ["مبدع", "فني"]))
        except Exception as e:
            logger.warning(f"User identity enrichment failed: {e}")
    
    # توليد الوصف
    traits_str = "، ".join(state["traits"][:6])
    state["description_ar"] = IDENTITY_TEMPLATES["ar"].format(
        twin_name=state["twin_name"], traits_desc=traits_str
    )
    state["description_en"] = IDENTITY_TEMPLATES["en"].format(
        twin_name=state["twin_name"], traits_desc=traits_str
    )
    
    _twin_cache[user_id] = state
    return state

async def get_identity(user_id: str, twin_name: str = "MyTwin", lang: str = "ar") -> Dict[str, Any]:
    """استرجاع هوية التوأم"""
    state = await _build_state(user_id, twin_name)
    return {
        "traits": state["traits"],
        "evolution_stage": state["evolution_stage"],
        "description": state.get(f"description_{lang}", state.get("description_ar", "")),
        "interaction_count": state["interaction_count"],
    }

async def evolve(user_id: str, new_trait: str, reflection: str) -> None:
    """تطوير هوية التوأم (إضافة سمة جديدة)"""
    state = await _build_state(user_id)
    
    if new_trait and new_trait not in state["traits"] and len(state["traits"]) < 15:
        state["traits"].append(new_trait)
    
    state["evolution_stage"] = state.get("evolution_stage", 0) + 1
    state["interaction_count"] = state.get("interaction_count", 0) + 1
    
    # تحديث الوصف
    traits_str = "، ".join(state["traits"][:6])
    state["description_ar"] = IDENTITY_TEMPLATES["ar"].format(
        twin_name=state["twin_name"], traits_desc=traits_str
    )
    state["description_en"] = IDENTITY_TEMPLATES["en"].format(
        twin_name=state["twin_name"], traits_desc=traits_str
    )
    
    _twin_cache[user_id] = state
    await _save_to_db(user_id, state)
    logger.info(f"🎭 هوية التوأم تطورت: المرحلة {state['evolution_stage']}, الصفات: {state['traits']}")

async def get_traits(user_id: str) -> List[str]:
    state = await _build_state(user_id)
    return state["traits"]

async def get_evolution_stage(user_id: str) -> int:
    state = await _build_state(user_id)
    return state["evolution_stage"]

logger.info("✅ Twin Identity Service v2.0 initialized with DB persistence")
