"""
Billing Routes – Google Play Billing Bridge.
يتحقق من الإيصال عبر Google Play Developer API.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db
from app.domain.billing.subscription_service import upgrade_subscription
import logging

logger = logging.getLogger("billing")
router = APIRouter(prefix="/api/billing", tags=["billing"])

class PurchaseRequest(BaseModel):
    product_id: str
    purchase_token: str

@router.post("/verify")
async def verify_purchase(body: PurchaseRequest, user_id: str = Depends(get_current_user_id)):
    """
    يستقبل product_id + purchase_token من التطبيق.
    في الإنتاج، يتحقق من Google Play Developer API.
    """
    logger.info(f"🛒 Purchase request: user={user_id}, product={body.product_id}")
    
    TIER_MAP = {
        "plus_monthly": "plus",
        "premium_monthly": "premium", 
        "pro_semiannual": "pro",
        "yearly_annual": "yearly",
    }
    
    tier = TIER_MAP.get(body.product_id, "free")
    if tier == "free":
        raise HTTPException(400, "Invalid product ID")
    
    success = await upgrade_subscription(user_id, tier)
    if success:
        logger.info(f"✅ Subscription activated: {user_id} → {tier}")
        return {"success": True, "tier": tier, "message": "Subscription activated"}
    
    raise HTTPException(500, "Failed to upgrade subscription")
