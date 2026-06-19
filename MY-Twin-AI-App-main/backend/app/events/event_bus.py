"""
Event Bus – Central event system for the digital twin.
Publishers emit events. Subscribers react asynchronously.
Prevents service entanglement. Ready for global scale.
"""
import logging
import asyncio
from typing import Dict, List, Callable, Any, Awaitable
from app.models.event import BaseEvent

logger = logging.getLogger("event_bus")

# Global subscriber registry
_subscribers: Dict[str, List[Callable[[BaseEvent], Awaitable[None]]]] = {}


def subscribe(event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
    """Register a handler for a specific event type."""
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(handler)
    logger.info(f"📡 Subscribed: {event_type} → {handler.__name__}")


def unsubscribe(event_type: str, handler: Callable) -> None:
    """Remove a handler from an event type."""
    if event_type in _subscribers:
        _subscribers[event_type] = [h for h in _subscribers[event_type] if h != handler]


async def emit(event: BaseEvent) -> None:
    """
    Emit an event to all subscribers.
    Runs handlers in parallel. Failures are logged, never raised.
    """
    handlers = _subscribers.get(event.type.value if hasattr(event.type, 'value') else event.type, [])
    if not handlers:
        return

    logger.info(f"📢 Event: {event.type} for user {event.user_id}")

    async def _safe_run(handler):
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"❌ Handler {handler.__name__} failed for event {event.type}: {e}")

    tasks = [_safe_run(h) for h in handlers]
    await asyncio.gather(*tasks)


# ── Built-in Subscribers ──────────────────────────────

async def _log_event(event: BaseEvent) -> None:
    """Default logger for all events."""
    logger.info(f"📝 {event.type}: user={event.user_id} id={event.id}")


subscribe("*", _log_event)


async def _notify_stage_up(event: BaseEvent) -> None:
    """When stage changes, send a notification."""
    if event.type.value == "stage_changed" and hasattr(event, 'message_ar'):
        try:
            from app.infrastructure.voice.voice_service import speak
            msg = event.message_ar
            await speak(msg, tier="free", lang="ar")
        except Exception as e:
            logger.warning(f"Stage up voice failed: {e}")


subscribe("stage_changed", _notify_stage_up)


async def _track_analytics(event: BaseEvent) -> None:
    """Log every event for analytics."""
    # In production, this writes to an analytics database or queue.
    logger.info(f"📊 Analytics: {event.type} | user={event.user_id}")


subscribe("*", _track_analytics)
