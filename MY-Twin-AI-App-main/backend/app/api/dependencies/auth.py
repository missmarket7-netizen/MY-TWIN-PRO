"""Auth dependency – verifies JWT via Supabase."""
from fastapi import Header, HTTPException, Depends
from app.infrastructure.database.supabase_client import get_db

async def get_current_user_id(authorization: str = Header(..., alias="Authorization")) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")
    
    db = get_db()
    try:
        user_resp = db.auth.get_user(token)
        if not user_resp.user or not user_resp.user.id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_resp.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
