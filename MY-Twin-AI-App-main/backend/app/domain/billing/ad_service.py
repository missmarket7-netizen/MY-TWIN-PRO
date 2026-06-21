"""
Ad Service v3.0 – إعلانات ومكافآت وطاقة (متكامل مع TCMA)
=============================================================
- إعلانات يومية مع مكافآت (رسائل إضافية)
- تجديد طاقة التوأم بنسبة 20% عند المشاهدة
- تكامل مع TCMA (تسجيل المشاهدات كذكريات)
- تخزين دائم في Supabase
- دعم جميع الباقات (مجاني + مميز)
"""
import logging
from typing import Dict, Any
from datetime import date, datetime, timezone

logger = logging.getLogger("ad_service")

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.infrastructure.cache.cache_service import get, set as cache_set
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# إعدادات الإعلانات
MAX_DAILY_ADS_FREE = 3       # الباقة المجانية: 3 إعلانات يومياً
MAX_DAILY_ADS_PLUS = 1       # الباقة المميزة: إعلان واحد فقط
MAX_DAILY_ADS_PREMIUM = 0    # البريميوم: بدون إعلانات
REWARD_MESSAGES = 3           # رسائل إضافية لكل إعلان
ENERGY_BOOST_PERCENT = 0.20   # تجديد طاقة 20%

# ============================================================
# واجهة الإعلانات الرئيسية
# ============================================================
async def get_ad_status(user_id: str) -> Dict[str, Any]:
    """حالة الإعلانات اليومية للمستخدم"""
    today = date.today().isoformat()
    tier = await _get_user_tier(user_id)
    max_ads = _get_max_ads(tier)

    # جلب عدد المشاهدات من الكاش أو Supabase
    watched = await _get_watched_count(user_id, today)

    return {
        "watched_today": watched,
        "remaining_today": max(0, max_ads - watched),
        "max_daily_ads": max_ads,
        "reward_per_ad": REWARD_MESSAGES,
        "energy_boost_percent": int(ENERGY_BOOST_PERCENT * 100),
        "can_watch": watched < max_ads,
        "tier": tier,
    }

async def claim_ad_reward(user_id: str) -> Dict[str, Any]:
    """
    المطالبة بمكافأة مشاهدة الإعلان.
    يمنح: رسائل إضافية + تجديد طاقة 20%
    """
    today = date.today().isoformat()
    tier = await _get_user_tier(user_id)
    max_ads = _get_max_ads(tier)
    watched = await _get_watched_count(user_id, today)

    if watched >= max_ads:
        return {"success": False, "message": "لقد استنفدت حد الإعلانات اليومي"}

    # 1. تسجيل المشاهدة
    new_watched = watched + 1
    await _set_watched_count(user_id, today, new_watched)

    # 2. منح رسائل إضافية
    await _add_bonus_messages(user_id, REWARD_MESSAGES)

    # 3. تجديد الطاقة
    energy_before = await _get_energy(user_id)
    energy_after = await _renew_energy(user_id, ENERGY_BOOST_PERCENT)

    # 4. تسجيل في TCMA
    await _log_to_memory(user_id)

    logger.info(f"✅ إعلان {new_watched}/{max_ads} | طاقة: {energy_before}→{energy_after} | المستخدم: {user_id}")

    return {
        "success": True,
        "reward_messages": REWARD_MESSAGES,
        "remaining_ads": max_ads - new_watched,
        "energy_before": energy_before,
        "energy_after": energy_after,
        "energy_boost": f"+{int(ENERGY_BOOST_PERCENT * 100)}%",
    }

# ============================================================
# دوال مساعدة داخلية
# ============================================================
def _get_max_ads(tier: str) -> int:
    """الحد الأقصى للإعلانات حسب الباقة"""
    limits = {
        "free": MAX_DAILY_ADS_FREE,
        "plus": MAX_DAILY_ADS_PLUS,
        "premium": MAX_DAILY_ADS_PREMIUM,
        "pro": MAX_DAILY_ADS_PREMIUM,
        "yearly": MAX_DAILY_ADS_PREMIUM,
    }
    return limits.get(tier, MAX_DAILY_ADS_FREE)

async def _get_user_tier(user_id: str) -> str:
    """جلب باقة المستخدم"""
    if DB_AVAILABLE:
        try:
            db = get_db()
            result = db.table("profiles").select("tier").eq("id", user_id).single().execute()
            if result.data:
                return result.data.get("tier", "free")
        except: pass
    return "free"

async def _get_watched_count(user_id: str, today: str) -> int:
    """جلب عدد الإعلانات المشاهدة اليوم"""
    if CACHE_AVAILABLE:
        cached = get(f"ads:{user_id}:{today}")
        if cached is not None:
            return cached
    if DB_AVAILABLE:
        try:
            db = get_db()
            result = db.table("ad_views").select("count").eq("user_id", user_id).eq("view_date", today).execute()
            if result.data and len(result.data) > 0:
                return result.data[0].get("count", 0)
        except: pass
    return 0

async def _set_watched_count(user_id: str, today: str, count: int) -> None:
    """تحديث عدد الإعلانات المشاهدة"""
    if CACHE_AVAILABLE:
        cache_set(f"ads:{user_id}:{today}", count, 86400)
    if DB_AVAILABLE:
        try:
            db = get_db()
            # Upsert: تحديث أو إدراج
            existing = db.table("ad_views").select("id").eq("user_id", user_id).eq("view_date", today).execute()
            if existing.data:
                db.table("ad_views").update({"count": count, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", existing.data[0]["id"]).execute()
            else:
                db.table("ad_views").insert({
                    "user_id": user_id,
                    "view_date": today,
                    "count": count,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }).execute()
        except: pass

async def _get_energy(user_id: str) -> int:
    """جلب طاقة التوأم الحالية"""
    if DB_AVAILABLE:
        try:
            db = get_db()
            result = db.table("profiles").select("twin_energy").eq("id", user_id).single().execute()
            if result.data:
                return result.data.get("twin_energy", 100)
        except: pass
    return 100

async def _renew_energy(user_id: str, boost_percent: float) -> int:
    """تجديد طاقة التوأم"""
    current = await _get_energy(user_id)
    new_energy = min(current + int(100 * boost_percent), 100)
    if DB_AVAILABLE:
        try:
            db = get_db()
            db.table("profiles").update({"twin_energy": new_energy}).eq("id", user_id).execute()
        except: pass
    return new_energy

async def _add_bonus_messages(user_id: str, bonus: int) -> None:
    """إضافة رسائل إضافية للمستخدم"""
    if DB_AVAILABLE:
        try:
            db = get_db()
            result = db.table("profiles").select("daily_messages_used").eq("id", user_id).single().execute()
            if result.data:
                current = result.data.get("daily_messages_used", 0)
                new_val = max(0, current - bonus)  # تقليل المستخدم لإتاحة المزيد
                db.table("profiles").update({"daily_messages_used": new_val}).eq("id", user_id).execute()
        except: pass

async def _log_to_memory(user_id: str) -> None:
    """تسجيل مشاهدة الإعلان في TCMA"""
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        await store_emotional_memory(
            user_id=user_id,
            expressed_text="شاهد إعلاناً لتجديد الطاقة",
            detected_emotion={"primary": "neutral", "intensity": 0.3, "valence": 0.1},
            trigger="ad_watched",
            cultural_context="reward_ad"
        )
    except: pass

logger.info("✅ Ad Service v3.0 initialized (TCMA + Energy + DB)")
