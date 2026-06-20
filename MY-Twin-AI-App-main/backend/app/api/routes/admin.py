"""Admin Panel Routes."""
from fastapi import APIRouter, HTTPException, Header
from app.infrastructure.database.supabase_client import get_db
from app.observability.metrics_service import metrics
from app.domain.billing.revenue_service import get_monthly_revenue
from app.core.feature_flags import get_all_flags, set_feature_flag
from app.domain.billing.cost_dashboard import get_cost_summary
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "admin-secret-key")

async def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(403, "Forbidden")

@router.get("/stats")
async def admin_stats(x_admin_key: str = Header(...)):
    await verify_admin(x_admin_key)
    db = get_db()
    total_users = db.table("profiles").select("id", count="exact").execute().count
    revenue = await get_monthly_revenue()
    health = metrics.get_snapshot()
    flags = get_all_flags()
    cost = await get_cost_summary()
    return {
        "total_users": total_users,
        "revenue": revenue,
        "health": health,
        "feature_flags": flags,
        "cost_summary": cost,
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    }

@router.post("/flags")
async def admin_flags(feature: str, enabled: bool, x_admin_key: str = Header(...)):
    await verify_admin(x_admin_key)
    set_feature_flag(feature, enabled)
    return {"feature": feature, "enabled": enabled}
