"""
Reports API v2.0 – تقارير MyTwin المتكاملة
=============================================
- تقرير أسبوعي شامل (عاطفي + دراسي + اجتماعي + أعمال)
- تقرير يومي سريع
- تقرير شهري تحليلي
- تكامل كامل مع TCMA
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

logger = logging.getLogger("reports_routes")
router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/weekly")
async def get_weekly_report(user_id: str = Query(...)) -> Dict[str, Any]:
    """تقرير أسبوعي شامل (عاطفي + دراسي + اجتماعي + استنتاجات)"""
    try:
        report = {"status": "success", "data": {}}

        # 1. التقرير العاطفي
        try:
            from app.memory.emotional.emotional_memory import get_emotional_patterns
            emotional = await get_emotional_patterns(user_id, days=7)
            report["data"]["emotional"] = emotional
        except Exception as e:
            logger.warning(f"Emotional report failed: {e}")
            report["data"]["emotional"] = {"dominant_emotion": "neutral"}

        # 2. التقرير الدراسي
        try:
            from app.infrastructure.database.supabase_client import get_db
            db = get_db()
            knowledge = db.table("user_knowledge_state").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(10).execute()
            report["data"]["study"] = {
                "total_concepts": len(knowledge.data or []),
                "mastered": sum(1 for k in (knowledge.data or []) if k.get("mastery_level", 0) > 0.7),
                "concepts": knowledge.data or [],
            }
        except Exception as e:
            logger.warning(f"Study report failed: {e}")
            report["data"]["study"] = {}

        # 3. التقرير الاجتماعي
        try:
            from app.memory.relationship.person_node import get_person_network
            network = await get_person_network(user_id, min_importance=20)
            report["data"]["social"] = {
                "network_size": len(network),
                "important_people": [p["name"] for p in network[:5]],
            }
        except Exception as e:
            logger.warning(f"Social report failed: {e}")
            report["data"]["social"] = {}

        # 4. الاستنتاجات المتراكمة
        try:
            from app.memory.reflection.reflection_engine import get_user_insights
            insights = await get_user_insights(user_id, min_confidence=0.5)
            report["data"]["insights"] = insights
        except Exception as e:
            logger.warning(f"Insights report failed: {e}")
            report["data"]["insights"] = {}

        # 5. إحصائيات الأهداف
        try:
            goals = db.table("goals").select("status").eq("user_id", user_id).execute()
            if goals.data:
                report["data"]["goals"] = {
                    "active": sum(1 for g in goals.data if g.get("status") == "active"),
                    "completed_this_week": sum(1 for g in goals.data if g.get("status") == "completed"),
                }
        except: pass

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/daily")
async def get_daily_report(user_id: str = Query(...)) -> Dict[str, Any]:
    """تقرير يومي سريع"""
    try:
        from app.core.unified_recommendation_engine import engine
        recs = await engine.get_daily_recommendation(user_id)

        from app.memory.emotional.emotional_memory import get_emotional_patterns
        emotional = await get_emotional_patterns(user_id, days=1)

        return {
            "status": "success",
            "date": __import__('datetime').datetime.now().__str__("%Y-%m-%d"),
            "mood": emotional.get("dominant_emotion", "neutral"),
            "recommendations": recs.get("recommendations", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/study-summary")
async def get_study_summary(user_id: str = Query(...)) -> Dict[str, Any]:
    """ملخص الدراسة الحالي للمستخدم"""
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        res = db.table("user_knowledge_state").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(10).execute()
        concepts = []
        for row in (res.data or []):
            concepts.append({
                "concept": row.get("concept_name"),
                "mastery": row.get("mastery_level"),
                "next_review": row.get("next_review_date"),
                "ease": row.get("ease_factor")
            })
        return {"status": "success", "user_id": user_id, "concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly")
async def get_monthly_report(user_id: str = Query(...)) -> Dict[str, Any]:
    """تقرير شهري تحليلي"""
    try:
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        from app.memory.reflection.reflection_engine import get_user_insights

        emotional = await get_emotional_patterns(user_id, days=30)
        insights = await get_user_insights(user_id, min_confidence=0.6)

        return {
            "status": "success",
            "monthly_emotion": emotional.get("dominant_emotion", "neutral"),
            "emotion_distribution": emotional.get("emotion_distribution", {}),
            "total_insights": len(insights.get("insights", [])),
            "patterns": emotional.get("patterns", []),
            "recommendation": emotional.get("recommendation", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

logger.info("✅ Reports API v2.0 initialized")
