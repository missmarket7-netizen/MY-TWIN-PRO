"""
Referral Routes v3.0 – متكاملة مع TCMA و Event Bus
=========================================================
- توليد كود إحالة فريد
- تفعيل الكود ومنح مكافآت للطرفين
- إحصائيات الإحالة
- تكامل مع الذاكرة العاطفية
"""
import hashlib, logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("referral_routes")
router = APIRouter(prefix="/api/referral", tags=["referral"])

class ActivateBody(BaseModel):
    code: str = Field(..., min_length=6, max_length=10)

@router.post("/generate")
async def generate(user_id: str = Depends(get_current_user_id)):
    """توليد كود إحالة فريد"""
    db = get_db()
    code = "MT" + hashlib.sha256(user_id.encode()).hexdigest()[:6].upper()
    try:
        db.table("profiles").upsert({
            "id": user_id,
            "referral_code": code,
        }).execute()
    except:
        pass
    return {"code": code, "link": f"https://mytwin.app/join?ref={code}"}

@router.post("/activate")
async def activate(body: ActivateBody, user_id: str = Depends(get_current_user_id)):
    """تفعيل كود إحالة ومنح مكافآت"""
    db = get_db()
    code = body.code.upper().strip()
    try:
        # البحث عن صاحب الكود
        owner = db.table("profiles").select("id").eq("referral_code", code).single().execute()
        if not owner.data:
            raise HTTPException(400, "Invalid code")
        
        inviter_id = owner.data["id"]
        if inviter_id == user_id:
            raise HTTPException(400, "لا يمكنك استخدام كودك الخاص")

        # التحقق من عدم الاستخدام المسبق
        existing = db.table("referral_usage").select("*").eq("user_id", user_id).eq("code", code).execute()
        if existing.data:
            raise HTTPException(400, "لقد استخدمت هذا الكود من قبل")

        # تسجيل الاستخدام
        db.table("referral_usage").insert({
            "user_id": user_id,
            "code": code,
            "inviter_id": inviter_id,
            "activated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        # منح المكافآت (طاقة + رسائل) لكلا الطرفين
        for uid in [user_id, inviter_id]:
            try:
                db.table("profiles").update({
                    "twin_energy": 100,
                    "daily_messages_used": 0,
                }).eq("id", uid).execute()
            except: pass

        # تسجيل في TCMA
        try:
            from app.memory.emotional.emotional_memory import store_emotional_memory
            await store_emotional_memory(
                user_id=user_id,
                expressed_text="تم تفعيل كود إحالة",
                detected_emotion={"primary": "joy", "intensity": 0.8, "valence": 0.7},
                trigger="referral_activated"
            )
        except: pass

        # تسجيل الحدث
        try:
            from app.events.event_bus import emit
            await emit({
                "type": "referral_activated",
                "user_id": user_id,
                "inviter_id": inviter_id,
                "code": code,
            })
        except: pass

        return {"success": True, "message": "تم تفعيل الكود! 🎉 تم شحن طاقتك."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/stats")
async def stats(user_id: str = Depends(get_current_user_id)):
    """إحصائيات الإحالة"""
    db = get_db()
    try:
        invited = db.table("referral_usage").select("id").eq("inviter_id", user_id).execute()
        profile = db.table("profiles").select("referral_code").eq("id", user_id).single().execute()
        code = profile.data.get("referral_code", "") if profile.data else ""
        
        return {
            "code": code,
            "link": f"https://mytwin.app/join?ref={code}" if code else "",
            "invited_count": len(invited.data or []),
            "message": "شارك الكود مع أصدقائك ليكسبوا طاقة كاملة!"
        }
    except Exception as e:
        raise HTTPException(500, str(e))

logger.info("✅ Referral Routes v3.0 initialized")
