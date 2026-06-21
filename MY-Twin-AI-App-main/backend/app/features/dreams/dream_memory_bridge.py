"""
Dream-Memory Bridge – جسر التكامل بين الأحلام والذاكرة
===========================================================
يربط كل حلم بـ:
- الذاكرة العاطفية
- الاستنتاجات
- الرسم البياني للذاكرة
- التوصيات الموحدة
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_patterns
    from app.memory.reflection.reflection_engine import store_reflection, get_user_insights
    from app.memory.graph.memory_graph import auto_create_edges_from_memory, get_memory_cluster
    from app.memory.identity.identity_model import get_identity
    from app.memory.relationship.person_node import get_person_network
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("dream_memory_bridge")

class DreamMemoryBridge:
    """يربط الأحلام بجميع طبقات TCMA"""

    async def store_dream(
        self,
        user_id: str,
        dream_text: str,
        analysis: Dict[str, Any],
        lang: str = "ar"
    ) -> str:
        """
        يخزن الحلم في الذاكرة ويعيد معرف الذاكرة العاطفية.
        """
        if not TCMA_AVAILABLE:
            return ""

        try:
            emotions = analysis.get("emotions", ["neutral"])
            primary_emotion = emotions[0] if emotions else "neutral"

            # 1. تخزين عاطفة
            emo_result = await store_emotional_memory(
                user_id=user_id,
                expressed_text=dream_text[:300],
                detected_emotion={
                    "primary": primary_emotion,
                    "intensity": 0.8,
                    "valence": 0.2 if primary_emotion in ["فرح", "joy"] else -0.3
                },
                trigger="dream",
                cultural_context="تفسير حلم"
            )
            emo_id = emo_result.get("id") if emo_result else ""

            # 2. إضافة استنتاج
            symbols = analysis.get("symbols_analysis", [])
            if symbols:
                await store_reflection(
                    user_id=user_id,
                    insight_type="dream",
                    insight_text=f"حلم يتضمن رموز: {', '.join(symbols[:3])}",
                    confidence=0.7,
                    related_emotion=primary_emotion,
                    language=lang
                )

            # 3. ربط بالرسم البياني
            if emo_id:
                await auto_create_edges_from_memory(
                    user_id=user_id,
                    memory_id=emo_id,
                    memory_type="emotional_memory",
                    memory_data={"trigger": "dream", "symbols": symbols}
                )

            logger.info(f"🌙 حلم مخزن في TCMA: {emo_id}")
            return emo_id

        except Exception as e:
            logger.error(f"فشل تخزين الحلم في TCMA: {e}")
            return ""

    async def get_dream_context(self, user_id: str) -> Dict[str, Any]:
        """
        يجمع سياق الأحلام السابقة للمستخدم من TCMA.
        """
        context = {"previous_dreams": 0, "recurring_symbols": [], "emotional_pattern": "neutral"}

        if not TCMA_AVAILABLE:
            return context

        try:
            # جلب الأنماط العاطفية
            patterns = await get_emotional_patterns(user_id, days=30)
            context["emotional_pattern"] = patterns.get("dominant_emotion", "neutral")

            # جلب الاستنتاجات المتعلقة بالأحلام
            insights = await get_user_insights(user_id, min_confidence=0.5)
            dream_insights = [
                i for i in insights.get("insights", [])
                if i.get("type") == "dream"
            ]
            context["previous_dreams"] = len(dream_insights)
            context["recurring_symbols"] = [
                i["text"] for i in dream_insights[:5]
            ]

        except Exception as e:
            logger.error(f"فشل جلب سياق الأحلام: {e}")

        return context

    async def link_to_identity(self, user_id: str, dream_text: str, analysis: Dict) -> None:
        """
        يربط الحلم بنموذج هوية المستخدم.
        مثال: إذا كان الحلم يتكرر عن الطيران، قد يعني طموحاً عالياً.
        """
        if not TCMA_AVAILABLE:
            return

        try:
            identity = await get_identity(user_id)
            if identity:
                # يمكن إضافة منطق لتحليل ارتباط الأحلام بالهوية
                # مثال: أحلام متكررة عن السقوط ← صراع مع الفشل
                pass
        except Exception as e:
            logger.error(f"فشل ربط الحلم بالهوية: {e}")

    async def link_to_social_network(self, user_id: str, dream_text: str) -> List[str]:
        """
        يكتشف إذا كان الحلم يذكر أشخاصاً من شبكة المستخدم.
        """
        if not TCMA_AVAILABLE:
            return []

        try:
            network = await get_person_network(user_id, min_importance=40)
            mentioned = []
            for person in network:
                if person.get("name", "") in dream_text:
                    mentioned.append(person["name"])
            return mentioned
        except:
            return []


# نسخة عالمية
dream_bridge = DreamMemoryBridge()
logger.info("✅ Dream-Memory Bridge initialized")
