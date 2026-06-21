"""
Database Infrastructure – واجهات قاعدة البيانات
==================================================
- supabase_client: عميل Supabase الموحد
- memory_repo: واجهة الذاكرة الموحدة (TCMA)
"""
from .supabase_client import get_db, reset_db, check_db_health, get_profile
from .memory_repo import (
    store_memory,
    search_memories,
    get_recent_memories,
    count_memories,
    delete_old_memories,
)

__all__ = [
    "get_db", "reset_db", "check_db_health", "get_profile",
    "store_memory", "search_memories", "get_recent_memories",
    "count_memories", "delete_old_memories",
]
