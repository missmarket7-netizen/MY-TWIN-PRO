"""Goals Routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["goals"])

class AddGoalBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

@router.get("/goals")
async def get_goals(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("goals").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/goals")
async def add_goal(body: AddGoalBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("goals").insert({
            "user_id": user_id,
            "title": body.title,
            "status": "active",
            "progress": 0,
        }).execute()
        return r.data[0] if r.data else {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/goals/{goal_id}")
async def delete_goal(goal_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        db.table("goals").delete().eq("id", goal_id).eq("user_id", user_id).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))
