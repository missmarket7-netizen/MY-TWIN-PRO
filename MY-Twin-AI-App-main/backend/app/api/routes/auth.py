"""Auth Routes – Login, Signup via Supabase Auth."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginBody(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class SignupBody(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

@router.post("/login")
async def login(body: LoginBody):
    db = get_db()
    try:
        result = db.auth.sign_in_with_password({"email": body.email, "password": body.password})
        if result.user and result.session:
            return {"token": result.session.access_token, "user_id": result.user.id}
        raise HTTPException(401, "Invalid credentials")
    except Exception as e:
        raise HTTPException(401, str(e))

@router.post("/signup")
async def signup(body: SignupBody):
    db = get_db()
    try:
        result = db.auth.sign_up({"email": body.email, "password": body.password})
        if result.user:
            # Create profile on signup
            db.table("profiles").insert({
                "id": result.user.id,
                "email": body.email,
                "created_at": "now()",
            }).execute()
            if result.session:
                return {"token": result.session.access_token, "user_id": result.user.id}
            return {"message": "Check your email to confirm", "user_id": result.user.id}
        raise HTTPException(400, "Signup failed")
    except Exception as e:
        raise HTTPException(400, str(e))
