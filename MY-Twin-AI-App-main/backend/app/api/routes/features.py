"""
Feature Routes v3.0 – متوافقة مع الأنظمة المستقلة
=====================================================
- تستخدم TierRateLimit للتحقق من الباقة
- تستخدم Provider Router الموحّد
- تحافظ على التوافق مع القديم
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.api.dependencies.auth import get_current_user_id, get_user_tier
from app.api.dependencies.rate_limiter import TierRateLimit
import logging

logger = logging.getLogger("features")
router = APIRouter(prefix="/api/features", tags=["features"])

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
@router.post("/study", dependencies=[Depends(TierRateLimit(feature="study"))])
async def study_mode(body: StudyBody, user_id: str = Depends(get_current_user_id), tier: str = Depends(get_user_tier)):
    prompt = f"اشرح: {body.topic}. المستوى: {body.level}. اللغة: {body.lang}"
    try:
        from app.infrastructure.ai.provider_router import provider_router
        reply, _ = await provider_router.route(prompt, task="study", tier=tier)
        return {"reply": reply}
    except Exception:
        raise HTTPException(503, "AI unavailable")

@router.post("/code", dependencies=[Depends(TierRateLimit(feature="code_lab"))])
async def code_lab(body: CodeBody, user_id: str = Depends(get_current_user_id), tier: str = Depends(get_user_tier)):
    prompt = f"{body.action} كود {body.language}: {body.task}. اللغة: {body.lang}"
    try:
        from app.infrastructure.ai.provider_router import provider_router
        reply, _ = await provider_router.route(prompt, task="coding", tier=tier)
        return {"reply": reply}
    except Exception:
        raise HTTPException(503, "AI unavailable")

@router.post("/business", dependencies=[Depends(TierRateLimit(feature="business"))])
async def business_analysis(body: BusinessBody, user_id: str = Depends(get_current_user_id), tier: str = Depends(get_user_tier)):
    prompt = f"تحليل أعمال ({body.analysis_type}): {body.text}. اللغة: {body.lang}"
    try:
        from app.infrastructure.ai.provider_router import provider_router
        reply, _ = await provider_router.route(prompt, task="business", tier=tier)
        return {"reply": reply}
    except Exception:
        raise HTTPException(503, "AI unavailable")

@router.post("/coach", dependencies=[Depends(TierRateLimit(feature="life_coach"))])
async def life_coach(body: CoachBody, user_id: str = Depends(get_current_user_id), tier: str = Depends(get_user_tier)):
    prompt = f"مدرب حياة ({body.domain}): {body.topic}. اللغة: {body.lang}"
    try:
        from app.infrastructure.ai.provider_router import provider_router
        reply, _ = await provider_router.route(prompt, task="coaching", tier=tier)
        return {"reply": reply}
    except Exception:
        raise HTTPException(503, "AI unavailable")

@router.post("/content", dependencies=[Depends(TierRateLimit(feature="content"))])
async def content_creation(body: ContentBody, user_id: str = Depends(get_current_user_id), tier: str = Depends(get_user_tier)):
    prompt = f"كتابة محتوى لمنصة {body.platform} بنبرة {body.tone}: {body.topic}. اللغة: {body.lang}"
    try:
        from app.infrastructure.ai.provider_router import provider_router
        reply, _ = await provider_router.route(prompt, task="content", tier=tier)
        return {"reply": reply}
    except Exception:
        raise HTTPException(503, "AI unavailable")

@router.post("/dream", dependencies=[Depends(TierRateLimit(feature="dreams"))])
async def analyze_dream(body: DreamBody, user_id: str = Depends(get_current_user_id), tier: str = Depends(get_user_tier)):
    prompt = f"تفسير حلم: {body.dream}. اللغة: {body.lang}"
    try:
        from app.infrastructure.ai.provider_router import provider_router
        reply, _ = await provider_router.route(prompt, task="dream", tier=tier)
        return {"interpretation": reply}
    except Exception:
        raise HTTPException(503, "AI unavailable")

logger.info("✅ Feature Routes v3.0 initialized")
