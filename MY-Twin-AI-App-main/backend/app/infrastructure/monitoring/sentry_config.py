"""
Sentry Monitoring Setup v2.0 – متكامل مع Observability
=========================================================
- تكامل مع Logging Service
- تكامل مع Metrics Service
- تكامل مع Alert Service
- إعدادات متقدمة للإنتاج
"""
import os, logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger("sentry_config")

def init_sentry():
    """تهيئة Sentry للمراقبة"""
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        logger.warning("⚠️ SENTRY_DSN غير مضبوط – المراقبة معطلة")
        return False

    environment = os.getenv("ENVIRONMENT", "production")
    
    # تكامل مع نظام التسجيل
    sentry_logging = LoggingIntegration(
        level=logging.WARNING,        # سجل التحذيرات والأخطاء
        event_level=logging.ERROR,    # أرسل الأخطاء كأحداث
    )

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            AsyncioIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=0.3 if environment == "production" else 1.0,
        profiles_sample_rate=0.1,
        environment=environment,
        send_default_pii=False,
        max_breadcrumbs=100,
        attach_stacktrace=True,
        _experiments={"continuous_profiling_auto_start": True},
    )

    # إضافة معلومات البيئة
    sentry_sdk.set_tag("version", os.getenv("APP_VERSION", "1.0.0"))
    sentry_sdk.set_tag("railway_service", os.getenv("RAILWAY_SERVICE_NAME", "mytwin"))

    logger.info(f"✅ Sentry مهيأ (environment: {environment})")
    return True


def capture_exception(error: Exception, context: dict = None):
    """تسجيل استثناء في Sentry مع سياق"""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """تسجيل رسالة في Sentry"""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        sentry_sdk.capture_message(message, level=level)


def set_user_info(user_id: str, tier: str = "free", extras: dict = None):
    """ربط مستخدم بـ Sentry للتتبع"""
    sentry_sdk.set_user({
        "id": user_id,
        "tier": tier,
        **(extras or {})
    })


def clear_user():
    """إزالة المستخدم من السياق"""
    sentry_sdk.set_user(None)


logger.info("✅ Sentry Config v2.0 initialized")
