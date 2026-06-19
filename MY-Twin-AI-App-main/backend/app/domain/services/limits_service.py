"""
MyTwin – Limits Service v5.0
==============================
إدارة حدود الاستخدام والباقات.
مستخلص من message_limits.py الأصلي.
"""
import logging
from typing import Dict, Tuple
from datetime import datetime, timezone, timedelta
from app.infrastructure.cache.cache_service import get, set as cache_set

logger = logging.getLogger(__name__)

# ========== حدود الباقات ==========

DAILY_MESSAGES = {
    "free": 15, "free_week1": 20, "free_week2": 17, "free_week3": 15,
    "plus": 50, "premium": 150, "pro": 500, "yearly": 9999,
}

TIER_FEATURES = {
    "free": {"tts": False, "dreams": False, "coaching": False},
    "plus": {"tts": True, "dreams": False, "coaching": False},
    "premium": {"tts": True, "dreams": True, "coaching": True},
    "pro": {"tts": True, "dreams": True, "coaching": True},
    "yearly": {"tts": True, "dreams": True, "coaching": True},
}


def get_tier_features(tier: str) -> Dict:
    """جلب مميزات الباقة"""
    base = tier.split("_")[0] if "_" in tier else tier
    return TIER_FEATURES.get(base, TIER_FEATURES["free"])


def check_message_limit(uid: str, tier: str) -> Tuple[bool, int]:
    """التحقق من حد الرسائل اليومي"""
    today = datetime.now(timezone.utc).date().isoformat()
    key = f"msg:{uid}:{today}"
    used = get(key) or 0
    limit = DAILY_MESSAGES.get(tier, 15)
    
    if used >= limit:
        return False, 0
    
    cache_set(key, used + 1, 86400)
    return True, limit - used - 1


def get_usage_summary(uid: str, tier: str) -> Dict:
    """ملخص الاستخدام اليومي"""
    today = datetime.now(timezone.utc).date().isoformat()
    msg_used = get(f"msg:{uid}:{today}") or 0
    msg_limit = DAILY_MESSAGES.get(tier, 15)
    
    return {
        "messages": {
            "used": msg_used,
            "limit": msg_limit,
            "remaining": max(0, msg_limit - msg_used),
        },
    }


logger.info("✅ Limits Service v5.0 جاهز")
