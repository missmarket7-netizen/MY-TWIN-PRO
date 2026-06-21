""" Business API Routes - مسارات G.R.O.W.T.H-H.I.V.E """
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

try:
    from app.features.business.growth_hive_orchestrator import growth_hive
    HIVE_READY = True
except ImportError:
    HIVE_READY = False

router = APIRouter(prefix="/api/business", tags=["business"])

class IdeaRequest(BaseModel):
    user_id: str
    budget: float
    interests: str = ""
    location: str = ""
    language: str = "ar"

class AnalyzeRequest(BaseModel):
    user_id: str
    idea: str
    industry: str = ""
    language: str = "ar"

@router.post("/generate-ideas")
async def generate_ideas(request: IdeaRequest):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.generate_business_idea(request.user_id, request.budget, request.interests, request.location, request.language)

@router.post("/analyze-market")
async def analyze_market(request: AnalyzeRequest):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.analyze_market_opportunity(request.user_id, request.idea, request.industry, request.language)

@router.post("/feasibility")
async def feasibility(request: IdeaRequest):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.generate_feasibility_study(request.user_id, request.idea, request.budget, request.language)

@router.post("/canvas")
async def business_canvas(request: AnalyzeRequest):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.generate_business_canvas(request.user_id, request.idea, request.language)

@router.post("/marketing-plan")
async def marketing_plan(request: IdeaRequest):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.generate_marketing_plan(request.user_id, request.idea, request.budget, request.language)

@router.post("/sales-roleplay")
async def sales_roleplay(user_id: str = Query(...), scenario: str = Query(...), language: str = "ar"):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.sales_roleplay(user_id, scenario, language)

@router.post("/support")
async def support(user_id: str = Query(...), language: str = "ar"):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.entrepreneurial_support(user_id, language)

@router.get("/report")
async def report(user_id: str = Query(...)):
    if not HIVE_READY: raise HTTPException(status_code=503, detail="خدمة الأعمال غير متوفرة")
    return await growth_hive.venture_report(user_id)
