"""
MyTwin – Unified Limits & Tier Manager v4.0
- حدود الأدوات مخصصة بالباقة (Tier 1,2,3)
- طاقة التوأم مرتبطة بعدد الرسائل المتبقية
- مؤشر الترابط يكافئ التواصل اليومي المتكرر (Streak)
- سقف Bond ومكافآت الإحالة
"""
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, Dict
import os
from supabase import create_client, Client
from cache import get, set as cache_set

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
db: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ── حدود الرسائل اليومية ─────────────────────────────
DAILY_MESSAGES = {
    "free": 15, "free_week1": 20, "free_week2": 17, "free_week3": 15,
    "plus": 50, "premium": 150, "pro": 500, "yearly": 9999,
}

# ── حدود التوكن اليومية ──────────────────────────────
BASE_TOK = {
    "free": 500, "free_week1": 1500, "free_week2": 1000, "free_week3": 700,
    "plus": 1500, "premium": 4000, "pro": 7000, "yearly": 15000,
}

# ── سقف الـ Bond حسب الباقة ──────────────────────────
BOND_CEILING = {
    "free": 28, "free_week1": 28, "free_week2": 28, "free_week3": 28,
    "plus": 70, "premium": 90, "pro": 100, "yearly": 100,
}

# ── نماذج AI حسب الباقة ──────────────────────────────
TIER_MODELS = {
    "free":     ["groq", "gemma4"],
    "plus":     ["groq", "llama4", "deepseek", "gemma4"],
    "premium":  ["groq", "llama4", "deepseek", "qwen", "minimax", "gemma4"],
    "pro":      ["groq", "llama4", "deepseek", "qwen", "minimax", "gemma4", "gptoss", "gemini"],
    "yearly":   ["groq", "llama4", "deepseek", "qwen", "minimax", "gemma4", "gptoss", "gemini"],
}

# ── حدود الميزات اليومية حسب الباقة ─────────────────
TIER_FEATURES = {
    "free": {
        "tts": False, "dreams": False, "coaching": False,
        "proactive": False, "long_memory": False, "weekly_report": False, "smart_home": False,
        "daily_limits": {
            "youtube": 2, "search": 1, "weather": 3,
            "spotify": 0, "calendar": 0, "news": 1, "maps": 1,
            "currency": 1, "homeassistant": 0, "email": 0, "telegram": 1,
            "notes": 5, "tasks": 5,
        }
    },
    "plus": {
        "tts": True, "dreams": False, "coaching": False,
        "proactive": True, "long_memory": True, "weekly_report": False, "smart_home": False,
        "daily_limits": {
            "youtube": 5, "search": 5, "weather": 10,
            "spotify": 3, "calendar": 3, "news": 5, "maps": 5,
            "currency": 5, "homeassistant": 0, "email": 2, "telegram": 5,
            "notes": 20, "tasks": 20,
        }
    },
    "premium": {
        "tts": True, "dreams": True, "coaching": True,
        "proactive": True, "long_memory": True, "weekly_report": True, "smart_home": False,
        "daily_limits": {
            "youtube": 10, "search": 10, "weather": 20,
            "spotify": 10, "calendar": 10, "news": 10, "maps": 10,
            "currency": 10, "homeassistant": 0, "email": 10, "telegram": 20,
            "notes": 100, "tasks": 100,
        }
    },
    "pro": {
        "tts": True, "dreams": True, "coaching": True,
        "proactive": True, "long_memory": True, "weekly_report": True, "smart_home": True,
        "daily_limits": {
            "youtube": 30, "search": 30, "weather": 50,
            "spotify": 30, "calendar": 30, "news": 30, "maps": 30,
            "currency": 30, "homeassistant": 50, "email": 50, "telegram": 50,
            "notes": 500, "tasks": 500,
        }
    },
    "yearly": {
        "tts": True, "dreams": True, "coaching": True,
        "proactive": True, "long_memory": True, "weekly_report": True, "smart_home": True,
        "daily_limits": {
            "youtube": 999, "search": 999, "weather": 999,
            "spotify": 999, "calendar": 999, "news": 999, "maps": 999,
            "currency": 999, "homeassistant": 999, "email": 999, "telegram": 999,
            "notes": 9999, "tasks": 9999,
        }
    },
}

