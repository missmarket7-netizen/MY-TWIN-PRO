"""
MyTwin – Emotional Timeline v2.0 (متوافق مع Emotional Engine v8.0)
- يسجل المشاعر في Supabase
- يحلل الاتجاهات ويُنتج ملخصات
"""
import os, logging, asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from app.twin_state.emotional_service import EmotionalStateTracker

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
db: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

class EmotionalTimeline:
    def __init__(self):
        # ✅ لا نمرر أي معاملات، EmotionalStateTracker يقرأ المفتاح من البيئة داخلياً
        self.emotion_tracker = EmotionalStateTracker()

    async def record_emotion(self, user_id: str, text: str) -> Optional[Dict[str, Any]]:
        """تحليل النص وتسجيل المشاعر في Supabase"""
        if not db:
            return None
        try:
            result = await self.emotion_tracker.analyze(text)
            if result:
                db.table("emotional_timeline").insert({
                    "user_id": user_id,
                    "primary_emotion": result.get("primary", "neutral"),
                    "intensity": result.get("intensity", 0.5),
                    "valence": result.get("valence", 0.0),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }).execute()
                return result
        except Exception as e:
            logger.error(f"Failed to record emotion: {e}")
        return None

    async def get_emotion_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """ملخص المشاعر لآخر أيام"""
        if not db:
            return {"dominant": "neutral", "average_intensity": 0.5}
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            res = db.table("emotional_timeline").select("*").eq("user_id", user_id).gte("created_at", cutoff).execute()
            if not res.data:
                return {"dominant": "neutral", "average_intensity": 0.5}
            
            emotions = [r["primary_emotion"] for r in res.data]
            intensities = [r.get("intensity", 0.5) for r in res.data]
            
            freq: Dict[str, int] = {}
            for e in emotions:
                freq[e] = freq.get(e, 0) + 1
            dominant = max(freq, key=freq.get)
            avg_intensity = sum(intensities) / len(intensities)
            
            return {"dominant": dominant, "average_intensity": avg_intensity}
        except Exception as e:
            logger.error(f"Failed to get emotion summary: {e}")
            return {"dominant": "neutral", "average_intensity": 0.5}

emotional_timeline = EmotionalTimeline()
print("✅ Emotional Timeline v2.0 جاهز")
