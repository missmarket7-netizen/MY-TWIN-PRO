"""Profile & Mood Routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["profile"])

class UpdateProfileBody(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class AddMoodBody(BaseModel):
    mood: str = Field(...)

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("profiles").select("*").eq("id", user_id).single().execute()
        if r.data:
            return r.data
        return {}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put("/profile")
async def update_profile(body: UpdateProfileBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    update_data = {}
    if body.full_name is not None:
        update_data["full_name"] = body.full_name
    if body.phone is not None:
        update_data["phone"] = body.phone
    if update_data:
        try:
            db.table("profiles").update(update_data).eq("id", user_id).execute()
        except Exception as e:
            raise HTTPException(500, str(e))
    return {"status": "ok"}

@router.get("/moods")
async def get_moods(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("emotional_timeline").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/moods")
async def add_mood(body: AddMoodBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        mood_map = {
            "joy": 0.8, "neutral": 0.2, "sadness": -0.5, "anger": -0.5,
            "fear": -0.4, "love": 0.8, "tired": -0.3,
        }
        valence = mood_map.get(body.mood, 0.0)
        db.table("emotional_timeline").insert({
            "user_id": user_id,
            "primary_emotion": body.mood,
            "intensity": 0.7,
            "valence": valence,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))
