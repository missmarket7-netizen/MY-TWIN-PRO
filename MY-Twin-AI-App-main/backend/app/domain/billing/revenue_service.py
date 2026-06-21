"""
Revenue Service v2.0 – تتبع الإيرادات والأرباح (متكامل)
=============================================================
- الإيرادات الشهرية المتكررة (MRR)
- توقعات النمو (Projections)
- تحليل الإيرادات من الإعلانات
- تكامل مع Observability
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("revenue_service")

# أسعار الباقات
SUBSCRIPTION_PRICES = {
    "free": 0,
    "plus": 5.99,
    "premium": 14.99,
    "pro": 18.33,
    "yearly": 16.58,
}

# متوسط إيراد الإعلان الواحد (تقديري)
AD_REVENUE_PER_VIEW = 0.002  # 2 سنت لكل إعلان

async def get_monthly_revenue() -> Dict[str, Any]:
    """حساب الإيرادات الشهرية المتكررة (MRR)"""
    db = get_db()
    try:
        r = db.table("profiles").select("tier").execute()
        if not r.data:
            return {"mrr": 0, "subscribers": 0, "by_tier": {}}

        revenue = 0
        by_tier = {}
        subscribers = len(r.data)

        for user in r.data:
            tier = user.get("tier", "free")
            price = SUBSCRIPTION_PRICES.get(tier, 0)
            revenue += price
            by_tier[tier] = by_tier.get(tier, 0) + price

        return {
            "mrr": round(revenue, 2),
            "subscribers": subscribers,
            "by_tier": {k: round(v, 2) for k, v in by_tier.items()},
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"فشل حساب الإيرادات: {e}")
        return {"mrr": 0, "subscribers": 0, "by_tier": {}}

async def get_ad_revenue(days: int = 30) -> Dict[str, Any]:
    """حساب إيرادات الإعلانات لآخر فترة"""
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        r = db.table("ad_views").select("count").gte("created_at", cutoff).execute()
        total_views = sum(row.get("count", 0) for row in (r.data or []))
        revenue = total_views * AD_REVENUE_PER_VIEW
        return {
            "total_views": total_views,
            "estimated_revenue": round(revenue, 2),
            "period_days": days,
        }
    except:
        return {"total_views": 0, "estimated_revenue": 0.0}

async def get_total_revenue(days: int = 30) -> Dict[str, Any]:
    """إجمالي الإيرادات (اشتراكات + إعلانات)"""
    subs = await get_monthly_revenue()
    ads = await get_ad_revenue(days)
    total = subs.get("mrr", 0) + ads.get("estimated_revenue", 0)
    return {
        "subscription_mrr": subs.get("mrr", 0),
        "ad_revenue": ads.get("estimated_revenue", 0),
        "total_revenue": round(total, 2),
        "period_days": days,
    }

async def get_revenue_projection(months: int = 12, growth_rate: float = 0.1) -> List[Dict[str, Any]]:
    """توقعات الإيرادات المستقبلية"""
    current = await get_monthly_revenue()
    mrr = current.get("mrr", 0)
    projections = []
    for i in range(months):
        mrr = mrr * (1 + growth_rate)
        projections.append({"month": i + 1, "projected_mrr": round(mrr, 2)})
    return projections

logger.info("✅ Revenue Service v2.0 initialized")
