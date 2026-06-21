"""
Memory Repo v2.0 – واجهة موحدة للذاكرة (TCMA)
===============================================
تجميع طبقات الذاكرة المختلفة في واجهة واحدة للاستدعاء السهل.
"""
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger("memory_repo")

async def store_memory(
    user_id: str,
    content: str,
    memory_type: str = "emotional",
    importance: float = 0.5,
) -> Optional[str]:
    """
    تخزين ذاكرة في TCMA (الطبقة المناسبة).
    """
    try:
        if memory_type == "emotional":
            from app.memory.emotional.emotional_memory import store_emotional_memory
            result = await store_emotional_memory(
                user_id=user_id,
                expressed_text=content,
                detected_emotion={"primary": "neutral", "intensity": importance, "valence": 0.0},
                trigger="manual"
            )
            return result.get("id") if result else None
        
        elif memory_type == "reflection":
            from app.memory.reflection.reflection_engine import store_reflection
            return await store_reflection(
                user_id=user_id,
                insight_type="manual",
                insight_text=content,
                confidence=importance
            )
        
        else:
            # تخزين في الأرشيف الخام
            from app.memory.archive.raw_archive import archive_message
            return await archive_message(user_id, content, "user")
    
    except Exception as e:
        logger.error(f"فشل تخزين الذاكرة: {e}")
        return None

async def search_memories(
    user_id: str,
    query_text: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """بحث في الذاكرة باستخدام محرك TCMA الموحد"""
    try:
        from app.memory.retrieval.memory_retriever import retrieve_context
        result = await retrieve_context(user_id, query_text, top_k)
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"فشل البحث في الذاكرة: {e}")
        return []

async def get_recent_memories(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """جلب أحدث الذكريات من الأرشيف الخام"""
    try:
        from app.memory.archive.raw_archive import get_conversation_archive
        return await get_conversation_archive(user_id, limit)
    except Exception as e:
        logger.error(f"فشل جلب الذكريات الحديثة: {e}")
        return []

async def count_memories(user_id: str) -> int:
    """إحصاء إجمالي الذكريات"""
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        count = 0
        tables = ["raw_conversation_archive", "emotional_memory", "reflection_insights"]
        for table in tables:
            try:
                r = db.table(table).select("id", count="exact").eq("user_id", user_id).execute()
                count += r.count or 0
            except: pass
        return count
    except:
        return 0

async def delete_old_memories(user_id: str, keep: int = 100) -> int:
    """حذف الذكريات القديمة (احتفاظ بالأحدث)"""
    try:
        from app.infrastructure.cache.memory_cleanup_service import run_memory_cleanup
        result = await run_memory_cleanup(dry=False)
        return result.get("total_deleted", 0)
    except:
        return 0

logger.info("✅ Memory Repo v2.0 initialized (TCMA Interface)")
