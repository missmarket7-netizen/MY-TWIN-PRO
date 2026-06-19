"""
MyTwin – Memory Cleanup Service
=================================
تنظيف الذكريات القديمة من Supabase حسب الباقة.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger(__name__)

# عدد أيام الاحتفاظ حسب الباقة
RETENTION_DAYS = {
    "free": 3, "free_trial_14d": 3, "premium_trial": 20,
    "premium": 30, "pro": 90, "yearly": 365,
}


async def run_memory_cleanup(dry: bool = False) -> Dict[str, Any]:
    """
    تنظيف الذكريات القديمة حسب باقة المستخدم.
    تُستدعى دورياً أو عند الحاجة.
    """
    db = get_db()
    result: Dict[str, Any] = {
        "emergency": False, 
        "tiers_cleaned": 0, 
        "total_deleted": 0, 
        "errors": []
    }
    
    try:
        # فحص الطوارئ: أكثر من 40 ألف ذاكرة
        cnt_result = db.table("memories").select("id", count="exact").execute()
        total_count = cnt_result.count or 0
        
        if total_count > 40000:
            result["emergency"] = True
            if not dry:
                cut = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
                del_result = db.table("memories").delete().lt("created_at", cut).execute()
                result["total_deleted"] = len(del_result.data) if del_result.data else 0
                logger.warning(f"🚨 تنظيف طارئ: {result['total_deleted']} ذاكرة")

        # تنظيف حسب الباقة
        for tier, days in RETENTION_DAYS.items():
            cut = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            users_result = db.table("profiles").select("user_id").eq("tier", tier).execute()
            uids = [u["user_id"] for u in (users_result.data or [])]
            
            if not uids:
                continue
                
            if not dry:
                del_result = db.table("memories").delete()\
                    .in_("user_id", uids)\
                    .lt("created_at", cut)\
                    .execute()
                deleted = len(del_result.data) if del_result.data else 0
                result["total_deleted"] += deleted
                result["tiers_cleaned"] += 1
                
        logger.info(f"🧹 تنظيف: {result['total_deleted']} ذاكرة من {result['tiers_cleaned']} باقة")
        return result
        
    except Exception as e:
        logger.error(f"❌ فشل تنظيف الذكريات: {e}")
        result["errors"].append(str(e))
        return result
