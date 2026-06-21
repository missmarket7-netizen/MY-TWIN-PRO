"""
Meta-Reflection Engine – وعي التوأم بنفسه
=============================================
يحلل علاقة المستخدم بالتوأم نفسه.
يكتشف إذا كان المستخدم يبتعد، يفقد الثقة، أو يتغير سلوكه تجاه التوأم.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

try:
    from app.memory.relationship.relationship_memory import get_relationship_context_for_response
    from app.memory.relationship.attachment_model import detect_attachment_style
    from app.memory.emotional.emotional_memory import get_emotional_patterns
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("meta_reflection")

class MetaReflectionEngine:
    """يحلل علاقة المستخدم بالتوأم"""

    async def analyze_relationship_health(self, user_id: str) -> Dict[str, Any]:
        """تحليل صحة العلاقة بين المستخدم والتوأم"""
        if not TCMA_AVAILABLE:
            return {"status": "unavailable"}

        insights = []
        concerns = []

        # 1. تحليل الثقة والانفتاح
        rel = await get_relationship_context_for_response(user_id, "")
        trust = rel.get("relationship", {}).get("trust", 50)
        openness = rel.get("relationship", {}).get("openness", 50)
        trend = rel.get("relationship", {}).get("trend", "stable")

        if trend == "declining":
            concerns.append("الثقة تتراجع. يجب أن أكون أكثر دعماً.")
        elif trend == "improving":
            insights.append("الثقة في نمو. يمكنني التعمق أكثر في المحادثات.")

        # 2. تحليل نمط التعلق
        attachment = await detect_attachment_style(user_id)
        style = attachment.get("style", "unknown")
        if style == "avoidant":
            insights.append("المستخدم يتجنب العلاقة العميقة. سأحترم مساحته.")
        elif style == "anxious":
            insights.append("المستخدم يحتاج طمأنة مستمرة. سأكون أكثر حضوراً.")

        # 3. تحليل تكرار الاستخدام
        # (يمكن حسابه من عدد المحادثات في الأسبوع)

        return {
            "trust_level": trust,
            "openness_level": openness,
            "trend": trend,
            "attachment_style": style,
            "insights": insights,
            "concerns": concerns,
            "self_instruction": self._generate_self_instruction(style, trend)
        }

    def _generate_self_instruction(self, attachment_style: str, trend: str) -> str:
        """يولد تعليمات للتوأم نفسه بناءً على التحليل"""
        if trend == "declining":
            return "كن أكثر استماعاً وأقل نصحاً. ركز على المشاعر."
        if attachment_style == "avoidant":
            return "لا تضغط. حافظ على مسافة آمنة. كن متاحاً دون إلحاح."
        if attachment_style == "anxious":
            return "طمئن المستخدم. أكد له أنك هنا. كن ثابتاً."
        return "استمر في بناء العلاقة بشكل طبيعي."

meta_engine = MetaReflectionEngine()
logger.info("✅ Meta-Reflection Engine initialized")
