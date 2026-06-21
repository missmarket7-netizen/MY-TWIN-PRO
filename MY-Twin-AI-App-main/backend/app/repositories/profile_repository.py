"""
Profile Repository v2.0 – متوافق مع الهيكل الجديد
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger(__name__)

async def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        r = db.table("profiles").select("*").eq("id", user_id).single().execute()
        return r.data if r.data else None
    except Exception as e:
        logger.warning(f"get_profile failed: {e}")
        return None

async def update_last_active(user_id: str) -> None:
    db = get_db()
    try:
        db.table("profiles").update({"last_active": datetime.now(timezone.utc).isoformat()}).eq("id", user_id).execute()
    except Exception as e:
        logger.warning(f"update_last_active failed: {e}")

async def update_energy(user_id: str, energy: int, messages_used: int, tokens_used: int) -> None:
    db = get_db()
    try:
        db.table("profiles").update({
            "twin_energy": energy,
            "daily_messages_used": messages_used,
            "daily_tokens_used": tokens_used,
        }).eq("id", user_id).execute()
    except Exception as e:
        logger.warning(f"update_energy failed: {e}")

async def update_tier(user_id: str, tier: str) -> None:
    db = get_db()
    try:
        db.table("profiles").update({"tier": tier}).eq("id", user_id).execute()
    except Exception as e:
        logger.warning(f"update_tier failed: {e}")

async def get_recent_active_users(hours: int = 168) -> List[str]:
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - __import__('datetime').timedelta(hours=hours)).isoformat()
        r = db.table("profiles").select("id").gte("last_active", cutoff).execute()
        return [u["id"] for u in (r.data or [])]
    except:
        return []

logger.info("✅ Profile Repository v2.0")
