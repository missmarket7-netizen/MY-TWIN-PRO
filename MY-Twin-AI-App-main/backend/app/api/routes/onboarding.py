"""Onboarding Route."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["onboarding"])

class OnboardingBody(BaseModel):
    answers: Dict[str, str] = Field(...)
    lang: str = Field("ar")
    userName: str = Field(..., min_length=1)
    twinName: str = Field(..., min_length=1)
    twinGender: str = Field("female")
    freeInfo: str = Field("")

@router.post("/onboarding")
async def complete_onboarding(body: OnboardingBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        db.table("profiles").update({
            "full_name": body.userName,
            "twin_name": body.twinName,
            "twin_gender": body.twinGender,
            "onboarded": True,
            "personality_analysis": body.answers,
        }).eq("id", user_id).execute()
        memory_content = f"تحليل شخصية {body.userName}: {body.freeInfo}" if body.freeInfo else f"تحليل شخصية {body.userName}"
        db.table("memories").insert({
            "user_id": user_id,
            "content": memory_content,
            "importance": 0.9,
            "emotion": "neutral",
            "memory_type": "core",
        }).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))
