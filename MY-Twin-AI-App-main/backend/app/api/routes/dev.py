"""
Development routes – only for testing.
Creates a test user and returns a valid JWT token.
"""
import os, logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("dev_routes")
router = APIRouter(prefix="/api/dev", tags=["dev"])

DEV_SECRET = os.getenv("DEV_SECRET", "devsecret123")

class DevTokenRequest(BaseModel):
    secret: str = "devsecret123"
    email: str = "sir.market7@gmail.com"
    password: str = "M#m2606.1307"

@router.post("/token")
async def get_dev_token(body: DevTokenRequest):
    """Create or login a test user and return a valid JWT."""
    if body.secret != DEV_SECRET:
        raise HTTPException(403, "Wrong dev secret")
    
    db = get_db()
    try:
        # Try to sign in first
        result = db.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        if result.user and result.session:
            return {"token": result.session.access_token, "user_id": result.user.id, "created": False}
    except:
        pass
    
    # Sign up if not exists
    try:
        result = db.auth.sign_up({
            "email": body.email,
            "password": body.password,
        })
        if result.user and result.session:
            # Create profile
            db.table("profiles").insert({
                "id": result.user.id,
                "email": body.email,
                "full_name": "Test User",
                "twin_name": "توأمي",
                "lang": "ar",
                "tier": "free",
                "onboarded": True,
            }).execute()
            return {"token": result.session.access_token, "user_id": result.user.id, "created": True}
    except Exception as e:
        raise HTTPException(500, f"Failed: {e}")
    
    raise HTTPException(500, "Could not create or login user")
