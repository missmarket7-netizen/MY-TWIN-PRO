"""
CrossFeatureAnalyzer – العقل الجامع لكل الميزات
==================================================
يقرأ من جميع طبقات TCMA ومصادر البيانات ليكتشف الروابط بين أنشطة المستخدم.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except: DB_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import get_emotional_patterns
    from app.memory.reflection.reflection_engine import get_user_insights
    TCMA_AVAILABLE = True
except: TCMA_AVAILABLE = False

logger = logging.getLogger("cross_feature")

class CrossFeatureAnalyzer:
    async def analyze(self, user_id: str) -> Dict[str, Any]:
        insights = []
        if not DB_AVAILABLE: return {"insights": []}
        db = get_db()

        # 1. الدراسة vs الأعمال
        study = db.table("user_knowledge_state").select("updated_at").eq("user_id", user_id).order("updated_at", desc=True).limit(1).execute()
        business = db.table("raw_conversation_archive").select("created_at").eq("user_id", user_id).like("detected_intent", "%business%").order("created_at", desc=True).limit(1).execute()
        
        if study.data and business.data:
            study_date = study.data[0]["updated_at"]
            biz_date = business.data[0]["created_at"]
            diff = (datetime.fromisoformat(biz_date) - datetime.fromisoformat(study_date)).days
            if abs(diff) > 3:
                insights.append({
                    "type": "imbalance",
                    "message": f"تركز على {('الدراسة' if diff > 0 else 'الأعمال')} أكثر. هل تحتاج توازن؟"
                })

        # 2. العاطفة vs النشاط
        if TCMA_AVAILABLE:
            patterns = await get_emotional_patterns(user_id, days=7)
            dominant = patterns.get("dominant_emotion", "neutral")
            if dominant in ["sadness", "fear"]:
                insights.append({
                    "type": "emotional_impact",
                    "message": "لاحظت أنك تمر بفترة صعبة. هل تريد تقليل الضغط هذا الأسبوع؟"
                })

        return {"user_id": user_id, "cross_insights": insights}

analyzer = CrossFeatureAnalyzer()
logger.info("✅ CrossFeatureAnalyzer initialized")
