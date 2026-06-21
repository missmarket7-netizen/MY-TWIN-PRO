"""
MyTwin – Limits Service v6.0 (متكامل مع جميع الميزات)
=============================================================
- حدود يومية لكل باقة
- حدود لكل ميزة على حدة
- تكامل مع Feature Flags و TierConfig
- تخزين في Supabase + Cache
"""
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timezone, timedelta
from app.infrastructure.cache.cache_service import get, set as cache_set

logger = logging.getLogger(__name__)

# ========== حدود الرسائل اليومية ==========
DAILY_MESSAGES = {
    "free": 15, "plus": 50, "premium": 150, "pro": 500, "yearly": 9999,
}

# ========== حدود الميزات اليومية ==========
FEATURE_DAILY_LIMITS = {
    "study": {"free": 5, "plus": 15, "premium": 50, "pro": 200, "yearly": 9999},
    "code_lab": {"free": 2, "plus": 10, "premium": 40, "pro": 150, "yearly": 9999},
    "business": {"free": 2, "plus": 10, "premium": 40, "pro": 150, "yearly": 9999},
    "life_coach": {"free": 1, "plus": 5, "premium": 30, "pro": 100, "yearly": 9999},
    "dreams": {"free": 1, "plus": 3, "premium": 20, "pro": 50, "yearly": 9999},
    "content": {"free": 2, "plus": 10, "premium": 40, "pro": 150, "yearly": 9999},
    "smart_home": {"free": 3, "plus": 10, "premium": 50, "pro": 200, "yearly": 9999},
    "search": {"free": 5, "plus": 20, "premium": 100, "pro": 500, "yearly": 9999},
    "deep_search": {"free": 0, "plus": 1, "premium": 10, "pro": 50, "yearly": 200},
    "translate": {"free": 3, "plus": 15, "premium": 50, "pro": 200, "yearly": 9999},
    "summarize": {"free": 3, "plus": 15, "premium": 50, "pro": 200, "yearly": 9999},
    "weather": {"free": 10, "plus": 30, "premium": 100, "pro": 500, "yearly": 9999},
    "news": {"free": 5, "plus": 20, "premium": 100, "pro": 500, "yearly": 9999},
    "currency": {"free": 5, "plus": 20, "premium": 100, "pro": 500, "yearly": 9999},
    "voice": {"free": 3, "plus": 10, "premium": 50, "pro": 200, "yearly": 9999},
}

# ========== مميزات الباقات ==========
TIER_FEATURES = {
    "free": {"tts": False, "dreams": False, "coaching": False, "study": True, "code_lab": False, "business": False},
    "plus": {"tts": True, "dreams": True, "coaching": False, "study": True, "code_lab": True, "business": False},
    "premium": {"tts": True, "dreams": True, "coaching": True, "study": True, "code_lab": True, "business": True},
    "pro": {"tts": True, "dreams": True, "coaching": True, "study": True, "code_lab": True, "business": True},
    "yearly": {"tts": True, "dreams": True, "coaching": True, "study": True, "code_lab": True, "business": True},
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

async def check_feature_usage(uid: str, tier: str, feature: str) -> Tuple[bool, int]:
    """التحقق من حد استخدام ميزة معينة"""
    # 1. التحقق من صلاحية الميزة للباقة
    features = get_tier_features(tier)
    if feature in features and not features[feature]:
        return False, 0

    # 2. التحقق من الحد اليومي
    today = datetime.now(timezone.utc).date().isoformat()
    key = f"feat:{uid}:{feature}:{today}"
    used = get(key) or 0
    limits = FEATURE_DAILY_LIMITS.get(feature, {"free": 1})
    limit = limits.get(tier, limits.get("free", 1))
    
    if used >= limit:
        return False, 0
    
    cache_set(key, used + 1, 86400)
    return True, limit - used - 1

def get_usage_summary(uid: str, tier: str) -> Dict:
    """ملخص الاستخدام اليومي"""
    today = datetime.now(timezone.utc).date().isoformat()
    msg_used = get(f"msg:{uid}:{today}") or 0
    msg_limit = DAILY_MESSAGES.get(tier, 15)
    
    # استخدام الميزات
    feature_usage = {}
    for feature in FEATURE_DAILY_LIMITS:
        key = f"feat:{uid}:{feature}:{today}"
        used = get(key) or 0
        limits = FEATURE_DAILY_LIMITS.get(feature, {"free": 1})
        limit = limits.get(tier, limits.get("free", 1))
        if used > 0 or limit > 0:
            feature_usage[feature] = {"used": used, "limit": limit, "remaining": max(0, limit - used)}
    
    return {
        "messages": {
            "used": msg_used,
            "limit": msg_limit,
            "remaining": max(0, msg_limit - msg_used),
        },
        "features": feature_usage,
    }

logger.info("✅ Limits Service v6.0 initialized")
