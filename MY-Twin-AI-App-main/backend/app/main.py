"""
MyTwin API v12.1.0 – Complete Digital Twin Backend (Production Ready)
"""
import logging, os, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from app.core.config import config
from app.observability.logging_service import setup_logging
from app.infrastructure.monitoring.sentry_config import init_sentry
from app.middleware.security_audit import security_audit

# Import all route modules
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
from app.api.routes.features import router as features_router
from app.infrastructure.integrations.telegram_webhook import router as telegram_router, setup_webhook

setup_logging()
init_sentry()

logger = logging.getLogger("mytwin")
logger.info("🚀 MyTwin API v12.1.0 starting...")

app = FastAPI(title="MyTwin API", version="12.1.0")

# Global Security Middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # 1. Input sanitization for all routes
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
            for key, value in body.items():
                if isinstance(value, str):
                    threat = security_audit.scan_payload(value)
                    if threat:
                        return JSONResponse(status_code=400, content={"detail": threat})
        except:
            pass
    # 2. Correlation ID for observability
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Global Exception Handler (never leak internal errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": security_audit.safe_error(exc)}
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(memories_router)
app.include_router(goals_router)
app.include_router(feedback_router)
app.include_router(referral_router)
app.include_router(onboarding_router)
app.include_router(account_router)
app.include_router(push_router)
app.include_router(tasks_router)
app.include_router(calendar_router)
app.include_router(ads_router)
app.include_router(features_router)
app.include_router(telegram_router)

@app.get("/")
async def root():
    return {"status": "ok", "version": "12.1.0", "name": "MyTwin Digital Twin API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "12.1.0"}

@app.on_event("startup")
async def startup():
    await setup_webhook()
    logger.info("✅ MyTwin API v12.1.0 ready")
