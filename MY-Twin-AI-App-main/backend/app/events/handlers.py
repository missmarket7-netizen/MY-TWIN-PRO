"""
Event Handlers v3.0 – متكاملة مع TCMA والمحركات الجديدة
=============================================================
تتفاعل مع الأحداث لتخزين الذاكرة، توليد الاستنتاجات، والتكامل مع Proactive Engine.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("event_handlers")

async def on_stage_changed(event: Dict[str, Any]) -> None:
    """تغير مرحلة العلاقة ← تخزين في الذاكرة العاطفية"""
    logger.info(f"🎉 Stage up: {event.get('old_stage')} → {event.get('new_stage')}")
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        await store_emotional_memory(
            user_id=event.get("user_id"),
            expressed_text=f"تغيرت مرحلة العلاقة إلى {event.get('new_stage')}",
            detected_emotion={"primary": "joy", "intensity": 0.9, "valence": 0.8},
            trigger="stage_changed"
        )
        # تنبيه استباقي
        try:
            from app.features.proactive_engine import proactive_engine
            await proactive_engine.generate_proactive_message(event.get("user_id"))
        except: pass
    except Exception as e:
        logger.warning(f"on_stage_changed failed: {e}")

async def on_memory_created(event: Dict[str, Any]) -> None:
    """ذاكرة جديدة ← توليد استنتاج"""
    logger.info(f"🧠 Memory: {event.get('memory_type')}")
    try:
        from app.memory.reflection.reflection_engine import process_message_for_reflections
        await process_message_for_reflections(
            user_id=event.get("user_id"),
            message=event.get("content", "ذاكرة جديدة"),
            language="ar",
            detected_emotion=event.get("emotion", "neutral")
        )
    except Exception as e:
        logger.warning(f"on_memory_created failed: {e}")

async def on_goal_completed(event: Dict[str, Any]) -> None:
    """هدف مكتمل ← تخزين عاطفة إيجابية + استنتاج"""
    logger.info(f"🏆 Goal: {event.get('title')}")
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        from app.memory.reflection.reflection_engine import store_reflection
        await store_emotional_memory(
            user_id=event.get("user_id"),
            expressed_text=f"أكملت هدف: {event.get('title')}",
            detected_emotion={"primary": "joy", "intensity": 0.9, "valence": 0.8},
            trigger="goal_completed"
        )
        await store_reflection(
            user_id=event.get("user_id"),
            insight_type="achievement",
            insight_text=f"أنجز هدفاً: {event.get('title')}",
            confidence=0.9
        )
    except Exception as e:
        logger.warning(f"on_goal_completed failed: {e}")

async def on_reflection_completed(event: Dict[str, Any]) -> None:
    """تأمل مكتمل ← ربط بالرسم البياني للذاكرة"""
    logger.info(f"💭 Reflection: {str(event.get('summary', ''))[:80]}")
    try:
        from app.memory.graph.memory_graph import auto_create_edges_from_memory
        await auto_create_edges_from_memory(
            user_id=event.get("user_id"),
            memory_id=event.get("memory_id", ""),
            memory_type="reflection",
            memory_data={"trigger": event.get("type", "reflection")}
        )
    except Exception as e:
        logger.warning(f"on_reflection_completed failed: {e}")

async def on_attachment_detected(event: Dict[str, Any]) -> None:
    """نمط تعلق مكتشف ← تحديث الهوية"""
    logger.info(f"🔍 Attachment: {event.get('style')}")
    try:
        from app.memory.identity.identity_model import analyze_and_update_identity
        await analyze_and_update_identity(
            user_id=event.get("user_id"),
            message=f"نمط تعلقه: {event.get('style')}",
            language="ar"
        )
    except Exception as e:
        logger.warning(f"on_attachment_detected failed: {e}")

async def on_journey_phase_changed(event: Dict[str, Any]) -> None:
    """تغير طور الرحلة ← تخزين عاطفة"""
    logger.info(f"🗺️ Journey phase: {event.get('user_id')}")
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        await store_emotional_memory(
            user_id=event.get("user_id"),
            expressed_text=f"دخل مرحلة جديدة: {event.get('phase', 'unknown')}",
            detected_emotion={"primary": "joy", "intensity": 0.8, "valence": 0.7},
            trigger="journey_phase_changed"
        )
    except Exception as e:
        logger.warning(f"on_journey_phase_changed failed: {e}")

async def on_identity_evolved(event: Dict[str, Any]) -> None:
    """تطور الهوية ← تسجيل في الرسم البياني"""
    logger.info(f"🎭 Identity evolved: {event.get('user_id')}")
    try:
        from app.memory.graph.memory_graph import auto_create_edges_from_memory
        await auto_create_edges_from_memory(
            user_id=event.get("user_id"),
            memory_id=event.get("identity_id", ""),
            memory_type="identity",
            memory_data={"trigger": "identity_evolved"}
        )
    except Exception as e:
        logger.warning(f"on_identity_evolved failed: {e}")

# تسجيل المعالجات
from app.events.event_bus import subscribe

subscribe("stage_changed", on_stage_changed)
subscribe("memory_created", on_memory_created)
subscribe("goal_completed", on_goal_completed)
subscribe("reflection_completed", on_reflection_completed)
subscribe("attachment_detected", on_attachment_detected)
subscribe("journey_phase_changed", on_journey_phase_changed)
subscribe("identity_evolved", on_identity_evolved)

logger.info("✅ All Event Handlers v3.0 registered (TCMA Integrated)")
