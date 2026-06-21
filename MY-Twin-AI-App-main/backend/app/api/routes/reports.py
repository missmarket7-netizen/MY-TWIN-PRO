"""
Reports API - تقارير MyTwin الأسبوعية
========================================
يجمع تقارير الدراسة والعواطف والاستنتاجات.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/weekly")
async def get_weekly_report(user_id: str = Query(...)) -> Dict[str, Any]:
    """تقرير أسبوعي شامل (دراسي + عاطفي + اجتماعي)"""
    try:
        from app.memory.reflection.weekly_report import generate_weekly_report
        report = await generate_weekly_report(user_id)
        
        try:
            from app.infrastructure.database.supabase_client import get_db
            db = get_db()
            res = db.table("user_knowledge_state").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(5).execute()
            report["study_progress"] = res.data or []
        except:
            report["study_progress"] = []
            
        return {"status": "success", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

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
