from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
router = APIRouter(prefix="/api/life-coach", tags=["life-coach"])

class SessionRequest(BaseModel):
    user_id: str
    topic: str
    lang: str = "ar"

class PlanRequest(BaseModel):
    user_id: str
    goals: str
    lang: str = "ar"

@router.post("/session")
async def session(req: SessionRequest):
    try:
        from app.features.life_coach.life_coach_orchestrator import life_coach
        return await life_coach.start_session(req.user_id, req.topic, req.lang)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/plan")
async def plan(req: PlanRequest):
    try:
        from app.features.life_coach.life_coach_orchestrator import life_coach
        return await life_coach.generate_integrated_plan(req.user_id, req.goals, req.lang)
    except Exception as e: raise HTTPException(500, str(e))
