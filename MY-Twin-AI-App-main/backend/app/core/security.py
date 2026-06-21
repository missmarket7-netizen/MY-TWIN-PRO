"""
Security v2.0 – JWT، صلاحيات، وأمان متكامل
============================================
- فك تشفير JWT من Supabase
- استخراج الصلاحيات والباقة
- دعم متعدد الخوارزميات
"""
import os, logging
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError, InvalidTokenError

logger = logging.getLogger("security")

# الإعدادات
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
SUPABASE_JWT_ALGORITHMS = ["HS256", "RS256"]  # دعم خوارزميات متعددة
TOKEN_AUDIENCE = os.getenv("SUPABASE_JWT_AUD", "authenticated")

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    فك تشفير JWT من Supabase.
    يعيد payload كاملة أو None إذا فشل.
    """
    if not token:
        logger.warning("محاولة فك تشفير بدون رمز")
        return None
    
    if not SUPABASE_JWT_SECRET:
        logger.error("SUPABASE_JWT_SECRET غير موجود في البيئة")
        return None

    # تنظيف الرمز (إزالة Bearer إن وجدت)
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=SUPABASE_JWT_ALGORITHMS,
            audience=TOKEN_AUDIENCE,
            options={
                "verify_exp": True,
                "verify_aud": True,
                "verify_signature": True,
                "require": ["exp", "sub"]
            }
        )
        return payload
    except ExpiredSignatureError:
        logger.warning("انتهت صلاحية الرمز JWT")
        return None
    except InvalidTokenError as e:
        logger.error(f"رمز JWT غير صالح: {e}")
        return None
    except PyJWTError as e:
        logger.error(f"فشل فك تشفير JWT: {e}")
        return None

def extract_user_id(payload: Dict[str, Any]) -> Optional[str]:
    """استخراج معرف المستخدم من payload"""
    if not payload:
        return None
    return payload.get("sub") or payload.get("user_id") or payload.get("id") or None

def extract_tier(payload: Dict[str, Any]) -> str:
    """استخراج باقة المستخدم (افتراضياً free)"""
    if not payload:
        return "free"
    return payload.get("tier") or payload.get("user_metadata", {}).get("tier", "free")

def extract_role(payload: Dict[str, Any]) -> str:
    """استخراج دور المستخدم (افتراضياً authenticated)"""
    if not payload:
        return "authenticated"
    return payload.get("role", "authenticated")

def validate_token(token: str) -> bool:
    """التحقق من صحة الرمز فقط (بدون استخراج بيانات)"""
    return decode_access_token(token) is not None

def get_user_context(token: str) -> Dict[str, Any]:
    """
    استخراج سياق المستخدم الكامل من الرمز.
    يعيد: user_id, tier, role, email (إن وجد)
    """
    payload = decode_access_token(token)
    if not payload:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user_id": extract_user_id(payload),
        "tier": extract_tier(payload),
        "role": extract_role(payload),
        "email": payload.get("email", ""),
        "metadata": payload.get("user_metadata", {}),
    }

logger.info("✅ Security v2.0 initialized")
