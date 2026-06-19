"""Ads Routes – Rewarded Ads to earn extra messages."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db
from app.infrastructure.cache.cache_service import get, set as cache_set

router = APIRouter(prefix="/api/ads", tags=["ads"])

REWARD_MESSAGES = 3
MAX_DAILY_ADS = 5

class ClaimAdBody(BaseModel):
    ad_type: str = Field("rewarded")
    ad_platform: str = Field("admob")

@router.post("/reward")
async def claim_reward(body: ClaimAdBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    today = date.today().isoformat()
    
    # Premium users don't need ads
    try:
        profile = db.table("profiles").select("tier").eq("id", user_id).single().execute()
        tier = profile.data.get("tier", "free") if profile.data else "free"
        if tier not in ["free", "free_trial_14d"]:
            return {"success": True, "message": "Premium user – no ads needed"}
    except:
        tier = "free"

    # Daily limit check
    ad_key = f"ads:{user_id}:{today}"
    watched = get(ad_key) or 0
    if watched >= MAX_DAILY_ADS:
        raise HTTPException(429, "Daily ad limit reached")

    # Reward the user by reducing their message count
    msg_key = f"msg:{user_id}:{today}"
    current = get(msg_key) or 0
    cache_set(msg_key, max(0, current - REWARD_MESSAGES), 86400)
    cache_set(ad_key, watched + 1, 86400)

    # Log to database
    try:
        db.table("ad_rewards").insert({
            "user_id": user_id, "ad_type": body.ad_type,
            "reward_messages": REWARD_MESSAGES,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except: pass

    return {
        "success": True,
        "reward": REWARD_MESSAGES,
        "remaining_ads_today": MAX_DAILY_ADS - (watched + 1)
    }

@router.get("/status")
async def ad_status(user_id: str = Depends(get_current_user_id)):
    today = date.today().isoformat()
    watched = get(f"ads:{user_id}:{today}") or 0
    return {
        "watched_today": watched,
        "remaining_today": max(0, MAX_DAILY_ADS - watched),
        "reward_per_ad": REWARD_MESSAGES
    }
