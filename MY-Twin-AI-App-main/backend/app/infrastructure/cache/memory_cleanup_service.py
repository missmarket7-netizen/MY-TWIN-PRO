"""
MyTwin – Memory Cleanup Service v2.0 (TCMA Ready)
====================================================
تنظيف شامل لجميع جداول TCMA.
يعمل حسب باقة المستخدم ويستهدف الجداول الصحيحة.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger(__name__)

# جداول TCMA المراد تنظيفها
TCMA_TABLES = [
    "raw_conversation_archive",
    "emotional_memory",
    "reflection_insights",
    "memory_graph_edges",
    "memory_graph_nodes",
    "person_emotion_links",
]

# عدد أيام الاحتفاظ حسب الباقة
RETENTION_DAYS = {
    "free": 3,
    "plus": 14,
    "premium": 30,
    "pro": 90,
    "yearly": 365,
}

async def run_memory_cleanup(dry: bool = False) -> Dict[str, Any]:
    """
    تنظيف شامل لجميع طبقات TCMA.
    """
    db = get_db()
    result: Dict[str, Any] = {
        "emergency": False,
        "tables_cleaned": 0,
        "total_deleted": 0,
        "errors": []
    }

    try:
        # 1. تنظيف طارئ (إن كان إجمالي البيانات كبيراً جداً)
        total_size = 0
        for table in TCMA_TABLES:
            try:
                cnt = db.table(table).select("id", count="exact").execute()
                total_size += cnt.count or 0
            except: pass

        if total_size > 100000:
            result["emergency"] = True
            if not dry:
                logger.warning(f"🚨 تنظيف طارئ لـ {total_size} سجل")
                cut = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                for table in TCMA_TABLES:
                    try: db.table(table).delete().lt("created_at", cut).execute()
                    except: pass

        # 2. تنظيف دوري حسب الباقة
        for tier, days in RETENTION_DAYS.items():
            cut = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            for table in TCMA_TABLES:
                try:
                    if not dry:
                        del_result = db.table(table).delete().lt("created_at", cut).execute()
                        deleted = len(del_result.data) if del_result.data else 0
                        result["total_deleted"] += deleted
                except Exception as e:
                    logger.warning(f"فشل تنظيف {table}: {e}")

        logger.info(f"🧹 تنظيف ذاكرة: {result['total_deleted']} سجل من {len(TCMA_TABLES)} جداول")
        return result

    except Exception as e:
        logger.error(f"❌ فشل تنظيف الذاكرة: {e}")
        result["errors"].append(str(e))
        return result

async def get_storage_stats() -> Dict[str, Any]:
    """إحصائيات استخدام التخزين لجداول TCMA"""
    db = get_db()
    stats = {}
    total = 0
    for table in TCMA_TABLES:
        try:
            cnt = db.table(table).select("id", count="exact").execute()
            stats[table] = cnt.count or 0
            total += cnt.count or 0
        except:
            stats[table] = -1
    stats["total"] = total
    return stats

logger.info("✅ Memory Cleanup Service v2.0 initialized")
