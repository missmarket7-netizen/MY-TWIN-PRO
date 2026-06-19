"""Referral Routes."""
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api/referral", tags=["referral"])

class ActivateBody(BaseModel):
    code: str = Field(..., min_length=6, max_length=10)

@router.post("/generate")
async def generate(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    code = "MT" + hashlib.sha256(user_id.encode()).hexdigest()[:6].upper()
    try:
        db.table("profiles").update({"referral_code": code}).eq("id", user_id).execute()
    except:
        pass
    return {"code": code}

@router.post("/activate")
async def activate(body: ActivateBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    code = body.code.upper().strip()
    try:
        owner = db.table("profiles").select("id").eq("referral_code", code).single().execute()
        if not owner.data:
            raise HTTPException(400, "Invalid code")
        inviter_id = owner.data["id"]
        if inviter_id == user_id:
            raise HTTPException(400, "Cannot use your own code")
        existing = db.table("referral_usage").select("*").eq("user_id", user_id).eq("code", code).single().execute()
        if existing.data:
            raise HTTPException(400, "Already used")
        db.table("referral_usage").insert({
            "user_id": user_id, "code": code, "inviter_id": inviter_id,
            "activated_at": "now()",
        }).execute()
        return {"success": True, "bonus": 500}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/stats")
async def stats(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("referral_usage").select("id").eq("inviter_id", user_id).execute()
        invited_count = len(r.data or [])
        profile = db.table("profiles").select("referral_code").eq("id", user_id).single().execute()
        code = profile.data.get("referral_code", "") if profile.data else ""
        return {
            "code": code,
            "link": f"https://mytwin.app/join?ref={code}" if code else "",
            "invitedCount": invited_count,
            "earnedTokens": invited_count * 500,
        }
    except Exception as e:
        raise HTTPException(500, str(e))
