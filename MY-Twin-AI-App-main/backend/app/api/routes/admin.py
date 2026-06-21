"""
Admin Panel Routes v3.0 – لوحة إدارة متكاملة
=================================================
- إحصائيات شاملة (مستخدمين، إيرادات، تكاليف، صحة)
- إدارة أعلام الميزات (Feature Flags)
- إدارة الذاكرة (تنظيف، إحصائيات TCMA)
- إدارة المستخدمين (بحث، حظر، حذف)
- تكامل مع جميع الخدمات
"""
import os, logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("admin_routes")
router = APIRouter(prefix="/api/admin", tags=["admin"])
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "admin-secret-key")

# ============================================================
# المصادقة الإدارية
# ============================================================
async def verify_admin(x_admin_key: str = Header(...)):
    """التحقق من صلاحية مدير النظام"""
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(403, "Forbidden: Invalid Admin Key")

# ============================================================
# نماذج البيانات
# ============================================================
class FlagUpdateRequest(BaseModel):
    feature: str
    enabled: bool

class UserActionRequest(BaseModel):
    user_id: str
    reason: Optional[str] = "Administrative action"

# ============================================================
# لوحة المعلومات الرئيسية
# ============================================================
@router.get("/stats")
async def admin_stats(x_admin_key: str = Header(...)):
    await verify_admin(x_admin_key)
    db = get_db()

    # 1. إحصائيات المستخدمين
    total_users = db.table("profiles").select("id", count="exact").execute().count
    active_today = db.table("profiles").select("id").gte("last_active", datetime.now(timezone.utc).strftime("%Y-%m-%d")).execute()
    premium_users = db.table("profiles").select("id", count="exact").in_("tier", ["premium", "pro", "yearly"]).execute().count

    # 2. البيانات المالية
    from app.domain.billing.revenue_service import get_monthly_revenue
    revenue = await get_monthly_revenue()

    # 3. صحة النظام
    from app.observability.metrics_service import metrics
    health = metrics.get_snapshot()

    # 4. أعلام الميزات
    from app.core.feature_flags import get_all_flags
    flags = get_all_flags()

    # 5. التكاليف
    from app.domain.billing.cost_dashboard import get_cost_summary
    cost = await get_cost_summary()

    return {
        "users": {
            "total": total_users,
            "active_today": len(active_today.data or []),
            "premium": premium_users,
        },
        "revenue": revenue,
        "health": health,
        "feature_flags": flags,
        "cost_summary": cost,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# ============================================================
# إدارة أعلام الميزات
# ============================================================
@router.get("/flags")
async def get_flags(x_admin_key: str = Header(...)):
    await verify_admin(x_admin_key)
    from app.core.feature_flags import get_all_flags
    return get_all_flags()

@router.post("/flags")
async def set_flag(body: FlagUpdateRequest, x_admin_key: str = Header(...)):
    await verify_admin(x_admin_key)
    from app.core.feature_flags import set_feature_flag
    set_feature_flag(body.feature, body.enabled)
    return {"feature": body.feature, "enabled": body.enabled, "status": "updated"}

# ============================================================
# إدارة الذاكرة (TCMA)
# ============================================================
@router.post("/memory/cleanup")
async def force_memory_cleanup(x_admin_key: str = Header(...)):
    """تشغيل تنظيف الذاكرة يدوياً"""
    await verify_admin(x_admin_key)
    from app.infrastructure.cache.memory_cleanup_service import run_memory_cleanup
    result = await run_memory_cleanup(dry=False)
    return result

@router.get("/memory/stats")
async def memory_storage_stats(x_admin_key: str = Header(...)):
    """إحصائيات تخزين TCMA"""
    await verify_admin(x_admin_key)
    from app.infrastructure.cache.memory_cleanup_service import get_storage_stats
    return await get_storage_stats()

# ============================================================
# إدارة المستخدمين
# ============================================================
@router.get("/users/search")
async def search_users(query: str, x_admin_key: str = Header(...)):
    """البحث عن مستخدم"""
    await verify_admin(x_admin_key)
    db = get_db()
    try:
        result = db.table("profiles").select("id,email,full_name,tier,created_at,last_active").or_(f"email.ilike.%{query}%,full_name.ilike.%{query}%").limit(10).execute()
        return {"users": result.data or []}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/users/{user_id}")
async def get_user_details(user_id: str, x_admin_key: str = Header(...)):
    """تفاصيل مستخدم كاملة"""
    await verify_admin(x_admin_key)
    db = get_db()
    profile = db.table("profiles").select("*").eq("id", user_id).single().execute()
    if not profile.data:
        raise HTTPException(404, "User not found")

    # جلب إحصائيات الذاكرة
    from app.infrastructure.database.memory_repo import count_memories
    memory_count = await count_memories(user_id)

    return {
        "profile": profile.data,
        "memory_count": memory_count,
        "queried_at": datetime.now(timezone.utc).isoformat(),
    }

@router.post("/users/ban")
async def ban_user(body: UserActionRequest, x_admin_key: str = Header(...)):
    """حظر مستخدم"""
    await verify_admin(x_admin_key)
    db = get_db()
    db.table("profiles").update({"status": "banned", "ban_reason": body.reason}).eq("id", body.user_id).execute()
    return {"status": "banned", "user_id": body.user_id}

@router.post("/users/unban")
async def unban_user(body: UserActionRequest, x_admin_key: str = Header(...)):
    """رفع الحظر عن مستخدم"""
    await verify_admin(x_admin_key)
    db = get_db()
    db.table("profiles").update({"status": "active", "ban_reason": None}).eq("id", body.user_id).execute()
    return {"status": "active", "user_id": body.user_id}

logger.info("✅ Admin Routes v3.0 initialized")
