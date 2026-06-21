"""
Auth Dependency v3.0 – متكاملة مع Security Service و Cache
=============================================================
- فك تشفير JWT عبر Security Service
- استخراج كامل لسياق المستخدم (ID, Tier, Role)
- تخزين مؤقت للملف الشخصي (Cache) لتقليل استدعاءات DB
- تسجيل محاولات الفشل
"""
import logging
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends, Request

logger = logging.getLogger("auth_dependency")

try:
    from app.core.security import decode_access_token, extract_user_id, extract_tier, get_user_context
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

try:
    from app.infrastructure.cache.cache_service import get as cache_get, set as cache_set
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

async def get_current_user_id(
    authorization: str = Header(..., alias="Authorization")
) -> str:
    """
    استخراج user_id من JWT.
    يستخدم Security Service للفك، ثم Supabase للتحقق.
    """
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("محاولة بدون Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")

    # 1. محاولة فك التشفير محلياً (Security Service)
    if SECURITY_AVAILABLE:
        payload = decode_access_token(token)
        if payload:
            user_id = extract_user_id(payload)
            if user_id:
                return user_id

    # 2. التحقق عبر Supabase
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        user_resp = db.auth.get_user(token)
        if user_resp and user_resp.user and user_resp.user.id:
            return user_resp.user.id
    except Exception as e:
        logger.error(f"Supabase auth failed: {e}")

    raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(
    authorization: str = Header(..., alias="Authorization")
) -> Dict[str, Any]:
    """
    استخراج سياق المستخدم الكامل من JWT.
    يعيد: user_id, tier, role, email (إن وجد)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization[7:].strip()

    # 1. محاولة استخراج السياق محلياً
    if SECURITY_AVAILABLE:
        context = get_user_context(token)
        if context.get("authenticated"):
            return context

    # 2. التحقق عبر Supabase
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        user_resp = db.auth.get_user(token)
        if user_resp and user_resp.user:
            user = user_resp.user
            return {
                "authenticated": True,
                "user_id": user.id,
                "email": getattr(user, 'email', ''),
                "tier": getattr(user, 'user_metadata', {}).get('tier', 'free'),
                "role": getattr(user, 'role', 'authenticated'),
            }
    except Exception as e:
        logger.error(f"Supabase auth failed: {e}")

    raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_user_tier(
    user_id: str = Depends(get_current_user_id)
) -> str:
    """
    استخراج باقة المستخدم (مع تخزين مؤقت).
    """
    # 1. فحص الكاش
    if CACHE_AVAILABLE:
        cached_tier = cache_get(f"tier:{user_id}")
        if cached_tier:
            return cached_tier

    # 2. جلب من قاعدة البيانات
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        profile = db.table("profiles").select("tier").eq("id", user_id).single().execute()
        if profile.data and profile.data.get("tier"):
            tier = profile.data["tier"]
            if CACHE_AVAILABLE:
                cache_set(f"tier:{user_id}", tier, 600)
            return tier
    except Exception as e:
        logger.warning(f"Failed to fetch tier: {e}")

    return "free"


def require_tier(minimum_tier: str):
    """
    Dependency factory: يقيد الوصول بناءً على الباقة.
    مثال: `Depends(require_tier("premium"))`
    """
    async def tier_checker(user_tier: str = Depends(get_user_tier)) -> str:
        tier_levels = {"free": 0, "plus": 1, "premium": 2, "pro": 3, "yearly": 4}
        user_level = tier_levels.get(user_tier, 0)
        required_level = tier_levels.get(minimum_tier, 0)
        if user_level < required_level:
            raise HTTPException(status_code=403, detail=f"هذه الميزة تتطلب باقة {minimum_tier} على الأقل")
        return user_tier
    return tier_checker

logger.info("✅ Auth Dependency v3.0 initialized")
