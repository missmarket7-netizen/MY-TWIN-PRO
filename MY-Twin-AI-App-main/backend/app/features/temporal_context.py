"""
Temporal-Spatial Context Engine – وعي الزمان والمكان
======================================================
يضيف بُعد "متى" و"أين" إلى ردود التوأم.
يجعل التوأم يعيش في الزمن الحقيقي مع المستخدم.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

try:
    from app.memory.emotional.emotional_memory import get_emotional_patterns
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("temporal_context")

class TemporalContextEngine:
    """يحلل الزمن والمكان لتخصيص تجربة المستخدم"""

    def get_current_context(self, user_id: str, timezone_offset: int = 3) -> Dict[str, Any]:
        """يعيد السياق الزمني الحالي للمستخدم"""
        now = datetime.now(timezone.utc) + timedelta(hours=timezone_offset)
        hour = now.hour
        weekday = now.weekday()
        
        time_of_day = (
            "صباحاً" if 5 <= hour < 12 else
            "ظهراً" if 12 <= hour < 17 else
            "مساءً" if 17 <= hour < 22 else
            "ليلاً"
        )
        
        day_type = "نهاية الأسبوع" if weekday >= 5 else "يوم عمل"
        
        return {
            "greeting": self._get_greeting(time_of_day),
            "time_of_day": time_of_day,
            "day_type": day_type,
            "season": self._get_season(),
        }

    def _get_greeting(self, time_of_day: str) -> str:
        greetings = {
            "صباحاً": "صباح الخير",
            "ظهراً": "نهارك سعيد",
            "مساءً": "مساء الخير",
            "ليلاً": "مساء الليل"
        }
        return greetings.get(time_of_day, "أهلاً")

    def _get_season(self) -> str:
        month = datetime.now().month
        if 3 <= month <= 5: return "الربيع"
        elif 6 <= month <= 8: return "الصيف"
        elif 9 <= month <= 11: return "الخريف"
        else: return "الشتاء"

    async def get_study_reminder_context(self, user_id: str) -> Optional[str]:
        """يعيد سياقاً زمنياً عن آخر مرة درس فيها المستخدم"""
        if not TCMA_AVAILABLE: return None
        try:
            from app.infrastructure.database.supabase_client import get_db
            db = get_db()
            res = db.table("user_knowledge_state").select("updated_at").eq("user_id", user_id).order("updated_at", desc=True).limit(1).execute()
            if res.data:
                last = datetime.fromisoformat(res.data[0]["updated_at"])
                diff = datetime.now(timezone.utc) - last
                if diff.days == 0:
                    return "لقد درست اليوم. ممتاز!"
                elif diff.days == 1:
                    return "آخر مرة درست فيها كانت بالأمس. هل نستمر؟"
                else:
                    return f"آخر مرة درست فيها كانت منذ {diff.days} أيام. هل نراجع قليلاً؟"
        except: pass
        return None

temporal_engine = TemporalContextEngine()
logger.info("✅ Temporal-Spatial Context Engine initialized")
