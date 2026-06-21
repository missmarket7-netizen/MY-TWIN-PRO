"""
Cache Infrastructure – تخزين مؤقت وتنظيف
===========================================
- cache_service: تخزين مؤقت (محلي + Redis)
- memory_cleanup_service: تنظيف جداول TCMA
"""
from .cache_service import (
    get,
    set,
    delete,
    get_stats,
    get_cached_response,
    set_cached_response,
    cache_user_context,
    get_user_context,
    cache_emotional_state,
    get_emotional_state,
    cache_ai_response,
    get_ai_response,
)
from .memory_cleanup_service import (
    run_memory_cleanup,
    get_storage_stats,
)

__all__ = [
    "get", "set", "delete", "get_stats",
    "get_cached_response", "set_cached_response",
    "cache_user_context", "get_user_context",
    "cache_emotional_state", "get_emotional_state",
    "cache_ai_response", "get_ai_response",
    "run_memory_cleanup", "get_storage_stats",
]
