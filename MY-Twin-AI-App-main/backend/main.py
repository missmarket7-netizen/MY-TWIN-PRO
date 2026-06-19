"""
MyTwin API v12.3.0 – Main Entry Point
جميع نقاط النهاية في ملف واحد.
"""
import logging, sys, os

# تأكد من أن مجلد backend في مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# ========== الإعدادات والمراقبة ==========
from app.core.config import config
from app.observability.logging_service import setup_logging
from app.infrastructure.monitoring.sentry_config import init_sentry

# ========== المسارات ==========
from app.api.routes.chat import router as chat_router
from app.api.routes.auth import router as auth_router
from app.api.routes.profile import router as profile_router
from app.api.routes.memories import router as memories_router
from app.api.routes.goals import router as goals_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.referral import router as referral_router
from app.api.routes.onboarding import router as onboarding_router
from app.api.routes.account import router as account_router
from app.api.routes.push import router as push_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.ads import router as ads_router
from app.api.routes.dev import router as dev_router
from app.api.routes.stats import router as stats_router
from app.api.routes.features import router as features_router
from app.infrastructure.integrations.telegram_webhook import router as telegram_router, setup_webhook

setup_logging()
init_sentry()

logger = logging.getLogger("mytwin")
logger.info("🚀 MyTwin API v12.3.0 starting...")

app = FastAPI(title="MyTwin API", version="12.3.0")

# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== تسجيل كل المسارات ==========
app.include_router(chat_router)          # /api/chat, /api/chat/stream
app.include_router(auth_router)          # /api/auth/login, /api/auth/signup
app.include_router(profile_router)        # /api/profile, /api/moods
app.include_router(memories_router)       # /api/memories
app.include_router(goals_router)          # /api/goals
app.include_router(feedback_router)       # /api/feedback
app.include_router(referral_router)       # /api/referral/*
app.include_router(onboarding_router)     # /api/onboarding
app.include_router(account_router)        # /api/account, /api/me/export
app.include_router(push_router)           # /api/push-token
app.include_router(tasks_router)          # /api/tasks
app.include_router(calendar_router)       # /api/calendar/*
app.include_router(ads_router)            # /api/ads/*
app.include_router(dev_router)
app.include_router(stats_router)
app.include_router(features_router)       # /api/features/* (study, code, business, coach, image, dream, content, smart-home)
app.include_router(telegram_router)       # /api/telegram/*

# ========== فحص الصحة ==========
@app.get("/")
async def root():
    return {"status": "ok", "version": "12.3.0", "name": "MyTwin API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "12.3.0"}

# ========== بدء التشغيل ==========
@app.on_event("startup")
async def startup():
    await setup_webhook()
    logger.info("✅ MyTwin API v12.3.0 ready – جميع المسارات نشطة")
