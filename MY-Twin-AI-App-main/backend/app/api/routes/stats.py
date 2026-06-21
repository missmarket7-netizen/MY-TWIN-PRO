"""
Stats Routes v3.0 – لوحة إحصائيات المستخدم (متكاملة مع TCMA)
================================================================
- إحصائيات الباقة والاستخدام اليومي
- إحصائيات TCMA (الذاكرة، المشاعر، الاستنتاجات)
- إحصائيات الميزات (الدراسة، الأعمال، البرمجة)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime, timezone, timedelta
from app.api.dependencies.auth import get_current_user_id, get_user_tier
from app.infrastructure.database.supabase_client import get_db
from app.domain.services.limits_service import get_usage_summary

logger = logging.getLogger("stats_routes")
router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/dashboard")
async def get_user_dashboard(
    user_id: str = Depends(get_current_user_id),
    tier: str = Depends(get_user_tier),
):
    """لوحة معلومات المستخدم الكاملة"""
    db = get_db()
    today = date.today().isoformat()
    
    stats = {
        "subscription": {"tier": tier},
        "usage": {},
        "tcma": {},
        "features": {},
    }

    # 1. الباقة والاستخدام
    try:
        profile = db.table("profiles").select("*").eq("id", user_id).single().execute()
        if profile.data:
            p = profile.data
            stats["subscription"] = {
                "tier": p.get("tier", "free"),
                "twin_energy": p.get("twin_energy", 100),
                "twin_name": p.get("twin_name", "توأمك"),
            }
    except: pass

    try:
        stats["usage"] = get_usage_summary(user_id, tier)
    except: pass

    # 2. إحصائيات TCMA (الذاكرة)
    try:
        # عدد الذكريات
        from app.infrastructure.database.memory_repo import count_memories
        stats["tcma"]["total_memories"] = await count_memories(user_id)
    except: pass

    try:
        # المشاعر المسيطرة
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        patterns = await get_emotional_patterns(user_id, days=7)
        stats["tcma"]["dominant_emotion"] = patterns.get("dominant_emotion", "neutral")
        stats["tcma"]["emotion_patterns"] = patterns.get("patterns", [])
    except: pass

    try:
        # عدد الاستنتاجات
        from app.memory.reflection.reflection_engine import get_user_insights
        insights = await get_user_insights(user_id, min_confidence=0.5)
        stats["tcma"]["total_insights"] = len(insights.get("insights", []))
    except: pass

    try:
        # شبكة العلاقات
        from app.memory.relationship.person_node import get_person_network
        network = await get_person_network(user_id, min_importance=20)
        stats["tcma"]["people_network_size"] = len(network)
    except: pass

    # 3. إحصائيات الميزات
    try:
        # الدراسة
        knowledge = db.table("user_knowledge_state").select("concept_name,mastery_level").eq("user_id", user_id).order("updated_at", desc=True).limit(5).execute()
        stats["features"]["study"] = {"concepts_learned": len(knowledge.data or []), "top_concepts": [k["concept_name"] for k in (knowledge.data or [])[:3]]}
    except: pass

    try:
        # الأعمال
        projects = db.table("business_projects").select("name,stage").eq("user_id", user_id).execute()
        stats["features"]["business"] = {"active_projects": len(projects.data or [])}
    except: pass

    try:
        # الأهداف
        goals = db.table("goals").select("status").eq("user_id", user_id).execute()
        if goals.data:
            stats["features"]["goals"] = {
                "active": sum(1 for g in goals.data if g.get("status") == "active"),
                "completed": sum(1 for g in goals.data if g.get("status") == "completed"),
            }
    except: pass

    try:
        # المهام
        tasks = db.table("tasks").select("status").eq("user_id", user_id).execute()
        if tasks.data:
            stats["features"]["tasks"] = {
                "pending": sum(1 for t in tasks.data if t.get("status") == "pending"),
                "completed": sum(1 for t in tasks.data if t.get("status") == "completed"),
            }
    except: pass

    return stats

@router.get("/daily-usage")
async def get_daily_usage(
    user_id: str = Depends(get_current_user_id),
    tier: str = Depends(get_user_tier),
):
    """استخدام اليوم الحالي"""
    from app.domain.services.limits_service import get_usage_summary
    return get_usage_summary(user_id, tier)

logger.info("✅ Stats Routes v3.0 initialized")
