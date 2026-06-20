"""Admin Dashboard Routes."""
from fastapi import APIRouter, HTTPException, Header
from app.infrastructure.database.supabase_client import get_db
from app.observability.metrics_service import metrics
from app.domain.billing.revenue_service import get_monthly_revenue
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
    return {
        "total_users": total_users,
        "revenue": revenue,
        "health": health,
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    }
