"""
Relationship API v2.0 – متكاملة مع TCMA
============================================
- حالة العلاقة (ثقة، انفتاح، تعلق)
- شبكة الأشخاص المهمين
- مرحلة الرحلة الحالية
- صحة العلاقة
- تطور العلاقة عبر الزمن
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

router = APIRouter(prefix="/api/relationship", tags=["relationship"])

@router.get("/state")
async def get_relationship_state(user_id: str = Query(...)) -> Dict[str, Any]:
    """حالة العلاقة الكاملة مع التوأم"""
    try:
        from app.memory.relationship.relationship_memory import get_relationship_context_for_response
        context = await get_relationship_context_for_response(user_id, "")
        return {"status": "success", "data": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attachment")
async def get_attachment_style(user_id: str = Query(...)) -> Dict[str, Any]:
    """نمط التعلق (Secure, Anxious, Avoidant, Disorganized)"""
    try:
        from app.memory.relationship.attachment_model import detect_attachment_style
        style = await detect_attachment_style(user_id)
        return {"status": "success", "data": style}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_relationship_health(user_id: str = Query(...)) -> Dict[str, Any]:
    """تحليل صحة العلاقة (من Meta-Reflection)"""
    try:
        from app.features.meta_reflection import meta_engine
        health = await meta_engine.analyze_relationship_health(user_id)
        return {"status": "success", "data": health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/people")
async def get_important_people(user_id: str = Query(...)) -> Dict[str, Any]:
    """شبكة الأشخاص المهمين في حياة المستخدم"""
    try:
        from app.memory.relationship.person_node import get_person_network
        network = await get_person_network(user_id, min_importance=20)
        return {
            "status": "success",
            "total": len(network),
            "people": [
                {
                    "name": p.get("name"),
                    "relationship": p.get("relationship_type"),
                    "importance": p.get("importance_score"),
                    "emotional_associations": p.get("emotional_associations", [])[:3],
                }
                for p in network[:10]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journey")
async def get_journey_phase(user_id: str = Query(...)) -> Dict[str, Any]:
    """المرحلة الحالية في رحلة المستخدم"""
    try:
        from app.twin_state.journey_service import get_current_phase, get_behavior, get_daily_message
        phase = await get_current_phase(user_id)
        behavior = get_behavior(phase)
        daily_msg = get_daily_message(phase)
        return {
            "status": "success",
            "phase": phase,
            "behavior": behavior,
            "daily_message": daily_msg,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evolution")
async def get_relationship_evolution(user_id: str = Query(...)) -> Dict[str, Any]:
    """تطور العلاقة عبر الزمن (آخر 10 لقطات)"""
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        result = db.table("relationship_memory").select("trust,openness,attachment,comfort,created_at").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        
        if not result.data:
            return {"status": "success", "snapshots": [], "trend": "not_enough_data"}
        
        snapshots = result.data
        first = snapshots[-1]
        last = snapshots[0]
        
        trend = "improving" if last["trust"] > first["trust"] else "declining" if last["trust"] < first["trust"] else "stable"
        
        return {
            "status": "success",
            "snapshots": snapshots,
            "trend": trend,
            "trust_change": round(last["trust"] - first["trust"], 1),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

logger.info("✅ Relationship API v2.0 initialized")
