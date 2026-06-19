"""Auth dependency – extracts user_id from JWT."""
from fastapi import Header, HTTPException
from app.core.security import decode_access_token, extract_user_id

async def get_current_user_id(authorization: str = Header(..., alias="Authorization")) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = extract_user_id(payload)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user identity")
    
    return user_id
