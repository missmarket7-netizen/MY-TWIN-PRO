"""
Profile & Mood Routes v3.0 – متكاملة مع TCMA
=================================================
- الملف الشخصي (محدث من TCMA)
- المزاج (من الذاكرة العاطفية)
- تحديثات فورية للهوية والعلاقات
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("profile_routes")
router = APIRouter(prefix="/api/profile", tags=["profile"])

class UpdateProfileBody(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    twin_name: Optional[str] = None
    twin_gender: Optional[str] = None
    lang: Optional[str] = None

class MoodBody(BaseModel):
    mood: str = Field(...)

@router.get("/")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """جلب الملف الشخصي محدثاً من TCMA"""
    db = get_db()
    profile = {}
    try:
        r = db.table("profiles").select("*").eq("id", user_id).single().execute()
        if r.data:
            profile = r.data
    except: pass

    # إثراء من TCMA
    try:
        from app.memory.identity.identity_model import get_identity
        identity = await get_identity(user_id)
        if identity:
            profile["tcma_traits"] = identity.get("traits", [])
    except: pass

    try:
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        patterns = await get_emotional_patterns(user_id, days=7)
        profile["current_mood"] = patterns.get("dominant_emotion", "neutral")
    except: pass

    return profile or {}

@router.put("/")
async def update_profile(body: UpdateProfileBody, user_id: str = Depends(get_current_user_id)):
    """تحديث الملف الشخصي"""
    db = get_db()
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        db.table("profiles").update(update_data).eq("id", user_id).execute()
    return {"status": "ok"}

@router.get("/moods")
async def get_moods(user_id: str = Depends(get_current_user_id)):
    """جلب سجل المزاج من TCMA"""
    try:
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        patterns = await get_emotional_patterns(user_id, days=30)
        return {
            "dominant": patterns.get("dominant_emotion", "neutral"),
            "distribution": patterns.get("emotion_distribution", {}),
            "patterns": patterns.get("patterns", []),
            "recommendation": patterns.get("recommendation", ""),
        }
    except: return {"dominant": "neutral", "distribution": {}}

@router.post("/moods")
async def add_mood(body: MoodBody, user_id: str = Depends(get_current_user_id)):
    """تسجيل مزاج (يُخزن في TCMA مباشرة)"""
    mood_map = {
        "joy": 0.8, "neutral": 0.2, "sadness": -0.5, "anger": -0.5,
        "fear": -0.4, "love": 0.8, "tired": -0.3,
    }
    valence = mood_map.get(body.mood, 0.0)
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        await store_emotional_memory(
            user_id=user_id, expressed_text=f"مزاجي: {body.mood}",
            detected_emotion={"primary": body.mood, "intensity": 0.7, "valence": valence},
            trigger="manual_mood"
        )
        return {"status": "ok", "mood": body.mood}
    except Exception as e:
        raise HTTPException(500, str(e))

logger.info("✅ Profile Routes v3.0 initialized")
