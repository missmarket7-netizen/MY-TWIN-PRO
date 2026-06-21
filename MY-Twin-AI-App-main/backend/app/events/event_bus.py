"""
Event Bus v2.0 – نظام أحداث مركزي متكامل
=============================================
- تكامل مع TCMA (تسجيل الأحداث كذكريات)
- تكامل مع Observability (Metrics, Logging)
- دعم لأنواع الأحداث الجديدة (الميزات المطورة)
"""
import logging, asyncio
from typing import Dict, List, Callable, Any, Awaitable
from datetime import datetime, timezone

logger = logging.getLogger("event_bus")

# سجل المشتركين العالمي
_subscribers: Dict[str, List[Callable[..., Awaitable[None]]]] = {}

def subscribe(event_type: str, handler: Callable[..., Awaitable[None]]) -> None:
    """تسجيل معالج لنوع حدث محدد"""
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(handler)
    logger.info(f"📡 Subscribed: {event_type} → {handler.__name__}")

async def emit(event: Dict[str, Any]) -> None:
    """إرسال حدث إلى جميع المشتركين (آمن، لا يرفع استثناءات)"""
    event_type = event.get("type", "unknown")
    handlers = _subscribers.get(event_type, []) + _subscribers.get("*", [])

    if not handlers:
        return

    logger.info(f"📢 Event: {event_type} | user={event.get('user_id', '-')}")

    async def _safe_run(handler):
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"❌ Handler {handler.__name__} failed for {event_type}: {e}")

    await asyncio.gather(*[_safe_run(h) for h in handlers])

# ========== المشتركون المدمجون ==========

async def _log_event(event: Dict[str, Any]) -> None:
    """تسجيل جميع الأحداث"""
    logger.info(f"📝 {event.get('type')}: user={event.get('user_id')}")

async def _track_metrics(event: Dict[str, Any]) -> None:
    """تسجيل مقاييس الأحداث"""
    try:
        from app.observability.metrics_service import metrics
        metrics.record_request(f"event:{event.get('type')}", 200, 0, event.get('user_id'))
    except: pass

async def _store_memory(event: Dict[str, Any]) -> None:
    """تخزين الأحداث المهمة في TCMA"""
    if event.get("type") in ["stage_changed", "goal_completed", "reflection_completed"]:
        try:
            from app.memory.emotional.emotional_memory import store_emotional_memory
            await store_emotional_memory(
                user_id=event.get("user_id", "unknown"),
                expressed_text=event.get("summary", event.get("type")),
                detected_emotion={"primary": "neutral", "intensity": 0.7, "valence": 0.5},
                trigger=event.get("type")
            )
        except: pass

# تسجيل المشتركين
subscribe("*", _log_event)
subscribe("*", _track_metrics)
subscribe("*", _store_memory)

logger.info("✅ Event Bus v2.0 initialized (TCMA + Observability)")
