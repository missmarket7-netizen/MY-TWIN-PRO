"""Revenue Service – tracks revenue and projections."""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("revenue_service")

async def get_monthly_revenue() -> Dict[str, Any]:
    """Calculate monthly recurring revenue (MRR)."""
    PRICES = {"free": 0, "plus": 5.99, "premium": 14.99, "pro": 18.33, "yearly": 16.58}
    db = get_db()
    try:
        r = db.table("profiles").select("tier").execute()
        if not r.data:
            return {"mrr": 0, "subscribers": 0, "by_tier": {}}
        
        revenue = 0
        by_tier = {}
        for user in r.data:
            tier = user.get("tier", "free")
            price = PRICES.get(tier, 0)
            revenue += price
            by_tier[tier] = by_tier.get(tier, 0) + price
        
        return {
            "mrr": round(revenue, 2),
            "subscribers": len(r.data),
            "by_tier": {k: round(v, 2) for k, v in by_tier.items()},
        }
    except Exception as e:
        logger.error(f"Failed to calculate revenue: {e}")
        return {"mrr": 0, "subscribers": 0, "by_tier": {}}

async def get_revenue_projection(months: int = 12, growth_rate: float = 0.1) -> List[Dict[str, Any]]:
    """Project future revenue based on current MRR and growth rate."""
    current = await get_monthly_revenue()
    mrr = current.get("mrr", 0)
    projections = []
    for i in range(months):
        mrr = mrr * (1 + growth_rate)
        projections.append({"month": i + 1, "projected_mrr": round(mrr, 2)})
    return projections
