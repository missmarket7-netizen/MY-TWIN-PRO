"""Memories Routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["memories"])

@router.get("/memories")
async def get_memories(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("memories").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(50).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))