REFERRAL_BONUS_TOK = 500
REFERRAL_DAILY_MSG_BONUS = 5
STREAK_BONUS_INCREMENT = 2  # رسائل إضافية لكل 3 أيام تواصل متتالية
STREAK_DAYS_THRESHOLD = 3   # عدد الأيام للحصول على مكافأة الاستمرارية

def _get_effective_tier(tier: str, signup_date: Optional[str] = None) -> str:
    if tier == "free" and signup_date:
        try:
            signup = datetime.fromisoformat(signup_date)
            days = (datetime.now(timezone.utc) - signup).days
            if days < 7:  return "free_week1"
            if days < 14: return "free_week2"
            if days < 21: return "free_week3"
        except: pass
    return tier

def _get_daily_referral_bonus(uid: str) -> int:
    referral_data = get(f"referral:{uid}")
    if not referral_data: return 0
    try:
        activated_at = datetime.fromisoformat(referral_data.get("activated_at", ""))
        days_since = (datetime.now(timezone.utc) - activated_at).days
        if days_since < 7: return REFERRAL_DAILY_MSG_BONUS
    except: pass
    return 0

def _get_referral_tok_bonus(uid: str) -> int:
    cache_key = f"referral_bonus:{uid}"
    cached = get(cache_key)
    if cached is not None: return cached
    if db:
        try:
            total = 0
            now = datetime.now(timezone.utc)
            res = db.table("referral_usage").select("activated_at").eq("inviter_id", uid).execute()
            if res.data:
                for row in res.data:
                    activated = datetime.fromisoformat(row["activated_at"].replace("Z", "+00:00"))
                    if (now - activated).days < 30: total += REFERRAL_BONUS_TOK
            res2 = db.table("referral_usage").select("activated_at").eq("id", uid).execute()
            if res2.data:
                for row in res2.data:
                    activated = datetime.fromisoformat(row["activated_at"].replace("Z", "+00:00"))
                    if (now - activated).days < 30: total += REFERRAL_BONUS_TOK
            cache_set(cache_key, total, 3600)
            return total
        except Exception as e:
            print(f"Referral bonus error: {e}")
    return 0

