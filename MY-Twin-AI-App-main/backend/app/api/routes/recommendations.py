from fastapi import APIRouter, Query
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("/daily")
async def daily(user_id: str = Query(...)):
    from app.core.unified_recommendation_engine import engine
    return await engine.get_daily_recommendation(user_id)
