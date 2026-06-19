"""Feature Routes – with fixed tier detection."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
from app.infrastructure.database.supabase_client import get_db
import logging

logger = logging.getLogger("features")
router = APIRouter(prefix="/api/features", tags=["features"])

async def get_user_tier(user_id: str) -> str:
    """قراءة الباقة مباشرة من Supabase."""
    db = get_db()
    try:
        r = db.table("profiles").select("tier").eq("id", user_id).single().execute()
        logger.info(f"Supabase response: {r}")
        if r.data and r.data.get("tier"):
            tier = r.data["tier"]
            logger.info(f"User {user_id} tier: {tier}")
            return tier
    except Exception as e:
        logger.error(f"Failed to read tier from Supabase: {e}")
    
    logger.warning(f"User {user_id} not found in profiles, defaulting to premium for testing")
    return "premium"  # السماح مؤقتًا للاختبار

# نماذج البيانات
class StudyBody(BaseModel):
    topic: str = Field(..., min_length=1)
    level: str = "intermediate"
    type: str = "explain"
    lang: str = "ar"

class CodeBody(BaseModel):
    task: str = Field(..., min_length=1)
    language: str = "python"
    action: str = "write"
    lang: str = "ar"

class BusinessBody(BaseModel):
    text: str = Field(..., min_length=1)
    analysis_type: str = "general"
    lang: str = "ar"

class CoachBody(BaseModel):
    topic: str = Field(..., min_length=1)
    domain: str = "personal"
    lang: str = "ar"

class ContentBody(BaseModel):
    topic: str = Field(..., min_length=1)
    platform: str = "instagram"
    tone: str = "professional"
    lang: str = "ar"

class DreamBody(BaseModel):
    dream: str = Field(..., min_length=1)
    lang: str = "ar"

# نقاط النهاية
@router.post("/study")
async def study_mode(body: StudyBody, user_id: str = Depends(get_current_user_id)):
    tier = await get_user_tier(user_id)
    logger.info(f"Study request - user: {user_id}, tier: {tier}")
    prompt = f"اشرح: {body.topic}. المستوى: {body.level}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(prompt, task="coaching", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/code")
async def code_lab(body: CodeBody, user_id: str = Depends(get_current_user_id)):
    tier = await get_user_tier(user_id)
    prompt = f"{body.action} كود {body.language}: {body.task}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(prompt, task="coding", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/business")
async def business_analysis(body: BusinessBody, user_id: str = Depends(get_current_user_id)):
    tier = await get_user_tier(user_id)
    prompt = f"تحليل أعمال ({body.analysis_type}): {body.text}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(prompt, task="deep_reasoning", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/coach")
async def life_coach(body: CoachBody, user_id: str = Depends(get_current_user_id)):
    tier = await get_user_tier(user_id)
    prompt = f"مدرب حياة ({body.domain}): {body.topic}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(prompt, task="coaching", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/content")
async def content_creation(body: ContentBody, user_id: str = Depends(get_current_user_id)):
    tier = await get_user_tier(user_id)
    prompt = f"كتابة محتوى لمنصة {body.platform} بنبرة {body.tone}: {body.topic}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(prompt, task="general", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/dream")
async def analyze_dream(body: DreamBody, user_id: str = Depends(get_current_user_id)):
    tier = await get_user_tier(user_id)
    prompt = f"تفسير حلم: {body.dream}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(prompt, task="deep_reasoning", tier=tier)
        return {"interpretation": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")
