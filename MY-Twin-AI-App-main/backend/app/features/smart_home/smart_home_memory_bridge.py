"""
Smart Home Memory Bridge – جسر التكامل مع TCMA
=================================================
يربط إجراءات المنزل الذكي بالذاكرة العاطفية والاستنتاجات.
"""
import logging
from typing import Dict, Any, Optional

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_state_for_response
    from app.memory.reflection.reflection_engine import store_reflection
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("smart_home_memory")

class SmartHomeMemoryBridge:
    """يربط المنزل الذكي بـ TCMA"""

    async def log_action(self, user_id: str, command: str, result: str, emotion: str = "neutral"):
        """يسجل إجراء المنزل الذكي في الذاكرة"""
        if not TCMA_AVAILABLE:
            return

        try:
            await store_emotional_memory(
                user_id=user_id,
                expressed_text=command,
                detected_emotion={"primary": emotion, "intensity": 0.5, "valence": 0.3},
                trigger="smart_home",
                cultural_context=f"أمر منزلي: {result}"
            )
        except Exception as e:
            logger.error(f"Memory bridge error: {e}")

    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """يجلب السياق العاطفي للمستخدم لتكييف المنزل"""
        if not TCMA_AVAILABLE:
            return {"emotion": "neutral"}

        try:
            emotional = await get_emotional_state_for_response(user_id, "")
            return {
                "emotion": emotional.get("current_emotion", "neutral") if emotional else "neutral"
            }
        except:
            return {"emotion": "neutral"}

smart_home_bridge = SmartHomeMemoryBridge()
logger.info("✅ Smart Home Memory Bridge initialized")
