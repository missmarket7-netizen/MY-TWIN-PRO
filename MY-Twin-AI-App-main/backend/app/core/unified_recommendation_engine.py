"""
Unified Recommendation Engine v2.0 – محرك التوصيات الشامل
=============================================================
يحلل جميع طبقات TCMA والميزات (الدراسة، الأعمال، البرمجة، الأحلام، العلاقات)
ويقدم توصيات شخصية ذكية.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("recommendation_engine")

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import get_emotional_patterns, get_emotional_state_for_response
    TCMA_EMOTION_AVAILABLE = True
except ImportError:
    TCMA_EMOTION_AVAILABLE = False

try:
    from app.memory.reflection.reflection_engine import get_user_insights
    TCMA_REFLECTION_AVAILABLE = True
except ImportError:
    TCMA_REFLECTION_AVAILABLE = False

class UnifiedRecommendationEngine:
    async def get_daily_recommendation(self, user_id: str) -> Dict[str, Any]:
        recommendations = []

        # 1. توصيات عاطفية
        emotional_recs = await self._emotional_recommendations(user_id)
        recommendations.extend(emotional_recs)

        # 2. توصيات دراسية
        study_recs = await self._study_recommendations(user_id)
        recommendations.extend(study_recs)

        # 3. توصيات الأعمال
        business_recs = await self._business_recommendations(user_id)
        recommendations.extend(business_recs)

        # 4. توصيات البرمجة
        code_recs = await self._code_recommendations(user_id)
        recommendations.extend(code_recs)

        # 5. توصيات الأحلام
        dream_recs = await self._dream_recommendations(user_id)
        recommendations.extend(dream_recs)

        # 6. توصيات العلاقات
        rel_recs = await self._relationship_recommendations(user_id)
        recommendations.extend(rel_recs)

        # 7. توصيات عامة
        general_recs = await self._general_recommendations(user_id)
        recommendations.extend(general_recs)

        return {
            "user_id": user_id,
            "recommendations": recommendations[:5],  # أهم 5 توصيات
            "total": len(recommendations),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def _emotional_recommendations(self, user_id: str) -> List[Dict]:
        if not TCMA_EMOTION_AVAILABLE: return []
        try:
            patterns = await get_emotional_patterns(user_id, days=7)
            dominant = patterns.get("dominant_emotion", "neutral")
            recs = []
            if dominant == "frustration":
                recs.append({"type": "emotional_support", "message": "لاحظت أنك تمر بفترة صعبة. خذ استراحة، أو تحدث معي.", "action": "chat"})
            elif dominant == "joy":
                recs.append({"type": "momentum", "message": "أنت في حالة رائعة! هذا أفضل وقت للدراسة أو العمل على مشروعك.", "action": "study_or_business"})
            elif dominant == "fear":
                recs.append({"type": "reassurance", "message": "لا تقلق. أنا معك. جرب تمرين تنفس سريع.", "action": "life_coach"})
            return recs
        except: return []

    async def _study_recommendations(self, user_id: str) -> List[Dict]:
        if not DB_AVAILABLE: return []
        try:
            db = get_db()
            due = db.table("user_knowledge_state").select("concept_name").eq("user_id", user_id).lte("next_review_date", "now()").execute()
            if due.data:
                concepts = [c["concept_name"] for c in due.data[:3]]
                return [{"type": "study_reminder", "message": f"حان وقت مراجعة: {', '.join(concepts)}.", "action": "study"}]
        except: pass
        return []

    async def _business_recommendations(self, user_id: str) -> List[Dict]:
        # يمكن تتبع نشاط الأعمال من المحادثات أو جدول المشاريع
        return []

    async def _code_recommendations(self, user_id: str) -> List[Dict]:
        # يمكن تتبع مشاريع البرمجة النشطة
        return []

    async def _dream_recommendations(self, user_id: str) -> List[Dict]:
        if not TCMA_REFLECTION_AVAILABLE: return []
        try:
            insights = await get_user_insights(user_id, min_confidence=0.5)
            dream_insights = [i for i in insights.get("insights", []) if i.get("type") == "dream"]
            if dream_insights:
                return [{"type": "dream_reflection", "message": "حلمك الأخير يحمل رموزاً مثيرة. هل تريد مناقشته؟", "action": "dreams"}]
        except: pass
        return []

    async def _relationship_recommendations(self, user_id: str) -> List[Dict]:
        if not DB_AVAILABLE: return []
        try:
            db = get_db()
            rel = db.table("relationship_memory").select("trust,openness").eq("user_id", user_id).order("created_at", desc=True).limit(2).execute()
            if rel.data and len(rel.data) >= 2:
                if rel.data[0]["trust"] > rel.data[1]["trust"] + 10:
                    return [{"type": "relationship_growth", "message": "علاقتنا تتحسن بشكل رائع! استمر في مشاركتي.", "action": "chat"}]
        except: pass
        return []

    async def _general_recommendations(self, user_id: str) -> List[Dict]:
        hour = datetime.now(timezone.utc).hour + 3  # توقيت السعودية
        recs = []
        if 5 <= hour < 9:
            recs.append({"type": "morning_routine", "message": "صباح الخير! كيف يمكنني مساعدتك في بدء يومك؟", "action": "chat"})
        elif 21 <= hour or hour < 3:
            recs.append({"type": "evening_reflection", "message": "وقت التأمل. كيف كان يومك؟", "action": "chat"})
        return recs

engine = UnifiedRecommendationEngine()
logger.info("✅ Unified Recommendation Engine v2.0 initialized")
