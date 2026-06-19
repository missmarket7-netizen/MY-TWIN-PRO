"""Profile Repository – user profiles, tier, energy, settings, referrals."""
import logging
from typing import Optional, List
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db
from app.models.profile import UserProfile, TierConfig, VoiceConfig
from app.models.tier import get_tier_config

logger = logging.getLogger(__name__)


async def get_profile(user_id: str) -> Optional[UserProfile]:
    db = get_db()
    try:
        r = db.table("profiles").select("*").eq("id", user_id).single().execute()
        if r.data:
            d = r.data
            return UserProfile(
                user_id=user_id, full_name=d.get("full_name"),
                twin_name=d.get("twin_name","توأمك"), twin_gender=d.get("twin_gender","female"),
                twin_style=d.get("twin_style","supportive"), lang=d.get("lang","ar"),
                tier=d.get("tier","free"), signup_date=d.get("created_at"),
                last_active=d.get("last_active", datetime.now(timezone.utc).isoformat()),
                daily_messages_used=d.get("daily_messages_used",0),
                daily_tokens_used=d.get("daily_tokens_used",0),
                twin_energy=d.get("twin_energy",100),
                voice_config=VoiceConfig(**d.get("voice_config",{}) if d.get("voice_config") else {}),
                tier_config=TierConfig(**d.get("tier_config",{}) if d.get("tier_config") else {}),
            )
    except Exception as e:
        logger.warning(f"get_profile failed: {e}")
    return None


async def update_last_active(user_id: str) -> None:
    db = get_db()
    try:
        db.table("profiles").update({"last_active": datetime.now(timezone.utc).isoformat()})\
            .eq("id", user_id).execute()
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
        tc = get_tier_config(tier)
        db.table("profiles").update({
            "tier": tier,
            "tier_config": tc.model_dump(),
        }).eq("id", user_id).execute()
    except Exception as e:
        logger.warning(f"update_tier failed: {e}")


async def activate_referral_bonus(user_id: str, bonus_messages: int = 5, bonus_tokens: int = 500) -> None:
    db = get_db()
    try:
        db.table("referral_usage").insert({
            "id": user_id,
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "bonus_messages": bonus_messages,
            "bonus_tokens": bonus_tokens,
        }).execute()
    except Exception as e:
        logger.warning(f"activate_referral_bonus failed: {e}")


async def get_profiles_for_cleanup(tier: str) -> List[str]:
    db = get_db()
    try:
        r = db.table("profiles").select("id").eq("tier", tier).execute()
        return [u["id"] for u in (r.data or [])]
    except: return []


async def count_all_memories() -> int:
    db = get_db()
    try:
        r = db.table("memories").select("id", count="exact").execute()
        return r.count or 0
    except: return 0


async def get_recent_active_users(hours: int = 168) -> List[str]:
    db = get_db()
    try:
        cutoff = datetime.now(timezone.utc).isoformat()
        r = db.table("profiles").select("id").gte("last_active", cutoff).execute()
        return [u["id"] for u in (r.data or [])]
    except: return []
