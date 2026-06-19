"""MyTwin API v12.4.0 – Resilient Entry Point"""
import logging, sys, os, traceback

# تأكد من أن مجلد backend في مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# تكوين التسجيل الأساسي
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mytwin_startup")

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from dotenv import load_dotenv

    load_dotenv()
    logger.info("✅ المكتبات الأساسية محملة")

    from app.core.config import config
    from app.observability.logging_service import setup_logging
    from app.infrastructure.monitoring.sentry_config import init_sentry
    logger.info("✅ الإعدادات والمراقبة محملة")

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
    from app.api.routes.features import router as features_router
    from app.api.routes.stats import router as stats_router
    from app.api.routes.dev import router as dev_router
    from app.infrastructure.integrations.telegram_webhook import router as telegram_router, setup_webhook
    logger.info("✅ جميع المسارات محملة")

    app = FastAPI(title="MyTwin API", version="12.4.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
    app.include_router(stats_router)
    app.include_router(dev_router)
    app.include_router(telegram_router)

    @app.get("/")
    async def root():
        return {"status": "ok", "version": "12.4.0"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.on_event("startup")
    async def startup():
        await setup_webhook()
        logger.info("✅ MyTwin API جاهز")

    logger.info("🚀 MyTwin API v12.4.0 جاهز للتشغيل")

except Exception as e:
    logger.error(f"❌ فشل تشغيل التطبيق: {e}")
    logger.error(traceback.format_exc())
    raise
