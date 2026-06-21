"""
Ads Routes v3.0 – متوافقة مع Ad Service الجديدة
====================================================
- تستخدم AdService v3 (طاقة + رسائل + Supabase + TCMA)
- تدعم جميع الباقات
- تسجيل الأحداث
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies.auth import get_current_user_id, get_user_tier

logger = logging.getLogger("ads_routes")
router = APIRouter(prefix="/api/ads", tags=["ads"])

class ClaimAdBody(BaseModel):
    ad_type: str = Field("rewarded")
    ad_platform: str = Field("admob")

@router.post("/reward")
async def claim_reward(
    body: ClaimAdBody,
    user_id: str = Depends(get_current_user_id),
    tier: str = Depends(get_user_tier),
):
    """
    مطالبة بمكافأة مشاهدة إعلان.
    يمنح: رسائل إضافية + تجديد طاقة 20%
    """
    try:
        from app.domain.billing.ad_service import claim_ad_reward
        
        result = await claim_ad_reward(user_id)
        
        if not result.get("success"):
            raise HTTPException(429, result.get("message", "Daily ad limit reached"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ad reward failed: {e}")
        raise HTTPException(500, "فشل معالجة المكافأة")

@router.get("/status")
async def ad_status(
    user_id: str = Depends(get_current_user_id),
):
    """حالة الإعلانات اليومية للمستخدم"""
    try:
        from app.domain.billing.ad_service import get_ad_status
        
        return await get_ad_status(user_id)
        
    except Exception as e:
        logger.error(f"Ad status failed: {e}")
        return {
            "watched_today": 0,
            "remaining_today": 3,
            "max_daily_ads": 3,
            "can_watch": True,
        }

logger.info("✅ Ads Routes v3.0 initialized")
