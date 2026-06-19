"""
MyTwin API v13.0.0 – Railway Optimized
"""
import logging, sys, os

# === إعداد المسارات لبيئة Railway ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'app'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mytwin")
logger.info(f"🚀 MyTwin API v13.0.0 starting...")
logger.info(f"   BASE_DIR: {BASE_DIR}")
logger.info(f"   sys.path: {sys.path[:2]}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

# استيراد config مع معالجة الخطأ
try:
    from app.core.config import config
    logger.info("✅ app.core.config loaded")
except Exception as e:
    logger.error(f"❌ app.core.config failed: {e}")
    class config:
        ALLOWED_ORIGINS = ["*"]

app = FastAPI(title="MyTwin API", version="13.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS if hasattr(config, 'ALLOWED_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تحميل المسارات مع معالجة الأخطاء لكل منها
ROUTES = {
    "chat": "app.api.routes.chat",
    "auth": "app.api.routes.auth",
    "profile": "app.api.routes.profile",
    "memories": "app.api.routes.memories",
    "goals": "app.api.routes.goals",
    "feedback": "app.api.routes.feedback",
    "referral": "app.api.routes.referral",
    "onboarding": "app.api.routes.onboarding",
    "account": "app.api.routes.account",
    "push": "app.api.routes.push",
    "tasks": "app.api.routes.tasks",
    "calendar": "app.api.routes.calendar",
    "ads": "app.api.routes.ads",
    "features": "app.api.routes.features",
    "stats": "app.api.routes.stats",
    "dev": "app.api.routes.dev",
}

loaded = 0
for name, module_path in ROUTES.items():
    try:
        mod = __import__(module_path, fromlist=['router'])
        app.include_router(mod.router)
        loaded += 1
        logger.info(f"   ✅ {name}")
    except Exception as e:
        logger.warning(f"   ⚠️  {name}: {str(e)[:80]}")

logger.info(f"🚀 {loaded}/{len(ROUTES)} مسارات محملة")

@app.get("/")
async def root():
    return {"status": "ok", "version": "13.0.0", "routes": loaded}

@app.get("/health")
async def health():
    return {"status": "healthy", "routes": loaded}
