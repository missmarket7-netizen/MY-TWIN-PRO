"""
MyTwin – Auth Dependency
==========================
حقن المستخدم في FastAPI عبر فك JWT محلياً.
لا استدعاء شبكي لـ Supabase.
"""
import logging
from fastapi import Header, HTTPException
import jwt
from jwt.exceptions import PyJWTError
from app.core.config import config

logger = logging.getLogger(__name__)


async def get_current_user_id(
    authorization: str = Header(..., alias="Authorization"),
) -> str:
    """
    استخراج user_id من توكن Bearer.
    يرفع 401 إذا كان التوكن مفقوداً أو منتهياً.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="مفقود أو غير صالح")
    
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="توكن فارغ")
    
    try:
        payload = jwt.decode(
            token,
            config.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True, "verify_aud": True},
        )
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="توكن بدون هوية")
        return user_id
    except PyJWTError as e:
        logger.warning(f"فشل فك JWT: {e}")
        raise HTTPException(status_code=401, detail="توكن غير صالح أو منتهي")
