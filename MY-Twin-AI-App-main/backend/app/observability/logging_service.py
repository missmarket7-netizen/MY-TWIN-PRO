"""
Centralised Logging Service v2.0
==================================
سجلات منظمة مع تتبع الطلبات، ومستويات تحكم، وتكامل Sentry.
"""
import logging, os, sys, json
from typing import Optional
from datetime import datetime, timezone

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

class CorrelationFilter(logging.Filter):
    """فلتر يضيف correlation_id لكل سجل"""
    _correlation_id: Optional[str] = None

    def filter(self, record):
        record.correlation_id = CorrelationFilter._correlation_id or "-"
        return True

class JsonFormatter(logging.Formatter):
    """تنسيق JSON للإنتاج"""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", "-"),
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """تهيئة نظام التسجيل"""
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    
    # استخدام JSON في الإنتاج، نص بسيط في التطوير
    if ENVIRONMENT == "production":
        handler.setFormatter(JsonFormatter())
    else:
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(correlation_id)s | %(message)s"
        handler.setFormatter(logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S"))
    
    handler.addFilter(CorrelationFilter())
    root.addHandler(handler)
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # إسكات المكتبات المزعجة
    for lib in ["httpx", "httpcore", "urllib3", "asyncio", "uvicorn.access"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    # تكامل Sentry
    sentry_dsn = os.getenv("SENTRY_DSN", "")
    if sentry_dsn and ENVIRONMENT == "production":
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)
            logging.info("✅ Sentry integrated")
        except ImportError:
            logging.warning("⚠️ sentry_sdk not installed")

    logging.info(f"Logging initialised at level {LOG_LEVEL}")

def set_correlation_id(cid: str):
    """تعيين معرّف التتبع للطلب الحالي"""
    CorrelationFilter._correlation_id = cid

def get_logger(name: str) -> logging.Logger:
    """الحصول على مسجل باسم محدد"""
    return logging.getLogger(name)

async def log_error(error: Exception, context: str = "", severity: str = "error"):
    """تسجيل خطأ مع إرسال تنبيه إذا كان حرجاً"""
    logger = get_logger("error_tracker")
    logger.error(f"{context}: {str(error)}", exc_info=True)
    
    if severity == "critical":
        try:
            from app.observability.alert_service import send_alert
            await send_alert(f"خطأ حرج: {context}\n{str(error)[:500]}", severity="critical")
        except:
            pass

logger = get_logger("logging_service")
