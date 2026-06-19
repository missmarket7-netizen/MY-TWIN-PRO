"""Push Token Route."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["push"])

class PushTokenBody(BaseModel):
    token: str = Field(...)
    platform: str = Field("android")

@router.put("/push-token")
async def update_push_token(body: PushTokenBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        db.table("profiles").update({
            "push_token": body.token,
            "device_platform": body.platform,
            "push_token_updated_at": "now()",
        }).eq("id", user_id).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))
