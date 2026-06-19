"""
MyTwin – Cache Service v5.0
=============================
- طبقة تخزين مؤقت موحدة (محلي + Redis)
- Response Cache للردود المتكررة
- سياق المستخدم والحالة العاطفية
- إحصائيات وتقارير الأداء
- تنظيف تلقائي للمفاتيح منتهية الصلاحية
"""
import hashlib
import time
import json
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

# ========== الذاكرة المؤقتة المحلية ==========
_cache: Dict[str, Dict[str, Any]] = {}
_cache_stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "last_cleanup": time.time()}

# ========== Redis (اختياري) ==========
_redis_client = None
_redis_enabled = False

try:
    import redis
    from app.core.config import config
    redis_url = config.REDIS_URL
    if redis_url:
        _redis_client = redis.Redis.from_url(
            redis_url, 
            decode_responses=True, 
            socket_connect_timeout=2, 
            socket_timeout=2
        )
        _redis_client.ping()
        _redis_enabled = True
        logger.info("✅ Redis متصل")
except Exception as e:
    logger.info(f"ℹ️ Redis غير متصل، استخدام الذاكرة المحلية: {e}")


def get(key: str) -> Optional[Any]:
    """جلب قيمة من التخزين المؤقت"""
    global _cache_stats
    
    # Redis أولاً
    if _redis_enabled and _redis_client:
        try:
            value = _redis_client.get(key)
            if value is not None:
                _cache_stats["hits"] += 1
                return json.loads(value)
        except Exception:
            pass
    
    # الذاكرة المحلية
    entry = _cache.get(key)
    if entry and entry["expires"] > time.time():
        _cache_stats["hits"] += 1
        return entry["value"]
    
    if entry:
        del _cache[key]
        _cache_stats["deletes"] += 1
    
    _cache_stats["misses"] += 1
    return None


def set(key: str, value: Any, ttl: int = 300) -> None:
    """تخزين قيمة مع مدة صلاحية"""
    global _cache_stats
    
    # Redis أولاً
    if _redis_enabled and _redis_client:
        try:
            _redis_client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        except Exception:
            pass
    
    # الذاكرة المحلية دائماً (احتياطي)
    _cache[key] = {
        "value": value, 
        "expires": time.time() + ttl, 
    }
    _cache_stats["sets"] += 1
    
    # تنظيف تلقائي كل 10 دقائق
    if time.time() - _cache_stats["last_cleanup"] > 600:
        _cleanup_expired()


def delete(key: str) -> bool:
    """حذف مفتاح من التخزين المؤقت"""
    global _cache_stats
    
    if _redis_enabled and _redis_client:
        try:
            _redis_client.delete(key)
        except Exception:
            pass
    
    if key in _cache:
        del _cache[key]
        _cache_stats["deletes"] += 1
        return True
    return False


def _cleanup_expired() -> int:
    """تنظيف المفاتيح منتهية الصلاحية"""
    global _cache_stats
    now = time.time()
    expired = [k for k, v in _cache.items() if v["expires"] <= now]
    for key in expired:
        del _cache[key]
    _cache_stats["last_cleanup"] = now
    if expired:
        logger.info(f"🧹 تنظيف {len(expired)} مفتاح منتهي")
    return len(expired)


def get_stats() -> Dict:
    """إحصائيات التخزين المؤقت"""
    total = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total * 100) if total > 0 else 0
    return {
        "total_entries": len(_cache),
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "hit_rate": round(hit_rate, 2),
        "redis_enabled": _redis_enabled,
    }


# ========== خدمات متخصصة ==========

def _make_response_key(message: str, twin_name: str, lang: str) -> str:
    """توليد مفتاح للردود المتكررة"""
    raw = f"{message.strip().lower()}|{twin_name}|{lang}"
    return f"resp:{hashlib.md5(raw.encode()).hexdigest()}"


def get_cached_response(message: str, twin_name: str, lang: str) -> Optional[str]:
    """جلب رد مخزن مؤقتاً"""
    key = _make_response_key(message, twin_name, lang)
    return get(key)


def set_cached_response(message: str, twin_name: str, lang: str, reply: str, ttl: int = 300) -> None:
    """تخزين رد مؤقتاً"""
    key = _make_response_key(message, twin_name, lang)
    set(key, reply, ttl)


def cache_user_context(user_id: str, context: dict, ttl: int = 600) -> None:
    """تخزين سياق المستخدم"""
    set(f"context:{user_id}", context, ttl)


def get_user_context(user_id: str) -> Optional[dict]:
    """جلب سياق المستخدم"""
    return get(f"context:{user_id}")


def cache_emotional_state(user_id: str, emotional_state: dict) -> None:
    """تخزين الحالة العاطفية"""
    set(f"emotion:{user_id}", emotional_state, ttl=120)


def get_emotional_state(user_id: str) -> Optional[dict]:
    """جلب الحالة العاطفية"""
    return get(f"emotion:{user_id}")


def cache_ai_response(query: str, response: str, ttl: int = 300) -> None:
    """تخزين رد الذكاء الاصطناعي"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    set(f"ai_response:{query_hash}", response, ttl)


def get_ai_response(query: str) -> Optional[str]:
    """جلب رد الذكاء الاصطناعي المخزن"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return get(f"ai_response:{query_hash}")


print(f"✅ Cache Service v5.0 | Redis: {'متصل' if _redis_enabled else 'محلي'}")
