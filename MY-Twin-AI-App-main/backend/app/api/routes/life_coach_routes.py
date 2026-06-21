from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
router = APIRouter(prefix="/api/life-coach", tags=["life-coach"])

class SessionRequest(BaseModel):
    user_id: str; topic: str; lang: str = "ar"

class NutritionRequest(BaseModel):
    user_id: str; goal: str; restrictions: str = ""; lang: str = "ar"

class FitnessRequest(BaseModel):
    user_id: str; goal: str; level: str = "beginner"; equipment: str = "none"; lang: str = "ar"

@router.post("/session")
async def session(req: SessionRequest):
    try:
        from app.features.life_coach.life_coach_orchestrator import life_coach
        return await life_coach.start_session(req.user_id, req.topic, req.lang)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/nutrition")
async def nutrition(req: NutritionRequest):
    try:
        from app.features.life_coach.life_coach_orchestrator import life_coach
        return await life_coach.get_nutrition_plan(req.user_id, req.goal, req.restrictions, req.lang)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/fitness")
async def fitness(req: FitnessRequest):
    try:
        from app.features.life_coach.life_coach_orchestrator import life_coach
        return await life_coach.get_fitness_plan(req.user_id, req.goal, req.level, req.equipment, req.lang)
    except Exception as e: raise HTTPException(500, str(e))
