"""
Push Notification Routes v3.0 – متكاملة مع Proactive Engine و TCMA
=========================================================================
- تحديث رمز الإشعارات (Push Token)
- إرسال إشعار استباقي بناءً على توصيات المحرك الموحد
- إعدادات الإشعارات (صوت، اهتزاز، فئات)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("push_routes")
router = APIRouter(prefix="/api/push", tags=["push"])

class PushTokenBody(BaseModel):
    token: str = Field(..., min_length=10)
    platform: str = Field("android")

class PushSettingsBody(BaseModel):
    sound_enabled: bool = True
    vibration_enabled: bool = True
    proactive_enabled: bool = True
    categories: Optional[list] = None  # ["study", "business", "emotional", "dreams"]

@router.put("/token")
async def update_push_token(
    body: PushTokenBody,
    user_id: str = Depends(get_current_user_id),
):
    """تحديث رمز الإشعارات للجهاز"""
    db = get_db()
    try:
        db.table("profiles").update({
            "push_token": body.token,
            "device_platform": body.platform,
            "push_token_updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", user_id).execute()
        
        # تسجيل في TCMA
        try:
            from app.memory.emotional.emotional_memory import store_emotional_memory
            await store_emotional_memory(
                user_id=user_id,
                expressed_text="تم تفعيل الإشعارات",
                detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.3},
                trigger="push_enabled"
            )
        except: pass
        
        return {"status": "ok", "message": "تم تفعيل الإشعارات"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/settings")
async def get_push_settings(user_id: str = Depends(get_current_user_id)):
    """جلب إعدادات الإشعارات الحالية"""
    db = get_db()
    try:
        profile = db.table("profiles").select("push_token,device_platform,push_settings").eq("id", user_id).single().execute()
        settings = profile.data.get("push_settings", {}) if profile.data else {}
        return {
            "token_registered": bool(profile.data.get("push_token")) if profile.data else False,
            "platform": profile.data.get("device_platform") if profile.data else None,
            "settings": settings,
        }
    except:
        return {"token_registered": False, "platform": None, "settings": {}}

@router.put("/settings")
async def update_push_settings(
    body: PushSettingsBody,
    user_id: str = Depends(get_current_user_id),
):
    """تحديث إعدادات الإشعارات"""
    db = get_db()
    try:
        settings = {
            "sound_enabled": body.sound_enabled,
            "vibration_enabled": body.vibration_enabled,
            "proactive_enabled": body.proactive_enabled,
            "categories": body.categories or ["general"],
        }
        db.table("profiles").update({
            "push_settings": settings,
        }).eq("id", user_id).execute()
        
        return {"status": "ok", "settings": settings}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/send-proactive")
async def send_proactive_notification(user_id: str = Depends(get_current_user_id)):
    """إرسال إشعار استباقي فوري (للتجربة)"""
    db = get_db()
    try:
        profile = db.table("profiles").select("push_token,device_platform").eq("id", user_id).single().execute()
        if not profile.data or not profile.data.get("push_token"):
            raise HTTPException(400, "لم يتم تسجيل جهاز للإشعارات بعد")
        
        # جلب توصية من المحرك الموحد
        from app.core.unified_recommendation_engine import engine
        recs = await engine.get_daily_recommendation(user_id)
        message = recs.get("recommendations", [{}])[0].get("message", "مرحباً! كيف يمكنني مساعدتك اليوم؟ 💜")
        
        # إرسال الإشعار (محاكاة للتطوير)
        logger.info(f"📨 Proactive push sent to {user_id}: {message}")
        
        # تسجيل في TCMA
        try:
            from app.memory.emotional.emotional_memory import store_emotional_memory
            await store_emotional_memory(
                user_id=user_id,
                expressed_text="تم إرسال إشعار استباقي",
                detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.3},
                trigger="proactive_push"
            )
        except: pass
        
        return {
            "status": "sent",
            "message": message,
            "platform": profile.data.get("device_platform", "android"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

logger.info("✅ Push Routes v3.0 initialized")
