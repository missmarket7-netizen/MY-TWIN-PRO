"""
MyTwin – Referral System v3.0 (متوافق مع TCMA)
"""
import os, hashlib, logging
from datetime import datetime, timezone

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger("referral_service")
BASE_URL = os.getenv("EXPO_PUBLIC_API_URL", "https://mytwin.app")

def generate_referral_code(uid: str) -> str:
    return "MT" + hashlib.sha256(uid.encode()).hexdigest()[:6].upper()

def get_referral_link(uid: str) -> str:
    code = generate_referral_code(uid)
    if DB_AVAILABLE:
        try:
            db = get_db()
            existing = db.table("profiles").select("referral_code").eq("id", uid).single().execute()
            if not existing.data or not existing.data.get("referral_code"):
                db.table("profiles").update({"referral_code": code}).eq("id", uid).execute()
        except Exception as e:
            logger.warning(f"Failed to store referral code: {e}")
    return f"{BASE_URL}/join?ref={code}"

def activate_referral(uid: str, code: str) -> dict:
    if not DB_AVAILABLE:
        return {"error": "no_db"}
    
    db = get_db()
    code = code.upper().strip()
    
    # البحث عن صاحب الكود
    owner = db.table("profiles").select("id").eq("referral_code", code).single().execute()
    if not owner.data:
        return {"error": "invalid_code"}
    
    inviter_id = owner.data["id"]
    if inviter_id == uid:
        return {"error": "own_code"}
    
    # منع التكرار
    existing = db.table("referral_usage").select("*").eq("user_id", uid).eq("code", code).execute()
    if existing.data:
        return {"error": "already_used"}
    
    # تسجيل الاستخدام
    db.table("referral_usage").insert({
        "user_id": uid, "code": code, "inviter_id": inviter_id,
        "activated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    
    # منح المكافأة (500 توكن للطرفين)
    bonus = 500
    try:
        from app.domain.billing.token_limits import add_referral_bonus
        add_referral_bonus(uid, bonus)
        add_referral_bonus(inviter_id, bonus)
    except ImportError:
        logger.warning("Token system not available, skipping bonus")
    
    return {"success": True, "bonus": bonus, "inviter_id": inviter_id}
