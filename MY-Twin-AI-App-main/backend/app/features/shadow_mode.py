"""
Shadow Mode Engine – الوعي الخفي للمستخدم
=============================================
يعمل بشكل دوري (كل 6 ساعات) لتحليل سلوك المستخدم دون علمه.
يكتشف الأنماط، التغيرات، ويضيف استنتاجات صامتة إلى TCMA.
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import get_emotional_patterns
    from app.memory.reflection.reflection_engine import store_reflection
    from app.memory.graph.memory_graph import auto_create_edges_from_memory
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("shadow_mode")

class ShadowModeEngine:
    """يعمل في الخلفية لتحليل سلوك المستخدم بشكل دوري"""

    async def run_daily_analysis(self, user_id: str) -> Dict[str, Any]:
        """تحليل شامل للمستخدم (يُستدعى كل 6-24 ساعة)"""
        if not DB_AVAILABLE or not TCMA_AVAILABLE:
            return {"status": "unavailable"}

        insights = []

        # 1. تحليل الانقطاع عن الدراسة
        study_gap = await self._detect_study_gap(user_id)
        if study_gap:
            insights.append(study_gap)

        # 2. تحليل المشاعر المتكررة
        emotion_shift = await self._detect_emotional_shift(user_id)
        if emotion_shift:
            insights.append(emotion_shift)

        # 3. تحليل نشاط المشروع التجاري
        business_pause = await self._detect_business_pause(user_id)
        if business_pause:
            insights.append(business_pause)

        return {"user_id": user_id, "insights_added": len(insights), "insights": insights}

    async def _detect_study_gap(self, user_id: str) -> Optional[Dict]:
        """يكتشف إذا توقف المستخدم عن الدراسة فجأة"""
        db = get_db()
        recent_study = db.table("user_knowledge_state").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(1).execute()
        if recent_study.data:
            last_study = datetime.fromisoformat(recent_study.data[0]["updated_at"])
            days_since = (datetime.now(timezone.utc) - last_study).days
            if days_since > 3:
                await store_reflection(
                    user_id=user_id,
                    insight_type="study_gap",
                    insight_text=f"توقف عن الدراسة لمدة {days_since} أيام",
                    confidence=0.8,
                )
                return {"type": "study_gap", "days": days_since}
        return None

    async def _detect_emotional_shift(self, user_id: str) -> Optional[Dict]:
        """يكتشف تحولاً عاطفياً كبيراً"""
        patterns = await get_emotional_patterns(user_id, days=7)
        if patterns.get("patterns"):
            if "تدهور عاطفي يستحق الانتباه" in patterns["patterns"]:
                await store_reflection(
                    user_id=user_id,
                    insight_type="emotional_shift",
                    insight_text="يمر بتدهور عاطفي ملحوظ هذا الأسبوع",
                    confidence=0.9,
                )
                return {"type": "emotional_shift", "dominant": patterns.get("dominant_emotion")}
        return None

    async def _detect_business_pause(self, user_id: str) -> Optional[Dict]:
        """يكتشف إذا توقف المستخدم عن متابعة مشروعه"""
        # يمكن تتبع ذلك من خلال محادثات الأعمال (اختياري)
        return None


class ShadowScheduler:
    """مجدول وضع الظل - يعمل كل 6 ساعات"""
    async def start(self):
        logger.info("🌑 Shadow Mode Scheduler started")
        while True:
            await asyncio.sleep(21600)  # 6 ساعات
            # في الإصدار الحي، نمر على جميع المستخدمين النشطين
            logger.info("🌑 Running Shadow Analysis...")

shadow_engine = ShadowModeEngine()
logger.info("✅ Shadow Mode Engine initialized")
