"""Ad Service – manages rewarded ads and daily limits."""
import logging
from typing import Dict, Any
from datetime import date
from app.infrastructure.cache.cache_service import get, set as cache_set

logger = logging.getLogger("ad_service")

MAX_DAILY_ADS = 5
REWARD_MESSAGES = 3

async def get_ad_status(user_id: str) -> Dict[str, Any]:
    today = date.today().isoformat()
    watched = get(f"ads:{user_id}:{today}") or 0
    return {
        "watched_today": watched,
        "remaining_today": max(0, MAX_DAILY_ADS - watched),
        "reward_per_ad": REWARD_MESSAGES,
        "can_watch": watched < MAX_DAILY_ADS,
    }

async def claim_ad_reward(user_id: str) -> Dict[str, Any]:
    today = date.today().isoformat()
    ad_key = f"ads:{user_id}:{today}"
    watched = get(ad_key) or 0
    
    if watched >= MAX_DAILY_ADS:
        return {"success": False, "message": "Daily ad limit reached"}
    
    msg_key = f"msg:{user_id}:{today}"
    current = get(msg_key) or 0
    cache_set(msg_key, max(0, current - REWARD_MESSAGES), 86400)
    cache_set(ad_key, watched + 1, 86400)
    
    logger.info(f"✅ Ad reward claimed for {user_id}: {REWARD_MESSAGES} messages")
    return {"success": True, "reward": REWARD_MESSAGES, "remaining_ads": MAX_DAILY_ADS - (watched + 1)}
