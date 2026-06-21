"""
Alert Service v2.0 – نظام تنبيهات متكامل
=============================================
يدعم: Slack، Telegram، Discord، Email.
يتكامل مع system_monitor لتحليل المقاييس.
"""
import logging, os, httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger("alert_service")

# الإعدادات
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
TELEGRAM_ALERT_CHAT = os.getenv("TELEGRAM_ALERT_CHAT_ID", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")

# ============================================================
# إرسال التنبيهات
# ============================================================
async def send_alert(
    message: str,
    severity: str = "warning",
    source: str = "system",
    metrics: Optional[Dict[str, Any]] = None
) -> bool:
    """
    إرسال تنبيه إلى جميع القنوات المكونة.
    severity: info, warning, critical, emergency
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴", "emergency": "🚨"}.get(severity, "⚠️")
    
    formatted_message = f"{emoji} [{severity.upper()}] {source}\n⏰ {timestamp}\n📋 {message}"
    if metrics:
        formatted_message += f"\n📊 Metrics: {metrics}"

    sent = False

    # 1. Slack
    if SLACK_WEBHOOK:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    SLACK_WEBHOOK,
                    json={"text": formatted_message},
                    timeout=5.0
                )
                sent = True
        except Exception as e:
            logger.error(f"Slack alert failed: {e}")

    # 2. Telegram
    if TELEGRAM_ALERT_CHAT and TELEGRAM_BOT_TOKEN:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": TELEGRAM_ALERT_CHAT,
                        "text": formatted_message,
                        "parse_mode": "HTML"
                    },
                    timeout=5.0
                )
                sent = True
        except Exception as e:
            logger.error(f"Telegram alert failed: {e}")

    # 3. Discord
    if DISCORD_WEBHOOK:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    DISCORD_WEBHOOK,
                    json={"content": formatted_message[:2000]},
                    timeout=5.0
                )
                sent = True
        except Exception as e:
            logger.error(f"Discord alert failed: {e}")

    return sent

# ============================================================
# فحوصات صحية
# ============================================================
async def check_system_health() -> Dict[str, Any]:
    """
    فحص صحة النظام وإرسال تنبيهات إذا لزم الأمر.
    """
    issues = []

    # 1. فحص Supabase
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        db.table("profiles").select("id", count="exact").limit(1).execute()
    except Exception as e:
        issues.append(f"Supabase: {str(e)[:100]}")

    # 2. فحص Redis
    try:
        from app.core.redis_config import get_redis, REDIS_AVAILABLE
        if REDIS_AVAILABLE:
            redis = get_redis()
            redis.ping()
    except Exception as e:
        issues.append(f"Redis: {str(e)[:100]}")

    # 3. فحص AI APIs
    try:
        from app.infrastructure.ai.provider_router import provider_router
        test = await provider_router.generate("ping", language="en")
        if not test:
            issues.append("AI APIs: No response")
    except Exception as e:
        issues.append(f"AI APIs: {str(e)[:100]}")

    if issues:
        await send_alert(
            f"مشاكل في صحة النظام:\n" + "\n".join(f"• {i}" for i in issues),
            severity="critical",
            source="health_check"
        )

    return {
        "healthy": len(issues) == 0,
        "issues": issues,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

async def check_health_metrics(metrics: Dict[str, Any]) -> None:
    """فحص المقاييس وإرسال تنبيهات حسب الحدود"""
    if metrics.get("p95_latency_ms", 0) > 3000:
        await send_alert(f"زمن استجابة مرتفع: P95 = {metrics['p95_latency_ms']}ms", severity="critical", metrics=metrics)
    if metrics.get("error_count", 0) > 50:
        await send_alert(f"معدل أخطاء مرتفع: {metrics['error_count']} خطأ", severity="critical", metrics=metrics)
    if metrics.get("memory_usage_percent", 0) > 90:
        await send_alert(f"استهلاك ذاكرة مرتفع: {metrics['memory_usage_percent']}%", severity="warning", metrics=metrics)

logger.info("✅ Alert Service v2.0 initialized")
