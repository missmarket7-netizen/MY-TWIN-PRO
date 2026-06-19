"""Stats Route."""
from fastapi import APIRouter, Depends
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db
from datetime import date

router = APIRouter(prefix="/api", tags=["stats"])

@router.get("/stats")
async def get_stats(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("profiles").select("tier,daily_messages_used").eq("id", user_id).single().execute()
        if r.data:
            return {
                "daily_requests": r.data.get("daily_messages_used", 0),
                "limits": {"messages": {"remaining": 10}}
            }
        return {"daily_requests": 0}
    except:
        return {"daily_requests": 0}