def _get_streak_bonus(uid: str) -> int:
    """حساب مكافأة التواصل اليومي المتكرر"""
    if not db:
        return 0
    try:
        # جلب آخر 10 أيام نشطة
        res = db.table("profiles").select("last_active").eq("id", uid).single().execute()
        if not res.data or not res.data.get("last_active"):
            return 0
        
        last_active = datetime.fromisoformat(res.data["last_active"].replace("Z", "+00:00"))
        today = datetime.now(timezone.utc).date()
        days_diff = (today - last_active.date()).days
        
        if days_diff > 1:  # انقطع اليوم أو أكثر
            return 0
        
        # حساب عدد الأيام المتتالية (من جدول message_log مثلاً)
        streak_key = f"streak:{uid}"
        current_streak = get(streak_key) or 0
        
        if days_diff == 0:  # نشط اليوم
            current_streak += 1
            cache_set(streak_key, current_streak, 86400 * 2)  # يحتفظ به ليومين
        
        if current_streak >= STREAK_DAYS_THRESHOLD:
            bonus = (current_streak // STREAK_DAYS_THRESHOLD) * STREAK_BONUS_INCREMENT
            return min(bonus, 10)  # أقصى مكافأة 10 رسائل إضافية
    except:
        pass
    return 0

def check_message_limit(uid: str, tier: str, signup_date: Optional[str] = None) -> Tuple[bool, int, str]:
    effective = _get_effective_tier(tier, signup_date)
    today = datetime.now(timezone.utc).date().isoformat()
    key = f"msg:{uid}:{today}"
    used = get(key) or 0
    base = DAILY_MESSAGES.get(effective, 15)
    referral_bonus = _get_daily_referral_bonus(uid)
    streak_bonus = _get_streak_bonus(uid)
    limit = base + referral_bonus + streak_bonus
    if used >= limit: return False, 0, "daily_limit_reached"
    cache_set(key, used + 1, 86400)
    return True, limit - used - 1, "ok"

def check_tok(uid: str, tier: str, est: int, signup_date: Optional[str] = None) -> Tuple[bool, int]:
    effective = _get_effective_tier(tier, signup_date)
    today = datetime.now(timezone.utc).date().isoformat()
    key = f"tok:{uid}:{today}"
    used = get(key) or 0
    limit = BASE_TOK.get(effective, 500) + _get_referral_tok_bonus(uid)
    if used + est > limit: return False, max(0, limit - used)
    cache_set(key, used + est, 86400)
    return True, limit - used - est

def get_bond_ceiling(tier: str, signup_date: Optional[str] = None) -> int:
    effective = _get_effective_tier(tier, signup_date)
    return BOND_CEILING.get(effective, 28)

def apply_bond_ceiling(bond: float, tier: str, signup_date: Optional[str] = None) -> float:
    return min(bond, float(get_bond_ceiling(tier, signup_date)))

def get_tier_models(tier: str) -> list:
    base = tier.split("_")[0] if "_" in tier else tier
    return TIER_MODELS.get(base, TIER_MODELS["free"])

def get_tier_features(tier: str) -> dict:
    base = tier.split("_")[0] if "_" in tier else tier
    return TIER_FEATURES.get(base, TIER_FEATURES["free"])

def get_daily_feature_limit(tier: str, feature_name: str) -> int:
    features = get_tier_features(tier)
    return features.get("daily_limits", {}).get(feature_name, 0)

def check_feature_usage(uid: str, tier: str, feature_name: str) -> Tuple[bool, int]:
    limit = get_daily_feature_limit(tier, feature_name)
    if limit == 0:
        return False, 0
    today = datetime.now(timezone.utc).date().isoformat()
    key = f"feat:{uid}:{feature_name}:{today}"
    used = get(key) or 0
    if used >= limit:
        return False, 0
    cache_set(key, used + 1, 86400)
    return True, limit - used - 1

def get_twin_energy(uid: str, tier: str, signup_date: Optional[str] = None) -> float:
    """حساب طاقة التوأم بناءً على عدد الرسائل المتبقية"""
    _, remaining, _ = check_message_limit(uid, tier, signup_date)
    effective = _get_effective_tier(tier, signup_date)
    base = DAILY_MESSAGES.get(effective, 15)
    energy = (remaining / base) * 100 if base > 0 else 0
    return min(100.0, max(0.0, energy))

def get_bond_streak_multiplier(uid: str) -> float:
    """مضاعف الترابط عند التواصل اليومي المتكرر"""
    streak_key = f"streak:{uid}"
    streak = get(streak_key) or 0
    if streak >= 7:   # أسبوع تواصل يومي
        return 1.5
    elif streak >= 3: # 3 أيام
        return 1.2
    elif streak >= 1:
        return 1.0
    return 1.0

def activate_referral_bonus(uid: str) -> None:
    cache_set(f"referral:{uid}", {
        "activated_at": datetime.now(timezone.utc).isoformat(),
        "daily_bonus": REFERRAL_DAILY_MSG_BONUS,
        "duration_days": 7,
    }, 86400 * 7)

def add_referral_tok_bonus(uid: str) -> None:
    cache_set(f"referral_bonus:{uid}", None, 1)

def get_usage_summary(uid: str, tier: str, signup_date: Optional[str] = None) -> Dict:
    effective = _get_effective_tier(tier, signup_date)
    today = datetime.now(timezone.utc).date().isoformat()
    msg_used = get(f"msg:{uid}:{today}") or 0
    tok_used = get(f"tok:{uid}:{today}") or 0
    msg_limit = DAILY_MESSAGES.get(effective, 15) + _get_daily_referral_bonus(uid) + _get_streak_bonus(uid)
    tok_limit = BASE_TOK.get(effective, 500) + _get_referral_tok_bonus(uid)
    now = datetime.now(timezone.utc)
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    hours = int((midnight - now).total_seconds() / 3600)
    energy = get_twin_energy(uid, tier, signup_date)
    streak_multiplier = get_bond_streak_multiplier(uid)
    return {
        "messages": {"used": msg_used, "limit": msg_limit, "remaining": max(0, msg_limit - msg_used)},
        "tokens":   {"used": tok_used, "limit": tok_limit, "remaining": max(0, tok_limit - tok_used)},
        "bond_ceiling": get_bond_ceiling(tier, signup_date),
        "hours_until_reset": hours,
        "effective_tier": effective,
        "features": get_tier_features(tier),
        "energy": energy,
        "streak_multiplier": streak_multiplier,
    }

print("✅ Unified Limits Manager v4.0 | أدوات + طاقة + Streak | جاهز")
