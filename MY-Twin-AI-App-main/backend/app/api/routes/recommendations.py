"""
Recommendations API v2.0 – توصيات موحدة من كل المصادر
=========================================================
- توصيات يومية (من جميع طبقات TCMA والميزات)
- توصيات حسب الفئة (دراسة، أعمال، صحة، علاقات)
- توصيات أسبوعية
- تكامل مع Cross-Feature Analyzer
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("/daily")
async def daily(user_id: str = Query(...)) -> Dict[str, Any]:
    """توصيات يومية مخصصة من جميع المصادر"""
    try:
        from app.core.unified_recommendation_engine import engine
        return await engine.get_daily_recommendation(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category")
async def by_category(
    user_id: str = Query(...),
    category: str = Query("study", regex="^(study|business|code|life_coach|social|emotional)$"),
) -> Dict[str, Any]:
    """توصيات حسب الفئة"""
    try:
        from app.core.unified_recommendation_engine import engine
        all_recs = await engine.get_daily_recommendation(user_id)
        
        # تصفية حسب الفئة
        filtered = [
            r for r in all_recs.get("recommendations", [])
            if r.get("action", "").startswith(category) or category in r.get("type", "")
        ]
        
        return {
            "user_id": user_id,
            "category": category,
            "recommendations": filtered,
            "total": len(filtered),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly")
async def weekly(user_id: str = Query(...)) -> Dict[str, Any]:
    """توصيات أسبوعية مع تحليل الأنماط"""
    try:
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        from app.core.unified_recommendation_engine import engine

        patterns = await get_emotional_patterns(user_id, days=7)
        daily_recs = await engine.get_daily_recommendation(user_id)

        return {
            "user_id": user_id,
            "emotional_week": {
                "dominant": patterns.get("dominant_emotion", "neutral"),
                "patterns": patterns.get("patterns", []),
            },
            "recommendations": daily_recs.get("recommendations", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cross-feature")
async def cross_feature_insights(user_id: str = Query(...)) -> Dict[str, Any]:
    """رؤى من تحليل العلاقات بين الميزات (Cross-Feature)"""
    try:
        from app.core.cross_feature_analyzer import analyzer
        return await analyzer.analyze(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

logger = __import__("logging").getLogger(__name__)
logger.info("✅ Recommendations API v2.0 initialized")
