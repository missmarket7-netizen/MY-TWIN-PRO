"""Subscription Service – manages user subscriptions and entitlements."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("subscription_service")

SUBSCRIPTION_PLANS = {
    "free": {"name": "Free", "price": 0, "messages": 10, "features": ["chat"]},
    "plus": {"name": "Plus", "price": 5.99, "messages": 30, "features": ["chat", "study", "content", "dreams"]},
    "premium": {"name": "Premium", "price": 14.99, "messages": 100, "features": ["chat", "study", "code", "business", "coach", "content", "dreams", "image"]},
    "pro": {"name": "Pro", "price": 110, "billing_period": "6_months", "messages": 500, "features": ["all"]},
    "yearly": {"name": "Yearly", "price": 199, "billing_period": "yearly", "messages": 9999, "features": ["all"]},
}

async def get_user_subscription(user_id: str) -> Dict[str, Any]:
    db = get_db()
    try:
        r = db.table("profiles").select("tier,subscription_expires,subscription_id").eq("id", user_id).single().execute()
        if r.data:
            tier = r.data.get("tier", "free")
            plan = SUBSCRIPTION_PLANS.get(tier, SUBSCRIPTION_PLANS["free"])
            return {
                "tier": tier,
                "plan": plan,
                "expires_at": r.data.get("subscription_expires"),
                "is_active": True,
                "subscription_id": r.data.get("subscription_id"),
            }
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
    return {"tier": "free", "plan": SUBSCRIPTION_PLANS["free"], "is_active": True}

async def check_subscription_active(user_id: str) -> bool:
    sub = await get_user_subscription(user_id)
    if sub["tier"] == "free":
        return True
    if sub.get("expires_at"):
        try:
            expires = datetime.fromisoformat(sub["expires_at"].replace("Z", "+00:00"))
            return expires > datetime.now(timezone.utc)
        except:
            return True
    return True

async def upgrade_subscription(user_id: str, tier: str, duration_days: int = 30) -> bool:
    db = get_db()
    try:
        expires = (datetime.now(timezone.utc) + timedelta(days=duration_days)).isoformat()
        db.table("profiles").update({
            "tier": tier,
            "subscription_expires": expires,
            "subscription_id": f"sub_{user_id[:8]}_{tier}",
        }).eq("id", user_id).execute()
        logger.info(f"✅ User {user_id} upgraded to {tier}")
        return True
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {e}")
        return False
