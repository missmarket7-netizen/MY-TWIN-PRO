"""Account Routes – Delete, Export."""
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["account"])

@router.delete("/account")
async def delete_account(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        # Delete user data
        db.table("memories").delete().eq("user_id", user_id).execute()
        db.table("goals").delete().eq("user_id", user_id).execute()
        db.table("emotional_timeline").delete().eq("user_id", user_id).execute()
        db.table("message_feedback").delete().eq("user_id", user_id).execute()
        db.table("referral_usage").delete().eq("user_id", user_id).execute()
        db.table("profiles").delete().eq("id", user_id).execute()
        # Delete auth user
        db.auth.admin.delete_user(user_id)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/me/export")
async def export_data(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        profile = db.table("profiles").select("*").eq("id", user_id).single().execute()
        memories = db.table("memories").select("*").eq("user_id", user_id).execute()
        goals = db.table("goals").select("*").eq("user_id", user_id).execute()
        moods = db.table("emotional_timeline").select("*").eq("user_id", user_id).execute()
        return {
            "profile": profile.data,
            "memories": memories.data,
            "goals": goals.data,
            "moods": moods.data,
        }
    except Exception as e:
        raise HTTPException(500, str(e))
