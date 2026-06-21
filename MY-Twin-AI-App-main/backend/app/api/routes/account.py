"""
Account Routes v3.0 – حذف مؤجل، تصدير TCMA، استعادة
=========================================================
- حذف مؤجل (30 يوم سماح) بدلاً من الحذف الفوري
- تصدير جميع طبقات TCMA
- استعادة الحساب قبل الحذف النهائي
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("account_routes")
router = APIRouter(prefix="/api/account", tags=["account"])

# ============================================================
# حذف مؤجل (30 يوم)
# ============================================================
@router.delete("/delete")
async def delete_account(user_id: str = Depends(get_current_user_id)):
    """
    تعطيل الحساب بدلاً من حذفه فوراً.
    يُحذف نهائياً بعد 30 يوماً إذا لم يستعد.
    """
    db = get_db()
    try:
        deletion_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        db.table("profiles").update({
            "deleted_at": deletion_date,
            "status": "pending_deletion"
        }).eq("id", user_id).execute()
        
        return {
            "message": "تم تعطيل الحساب. سيتم حذفه نهائياً بعد 30 يوماً. سجل الدخول قبل انتهاء المدة لاستعادته.",
            "deletion_date": deletion_date,
            "restore_possible": True
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/restore")
async def restore_account(user_id: str = Depends(get_current_user_id)):
    """استعادة الحساب قبل الحذف النهائي"""
    db = get_db()
    try:
        profile = db.table("profiles").select("deleted_at,status").eq("id", user_id).single().execute()
        if not profile.data or profile.data.get("status") != "pending_deletion":
            raise HTTPException(400, "الحساب ليس في حالة حذف")
        
        db.table("profiles").update({
            "deleted_at": None,
            "status": "active"
        }).eq("id", user_id).execute()
        
        return {"message": "تم استعادة الحساب بنجاح. أهلاً بك من جديد!"}
    except Exception as e:
        raise HTTPException(500, str(e))

# ============================================================
# تصدير بيانات TCMA
# ============================================================
@router.get("/export")
async def export_all_data(user_id: str = Depends(get_current_user_id)):
    """تصدير جميع بيانات المستخدم من كل طبقات TCMA"""
    db = get_db()
    data = {}
    
    # 1. الملف الشخصي
    try:
        profile = db.table("profiles").select("*").eq("id", user_id).single().execute()
        data["profile"] = profile.data
    except: data["profile"] = None

    # 2. الأرشيف الخام
    try:
        archive = db.table("raw_conversation_archive").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(500).execute()
        data["raw_conversations"] = archive.data or []
    except: data["raw_conversations"] = []

    # 3. الذاكرة العاطفية
    try:
        emotional = db.table("emotional_memory").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(500).execute()
        data["emotional_memory"] = emotional.data or []
    except: data["emotional_memory"] = []

    # 4. الاستنتاجات
    try:
        reflections = db.table("reflection_insights").select("*").eq("user_id", user_id).order("last_observed", desc=True).limit(200).execute()
        data["reflections"] = reflections.data or []
    except: data["reflections"] = []

    # 5. شبكة الأشخاص
    try:
        people = db.table("person_nodes").select("*").eq("user_id", user_id).order("importance_score", desc=True).execute()
        data["people_network"] = people.data or []
    except: data["people_network"] = []

    # 6. هوية التوأم
    try:
        identity = db.table("identity_model").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        data["identity"] = identity.data or []
    except: data["identity"] = []

    # 7. الأهداف
    try:
        goals = db.table("goals").select("*").eq("user_id", user_id).execute()
        data["goals"] = goals.data or []
    except: data["goals"] = []

    # 8. حالة المعرفة
    try:
        knowledge = db.table("user_knowledge_state").select("*").eq("user_id", user_id).execute()
        data["knowledge_state"] = knowledge.data or []
    except: data["knowledge_state"] = []

    # 9. رسم الذاكرة البياني
    try:
        edges = db.table("memory_graph_edges").select("*").eq("user_id", user_id).limit(500).execute()
        data["memory_graph_edges"] = edges.data or []
    except: data["memory_graph_edges"] = []

    return {
        "user_id": user_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_records": sum(len(v) if isinstance(v, list) else 1 for v in data.values()),
        "data": data
    }

# ============================================================
# تنظيف دوري (يُستدعى آلياً)
# ============================================================
async def run_deletion_cleanup():
    """حذف الحسابات التي تجاوزت 30 يوم سماح (تُستدعى يومياً)"""
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        users = db.table("profiles").select("id").eq("status", "pending_deletion").lt("deleted_at", cutoff).execute()
        
        deleted_count = 0
        for user in (users.data or []):
            uid = user["id"]
            # حذف جميع بيانات المستخدم
            tables = [
                "raw_conversation_archive", "emotional_memory", "reflection_insights",
                "person_nodes", "person_emotion_links", "identity_model",
                "goals", "tasks", "user_knowledge_state", "memory_graph_edges",
                "memory_graph_nodes", "ai_metrics", "agent_metrics", "product_impressions",
                "product_clicks", "referral_usage", "ad_views"
            ]
            for table in tables:
                try: db.table(table).delete().eq("user_id", uid).execute()
                except: pass
            try: db.table("profiles").delete().eq("id", uid).execute()
            except: pass
            deleted_count += 1
        
        if deleted_count:
            logger.info(f"🧹 Deleted {deleted_count} accounts (30-day grace period expired)")
        return deleted_count
    except Exception as e:
        logger.error(f"Deletion cleanup failed: {e}")
        return 0

logger.info("✅ Account Routes v3.0 initialized (Graceful Deletion + TCMA Export)")
