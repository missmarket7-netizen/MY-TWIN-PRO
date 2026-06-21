"""
Proactive Engine v2.0 – التوأم الحي الذي يتحدث أولاً
=======================================================
يولد إشعارات وتوصيات استباقية بناءً على كل طبقات TCMA.
يتكامل مع المحركات الجديدة (الظل، الزمان، التوصيات).
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

try:
    from app.memory.emotional.emotional_memory import get_emotional_patterns
    from app.memory.identity.identity_model import get_identity
    from app.memory.relationship.relationship_memory import get_relationship_insights
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

try:
    from app.core.unified_recommendation_engine import engine as rec_engine
    REC_AVAILABLE = True
except ImportError:
    REC_AVAILABLE = False

try:
    from app.features.temporal_context import temporal_engine
    TEMP_AVAILABLE = True
except ImportError:
    TEMP_AVAILABLE = False

logger = logging.getLogger("proactive_engine")

class ProactiveEngine:
    """يولد رسائل استباقية مخصصة"""

    async def generate_proactive_message(self, user_id: str, lang: str = "ar") -> Dict[str, Any]:
        """الرسالة الاستباقية الرئيسية لليوم"""
        messages = []
        
        # 1. تحية زمنية
        if TEMP_AVAILABLE:
            ctx = temporal_engine.get_current_context(user_id)
            messages.append(ctx["greeting"])
        
        # 2. توصية من المحرك الموحّد
        if REC_AVAILABLE:
            recs = await rec_engine.get_daily_recommendation(user_id)
            for rec in recs.get("recommendations", [])[:2]:
                messages.append(rec["message"])
        
        # 3. تذكير دراسي
        if TEMP_AVAILABLE:
            study_ctx = await temporal_engine.get_study_reminder_context(user_id)
            if study_ctx:
                messages.append(study_ctx)
        
        # 4. ملاحظة عاطفية
        if TCMA_AVAILABLE:
            patterns = await get_emotional_patterns(user_id, days=3)
            dominant = patterns.get("dominant_emotion", "neutral")
            if dominant in ["sadness", "fear"]:
                messages.append("أنا هنا من أجلك 💜")
            elif dominant == "joy":
                messages.append("أرى أنك في مزاج رائع! استمر 🎉")
        
        return {
            "message": " ".join(messages),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "send_notification": True
        }

    async def get_context_for_response(self, user_id: str, current_message: str) -> Dict[str, Any]:
        """يضيف السياق الاستباقي إلى ردود المحادثة"""
        context_additions = []
        
        if TEMP_AVAILABLE:
            ctx = temporal_engine.get_current_context(user_id)
            context_additions.append(f"الوقت: {ctx['time_of_day']} | {ctx['day_type']}")
        
        if TCMA_AVAILABLE:
            rel = await get_relationship_insights(user_id)
            if rel.get("insights"):
                context_additions.append(f"العلاقة: {rel['insights'][0]}")
        
        return {"context_additions": context_additions}

proactive_engine = ProactiveEngine()
logger.info("✅ Proactive Engine v2.0 initialized")
