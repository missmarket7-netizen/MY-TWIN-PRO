"""
Unified Recommendation Engine – محرك التوصيات الموحّد
=========================================================
يحلل كل طبقات الذاكرة والميزات، ويقدم توصيات شخصية.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("recommendation_engine")

class UnifiedRecommendationEngine:
    """يجمع بيانات المستخدم من كل المصادر ويقدم توصيات"""
    
    async def get_daily_recommendation(self, user_id: str) -> Dict[str, Any]:
        """توصية يومية مخصصة بناءً على كل شيء"""
        recommendations = []
        
        # 1. تحليل العاطفة الحالية
        try:
            from app.memory.emotional.emotional_memory import get_emotional_patterns
            emotional = await get_emotional_patterns(user_id, days=3)
            dominant = emotional.get("dominant_emotion", "neutral")
            
            if dominant == "frustration":
                recommendations.append({
                    "type": "emotional_support",
                    "message": "لاحظت أنك تمر بيوم صعب. خذ استراحة، أو تحدث معي عن أي شيء.",
                    "action": "chat"
                })
            elif dominant == "joy":
                recommendations.append({
                    "type": "momentum",
                    "message": "أنت في حالة رائعة! هذا أفضل وقت للدراسة أو العمل على مشروعك.",
                    "action": "study_or_business"
                })
        except: pass
        
        # 2. تحليل التقدم الدراسي
        try:
            from app.infrastructure.database.supabase_client import get_db
            db = get_db()
            due = db.table("user_knowledge_state").select("concept_name").eq("user_id", user_id).lte("next_review_date", "now()").execute()
            if due.data:
                concepts = [c["concept_name"] for c in due.data[:3]]
                recommendations.append({
                    "type": "study_reminder",
                    "message": f"حان وقت مراجعة: {', '.join(concepts)}. بضع دقائق الآن توفر ساعات لاحقاً.",
                    "action": "study"
                })
        except: pass
        
        # 3. تحليل الاستنتاجات
        try:
            from app.memory.reflection.reflection_engine import get_user_insights
            insights = await get_user_insights(user_id, min_confidence=0.7)
            if insights.get("insights"):
                top_insight = insights["insights"][0]["text"]
                recommendations.append({
                    "type": "insight",
                    "message": f"لاحظت عنك: {top_insight}",
                    "action": "reflect"
                })
        except: pass
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total": len(recommendations)
        }

engine = UnifiedRecommendationEngine()
logger.info("✅ Unified Recommendation Engine initialized")
