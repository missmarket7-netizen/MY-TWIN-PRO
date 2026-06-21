"""
Development Routes v2.0 – اختبار متقدم
=========================================
- إنشاء مستخدم اختبار
- جلب إحصائيات الذاكرة (TCMA)
- فحص حالة النظام الداخلية
"""
import os, logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("dev_routes")
router = APIRouter(prefix="/api/dev", tags=["dev"])

DEV_SECRET = os.getenv("DEV_SECRET", "devsecret123")

class DevTokenRequest(BaseModel):
    secret: str = "devsecret123"
    email: str = "sir.market7@gmail.com"
    password: str = "M#m2606.1307"

@router.post("/token")
async def get_dev_token(body: DevTokenRequest):
    """إنشاء أو تسجيل دخول مستخدم اختبار"""
    if body.secret != DEV_SECRET:
        raise HTTPException(403, "Wrong dev secret")
    
    db = get_db()
    try:
        result = db.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        if result.user and result.session:
            return {"token": result.session.access_token, "user_id": result.user.id, "created": False}
    except:
        pass
    
    try:
        result = db.auth.sign_up({
            "email": body.email,
            "password": body.password,
        })
        if result.user and result.session:
            db.table("profiles").insert({
                "id": result.user.id,
                "email": body.email,
                "full_name": "Test User",
                "twin_name": "توأمي",
                "lang": "ar",
                "tier": "free",
                "onboarded": True,
            }).execute()
            return {"token": result.session.access_token, "user_id": result.user.id, "created": True}
    except Exception as e:
        raise HTTPException(500, f"Failed: {e}")
    
    raise HTTPException(500, "Could not create or login user")

@router.get("/memory-stats")
async def get_memory_stats(user_id: str):
    """جلب إحصائيات الذاكرة (للتطوير فقط)"""
    from app.infrastructure.cache.memory_cleanup_service import get_storage_stats
    stats = await get_storage_stats()
    return {"user_id": user_id, "tcma_tables": stats}

@router.get("/test-tcma")
async def test_tcma(user_id: str):
    """اختبار طبقات TCMA"""
    results = {}
    # Emotional memory
    try:
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        patterns = await get_emotional_patterns(user_id, days=7)
        results["emotional"] = patterns
    except Exception as e:
        results["emotional"] = str(e)
    # Identity
    try:
        from app.memory.identity.identity_model import get_identity
        identity = await get_identity(user_id)
        results["identity"] = identity
    except Exception as e:
        results["identity"] = str(e)
    return results
