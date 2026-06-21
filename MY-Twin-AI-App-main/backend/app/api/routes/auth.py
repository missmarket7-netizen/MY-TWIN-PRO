"""
Auth Routes v2.0 – متكاملة مع الباقات ونظام الأحداث
=======================================================
- تسجيل الدخول والخروج
- إنشاء حساب مع إعدادات الباقة تلقائياً
- تسجيل الأحداث في Event Bus
- تخزين مؤقت للجلسات
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("auth_routes")
router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginBody(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class SignupBody(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    twin_name: str = "توأمك"
    lang: str = "ar"

class ResetPasswordBody(BaseModel):
    email: str = Field(..., min_length=3)

class UpdatePasswordBody(BaseModel):
    password: str = Field(..., min_length=6)

@router.post("/login")
async def login(body: LoginBody):
    """تسجيل الدخول عبر Supabase Auth"""
    db = get_db()
    try:
        result = db.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        if result.user and result.session:
            # تحديث آخر نشاط
            try:
                db.table("profiles").update({
                    "last_active": datetime.now(timezone.utc).isoformat()
                }).eq("id", result.user.id).execute()
            except: pass

            # تسجيل الحدث
            try:
                from app.events.event_bus import emit
                await emit({
                    "type": "user_logged_in",
                    "user_id": result.user.id,
                    "email": body.email,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except: pass

            return {
                "token": result.session.access_token,
                "refresh_token": result.session.refresh_token,
                "user_id": result.user.id,
                "expires_at": result.session.expires_at,
            }
        raise HTTPException(401, "Invalid credentials")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(401, "Invalid email or password")

@router.post("/signup")
async def signup(body: SignupBody):
    """إنشاء حساب جديد مع الملف الشخصي"""
    db = get_db()
    try:
        result = db.auth.sign_up({
            "email": body.email,
            "password": body.password,
        })
        if result.user:
            # إنشاء الملف الشخصي تلقائياً
            try:
                db.table("profiles").insert({
                    "id": result.user.id,
                    "email": body.email,
                    "full_name": body.email.split('@')[0],
                    "twin_name": body.twin_name,
                    "lang": body.lang,
                    "tier": "free",
                    "twin_energy": 100,
                    "daily_messages_used": 0,
                    "daily_tokens_used": 0,
                    "onboarded": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_active": datetime.now(timezone.utc).isoformat(),
                }).execute()
            except Exception as e:
                logger.warning(f"Profile creation failed: {e}")

            # تسجيل الحدث
            try:
                from app.events.event_bus import emit
                await emit({
                    "type": "user_registered",
                    "user_id": result.user.id,
                    "email": body.email,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except: pass

            if result.session:
                return {
                    "token": result.session.access_token,
                    "refresh_token": result.session.refresh_token,
                    "user_id": result.user.id,
                    "message": "تم إنشاء الحساب بنجاح",
                }
            return {
                "message": "تم إنشاء الحساب. تحقق من بريدك الإلكتروني للتأكيد.",
                "user_id": result.user.id,
            }
        raise HTTPException(400, "Signup failed")
    except Exception as e:
        logger.error(f"Signup failed: {e}")
        if "already registered" in str(e).lower():
            raise HTTPException(409, "البريد الإلكتروني مسجل بالفعل")
        raise HTTPException(400, str(e))

@router.post("/logout")
async def logout():
    """تسجيل الخروج (يتم على جانب العميل بحذف الرمز)"""
    return {"message": "تم تسجيل الخروج بنجاح. احذف الرمز من التخزين المحلي."}

@router.post("/reset-password")
async def reset_password(body: ResetPasswordBody):
    """إرسال رابط إعادة تعيين كلمة المرور"""
    db = get_db()
    try:
        db.auth.reset_password_email(body.email)
        return {"message": "تم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني"}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/me")
async def get_current_user_info(user_id: str):
    """جلب معلومات المستخدم الحالي"""
    db = get_db()
    try:
        profile = db.table("profiles").select("*").eq("id", user_id).single().execute()
        if profile.data:
            return {
                "user_id": user_id,
                "email": profile.data.get("email"),
                "twin_name": profile.data.get("twin_name", "توأمك"),
                "tier": profile.data.get("tier", "free"),
                "twin_energy": profile.data.get("twin_energy", 100),
                "onboarded": profile.data.get("onboarded", False),
            }
    except: pass
    return {"user_id": user_id, "tier": "free"}

logger.info("✅ Auth Routes v2.0 initialized")
