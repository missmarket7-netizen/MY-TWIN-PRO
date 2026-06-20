"""Alert Service – sends alerts on critical conditions."""
import logging, os, httpx
from typing import Dict, Any

logger = logging.getLogger("alert_service")

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
TELEGRAM_ALERT_CHAT = os.getenv("TELEGRAM_ALERT_CHAT_ID", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

async def send_alert(message: str, severity: str = "warning"):
    """Send alert to configured channels."""
    if SLACK_WEBHOOK:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(SLACK_WEBHOOK, json={"text": f"[{severity.upper()}] {message}"})
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    if TELEGRAM_ALERT_CHAT and TELEGRAM_BOT_TOKEN:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_ALERT_CHAT, "text": f"[{severity.upper()}] {message}"})
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

async def check_health_metrics(metrics: Dict[str, Any]):
    """Check metrics and alert if necessary."""
    if metrics.get("p95_latency_ms", 0) > 3000:
        await send_alert(f"High latency: P95 = {metrics['p95_latency_ms']}ms", "critical")
    if metrics.get("error_count", 0) > 50:
        await send_alert(f"High error rate: {metrics['error_count']} errors", "critical")
