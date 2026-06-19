"""Auth Dependency – extracts user_id from JWT."""
from fastapi import Header, HTTPException
from app.core.security import decode_access_token, extract_user_id

async def get_current_user_id(
    authorization: str = Header(..., alias="Authorization"),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="متغير غير صالح أو مفقود 'Authorization'")
    
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="توكن فارغ")
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="توكن غير صالح أو منتهي الصلاحية")
    
    user_id = extract_user_id(payload)
    if not user_id:
        raise HTTPException(status_code=401, detail="متغير غير صالح أو مفقود 'user_id'")
    
    return user_id
