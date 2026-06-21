"""
Emotional Timeline v3.0 – متكامل مع TCMA Emotional Memory
=============================================================
يسجل المشاعر في TCMA (التي تخزّنها في Supabase تلقائياً).
يحلل الاتجاهات من الذاكرة العاطفية مباشرة.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_patterns
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

class EmotionalTimeline:
    async def record_emotion(self, user_id: str, text: str) -> Optional[Dict[str, Any]]:
        """تحليل النص وتسجيل المشاعر في TCMA"""
        if not TCMA_AVAILABLE:
            return None
        try:
            from app.twin_state.emotional_service import emotional_service
            result = await emotional_service.analyze(text, user_id)
            if result:
                # TCMA تخزّن في Supabase داخلياً
                await store_emotional_memory(
                    user_id=user_id,
                    expressed_text=text,
                    detected_emotion=result,
                    trigger="chat"
                )
                return result
        except Exception as e:
            logger.error(f"Failed to record emotion: {e}")
        return None

    async def get_emotion_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """ملخص المشاعر من TCMA"""
        if not TCMA_AVAILABLE:
            return {"dominant": "neutral", "average_intensity": 0.5}
        try:
            patterns = await get_emotional_patterns(user_id, days)
            return {
                "dominant": patterns.get("dominant_emotion", "neutral"),
                "distribution": patterns.get("emotion_distribution", {}),
                "patterns": patterns.get("patterns", []),
                "recommendation": patterns.get("recommendation", ""),
                "source": "tcma"
            }
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {"dominant": "neutral", "average_intensity": 0.5}

emotional_timeline = EmotionalTimeline()
