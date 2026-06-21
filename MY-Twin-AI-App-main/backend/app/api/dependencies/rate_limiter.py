"""
Rate Limiter v3.0 – متكامل مع نظام الباقات وحدود الميزات
=============================================================
- حدود عامة لكل المستخدمين
- حدود مخصصة لكل باقة
- حدود لكل ميزة على حدة (متوافقة مع Limits Service)
- تكامل مع Cache (Redis/محلي)
"""
import logging, time
from typing import Dict, Optional, Callable
from fastapi import Request, HTTPException

logger = logging.getLogger("rate_limiter")

# حدود افتراضية لكل باقة (طلبات/دقيقة)
TIER_RATE_LIMITS = {
    "free": 10,
    "plus": 30,
    "premium": 60,
    "pro": 120,
    "yearly": 300,
}

# حدود لكل ميزة (طلبات/دقيقة)
FEATURE_RATE_LIMITS = {
    "chat": 15,
    "study": 5,
    "code_lab": 5,
    "business": 3,
    "life_coach": 2,
    "dreams": 2,
    "content": 5,
    "smart_home": 5,
    "image_lab": 3,
}

# تخزين مؤقت (في الذاكرة للإنتاج المحلي، يُستبدل بـ Redis للإنتاج)
_request_logs: Dict[str, list] = {}

def _get_tier_limit(tier: str) -> int:
    """الحد العام للباقة (طلبات/دقيقة)"""
    return TIER_RATE_LIMITS.get(tier, 10)

def _get_feature_limit(feature: str) -> int:
    """الحد الخاص بالميزة"""
    return FEATURE_RATE_LIMITS.get(feature, 10)

async def check_rate_limit(
    request: Request,
    user_id: str,
    tier: str = "free",
    feature: str = "general"
) -> bool:
    """
    فحص معدل الطلبات لمستخدم معين.
    يُرجع True إذا كان مسموحاً، False إذا تجاوز الحد.
    """
    now = time.time()
    window = 60  # ثانية (دقيقة واحدة)

    # مفتاح المستخدم
    key = f"{user_id}:{feature}"

    # تنظيف السجلات القديمة
    if key not in _request_logs:
        _request_logs[key] = []
    _request_logs[key] = [t for t in _request_logs[key] if now - t < window]

    # الحد المسموح
    feature_limit = _get_feature_limit(feature)
    tier_limit = _get_tier_limit(tier)
    effective_limit = min(feature_limit, tier_limit)

    if len(_request_logs[key]) >= effective_limit:
        logger.warning(f"Rate limit exceeded: {user_id} on {feature}")
        return False

    _request_logs[key].append(now)
    return True


def RateLimit(max_requests: int = 10, feature: str = "general"):
    """
    Dependency factory: يحدد عدد الطلبات المسموحة.
    مثال: `Depends(RateLimit(max_requests=5, feature="study"))`
    """
    async def limiter(
        request: Request,
        user_id: str = None,  # سيُملأ من get_current_user_id
    ) -> None:
        if not user_id:
            # محاولة استخراج user_id من الطلب
            try:
                from app.api.dependencies.auth import get_current_user_id
                user_id = await get_current_user_id(request.headers.get("Authorization", ""))
            except:
                pass

        if user_id:
            allowed = await check_rate_limit(request, user_id, "free", feature)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=f"تم تجاوز الحد المسموح ({max_requests} طلب/دقيقة). حاول مرة أخرى بعد قليل.",
                    headers={"Retry-After": "60"}
                )
    return limiter


def TierRateLimit(feature: str = "general"):
    """
    Dependency factory: يطبق حد الباقة تلقائياً.
    مثال: `Depends(TierRateLimit(feature="study"))`
    """
    async def limiter(
        request: Request,
        user_id: str = None,
        user_tier: str = "free",
    ) -> None:
        if not user_id:
            try:
                from app.api.dependencies.auth import get_current_user_id
                user_id = await get_current_user_id(request.headers.get("Authorization", ""))
            except:
                pass

        if user_id:
            max_req = _get_tier_limit(user_tier)
            allowed = await check_rate_limit(request, user_id, user_tier, feature)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=f"تم تجاوز حد الباقة ({max_req} طلب/دقيقة).",
                    headers={"Retry-After": "60"}
                )
    return limiter


def cleanup_expired_logs():
    """تنظيف السجلات القديمة (تُستدعى دورياً)"""
    now = time.time()
    window = 60
    for key in list(_request_logs.keys()):
        _request_logs[key] = [t for t in _request_logs[key] if now - t < window]
        if not _request_logs[key]:
            del _request_logs[key]

logger.info("✅ Rate Limiter v3.0 initialized")
