"""
MyTwin API v15.0.0 – Living Digital Twin Backend (Final)
============================================================
نقطة دخول موحّدة. تحميل ذكي للمسارات. تكامل مع جميع الأنظمة.
"""
import logging, sys, os, time
from pathlib import Path

# === إعداد المسارات ===
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'app'))

# === إعداد التسجيل ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("mytwin.api")
logger.info("🚀 MyTwin API v15.0.0 starting...")

# === تحميل البيئة ===
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# === FastAPI ===
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# === إعدادات التطبيق ===
try:
    from app.core.config import config
    logger.info("✅ Configuration loaded")
except Exception as e:
    logger.warning(f"⚠️ Configuration fallback: {e}")
    class config:
        ALLOWED_ORIGINS = ["*"]
        ENV = "development"
        DEBUG = True

app = FastAPI(
    title="MyTwin API",
    version="15.0.0",
    description="Living Digital Twin – Cognitive Memory & Adaptive Systems",
    docs_url="/docs" if getattr(config, 'DEBUG', False) else None,
    redoc_url="/redoc" if getattr(config, 'DEBUG', False) else None,
)

# === CORS محسّن ===
allowed = getattr(config, 'ALLOWED_ORIGINS', ["*"])
if isinstance(allowed, str):
    allowed = [o.strip() for o in allowed.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === وسيط التسجيل والتوقيت ===
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    if duration > 1.0:
        logger.warning(f"⏳ Slow request: {request.method} {request.url.path} ({duration:.2f}s)")
    return response

# ============================================================
# نظام تحميل المسارات الذكي (جميع مسارات MyTwin)
# ============================================================
ROUTES_REGISTRY = {
    # الأساسية
    "chat":        "app.api.routes.chat",
    "auth":        "app.api.routes.auth",
    "profile":     "app.api.routes.profile",
    "memories":    "app.api.routes.memories",
    "goals":       "app.api.routes.goals",
    "feedback":    "app.api.routes.feedback",
    "referral":    "app.api.routes.referral",
    "onboarding":  "app.api.routes.onboarding",
    "account":     "app.api.routes.account",
    "push":        "app.api.routes.push",
    "tasks":       "app.api.routes.tasks",
    "calendar":    "app.api.routes.calendar",
    "ads":         "app.api.routes.ads",
    "features":    "app.api.routes.features",
    "stats":       "app.api.routes.stats",
    "dev":         "app.api.routes.dev",
    "voice":       "app.api.routes.voice",
    # الميزات الجديدة
    "study":       "app.api.routes.study_routes",          # ATHENA
    "business":    "app.api.routes.business_routes",       # GROWTH-HIVE
    "creator":     "app.api.routes.creator_routes",        # C.R.E.A.T.O.R.
    "code_lab":    "app.api.routes.code_lab_routes",       # C.O.D.E. Lab
    "life_coach":  "app.api.routes.life_coach_routes",     # L.I.F.E. C.O.A.C.H.
    "dreams":      "app.api.routes.dream_routes",          # Dream Analysis
    "smart_home":  "app.api.routes.smart_home_routes",     # S.M.A.R.T. Home
    "pass":        "app.api.routes.task_manager_routes",   # P.A.S.S.
    # المحركات المتقدمة
    "reports":     "app.api.routes.reports",               # Weekly Reports
    "graph":       "app.api.routes.graph_routes",          # Graph Mining
    "recommendations": "app.api.routes.recommendations",   # Unified Recommendations
    "meta":        "app.api.routes.meta_routes",           # Meta-Reflection
    "relationship":"app.api.routes.relationship",          # Relationship State
    "ai_trainer":  "app.api.routes.ai_trainer_routes",     # AI Trainer
    # تكاملات خارجية
    "telegram":    "app.infrastructure.integrations.telegram_webhook",
}

loaded_routes = []
failed_routes = []

for name, module_path in ROUTES_REGISTRY.items():
    try:
        mod = __import__(module_path, fromlist=['router'])
        app.include_router(mod.router)
        loaded_routes.append(name)
        logger.info(f"   ✅ {name}")
    except ImportError as e:
        failed_routes.append((name, f"Import: {e}"))
        logger.debug(f"   📦 {name} not available: {e}")
    except AttributeError as e:
        failed_routes.append((name, f"Router: {e}"))
        logger.warning(f"   ⚠️ {name} has no router: {e}")
    except Exception as e:
        failed_routes.append((name, str(e)))
        logger.error(f"   ❌ {name} failed: {e}")

logger.info(f"🚀 {len(loaded_routes)}/{len(ROUTES_REGISTRY)} routes loaded")
if failed_routes:
    logger.info(f"   Skipped: {[n for n,_ in failed_routes]}")

# === نقاط النهاية الأساسية ===
@app.get("/", tags=["status"])
async def root():
    return {
        "name": "MyTwin API",
        "version": "15.0.0",
        "environment": os.getenv("ENV", "production"),
        "loaded_routes": len(loaded_routes),
        "total_registered": len(ROUTES_REGISTRY),
    }

@app.get("/health", tags=["status"])
async def health():
    health_status = {
        "api": "healthy",
        "routes": len(loaded_routes),
        "timestamp": time.time(),
    }
    # فحص طبقات الذاكرة
    try:
        from app.memory.emotional.emotional_memory import TABLE_NAME
        health_status["memory_emotional"] = "available"
    except: health_status["memory_emotional"] = "unavailable"
    
    try:
        from app.memory.graph.memory_graph import TABLE_EDGES
        health_status["memory_graph"] = "available"
    except: health_status["memory_graph"] = "unavailable"
    
    try:
        from app.features.study.athena_orchestrator import athena
        health_status["athena_study"] = "available"
    except: health_status["athena_study"] = "unavailable"
    
    try:
        from app.infrastructure.ai.provider_router import provider_router
        health_status["ai_provider"] = "available"
    except: health_status["ai_provider"] = "unavailable"
    
    try:
        from app.infrastructure.ai.internal_model_provider import internal_model
        health_status["internal_model"] = "loaded" if internal_model._loaded else "available"
    except: health_status["internal_model"] = "unavailable"
    
    return JSONResponse(content=health_status)

@app.get("/ready", tags=["status"])
async def ready():
    return {"status": "ready", "routes": len(loaded_routes)}

@app.get("/live", tags=["status"])
async def live():
    return {"status": "live"}

@app.on_event("startup")
async def startup_event():
    logger.info(f"🌟 MyTwin API v15.0.0 fully started")
    
    # مهام خلفية اختيارية
    try:
        import asyncio
        async def periodic_tasks():
            while True:
                await asyncio.sleep(86400)  # كل 24 ساعة
                try:
                    from app.infrastructure.cache.memory_cleanup_service import run_memory_cleanup
                    await run_memory_cleanup(dry=False)
                    logger.info("🔄 Memory cleanup completed")
                except: pass
        asyncio.create_task(periodic_tasks())
        
        # بدء وضع الظل (Shadow Mode)
        try:
            from app.features.shadow_mode import ShadowScheduler
            shadow = ShadowScheduler()
            asyncio.create_task(shadow.start())
            logger.info("🌑 Shadow Mode started")
        except: pass
    except: pass

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 MyTwin API shutting down")
    try:
        from app.background.queue import shutdown as queue_shutdown
        await queue_shutdown()
    except: pass

# === نقطة دخول للتشغيل المباشر ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=getattr(config, 'DEBUG', False),
        log_level="info"
    )
