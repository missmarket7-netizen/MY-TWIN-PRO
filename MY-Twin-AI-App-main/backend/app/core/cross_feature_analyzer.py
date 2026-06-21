"""
CrossFeatureAnalyzer v2.0 – العقل الجامع لكل الميزات
=========================================================
يربط بين الدراسة، الأعمال، البرمجة، الأحلام، والعلاقات.
يكتشف أنماطاً غير مرئية عبر جميع أنشطة المستخدم.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import get_emotional_patterns
    from app.memory.reflection.reflection_engine import get_user_insights
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("cross_feature")

class CrossFeatureAnalyzer:
    async def analyze(self, user_id: str) -> Dict[str, Any]:
        insights = []
        if not DB_AVAILABLE:
            return {"insights": [], "summary": "قاعدة البيانات غير متاحة"}

        db = get_db()

        # 1. الدراسة vs الأعمال (توازن)
        study_insight = await self._analyze_study_business_balance(db, user_id)
        if study_insight:
            insights.append(study_insight)

        # 2. البرمجة vs المحتوى (إبداع)
        code_insight = await self._analyze_code_content_balance(db, user_id)
        if code_insight:
            insights.append(code_insight)

        # 3. العاطفة وتأثيرها على الإنتاجية
        emotion_insight = await self._analyze_emotion_productivity(user_id)
        if emotion_insight:
            insights.append(emotion_insight)

        # 4. الأحلام وتأثيرها على المزاج
        dream_insight = await self._analyze_dreams_mood(user_id)
        if dream_insight:
            insights.append(dream_insight)

        # 5. العلاقات والدعم الاجتماعي
        rel_insight = await self._analyze_relationships_support(db, user_id)
        if rel_insight:
            insights.append(rel_insight)

        return {
            "user_id": user_id,
            "cross_insights": insights,
            "total": len(insights),
            "summary": self._generate_summary(insights)
        }

    async def _analyze_study_business_balance(self, db, user_id: str) -> Dict:
        try:
            study = db.table("user_knowledge_state").select("updated_at").eq("user_id", user_id).order("updated_at", desc=True).limit(1).execute()
            business = db.table("raw_conversation_archive").select("created_at").eq("user_id", user_id).like("detected_intent", "%business%").order("created_at", desc=True).limit(1).execute()
            if study.data and business.data:
                s_date = datetime.fromisoformat(study.data[0]["updated_at"])
                b_date = datetime.fromisoformat(business.data[0]["created_at"])
                diff = abs((b_date - s_date).days)
                if diff > 3:
                    focus = "الدراسة" if s_date > b_date else "الأعمال"
                    return {"type": "life_balance", "message": f"تركيزك منصب على {focus} مؤخراً. توازن أفضل؟", "action": "suggest_balance"}
        except: pass
        return None

    async def _analyze_code_content_balance(self, db, user_id: str) -> Dict:
        # يمكن تتبعه من سجلات CODE LAB و CREATOR
        return None

    async def _analyze_emotion_productivity(self, user_id: str) -> Dict:
        if not TCMA_AVAILABLE: return None
        try:
            patterns = await get_emotional_patterns(user_id, days=7)
            dominant = patterns.get("dominant_emotion", "neutral")
            if dominant in ["sadness", "fear"]:
                return {"type": "emotional_impact", "message": "مشاعرك تؤثر على إنتاجيتك هذا الأسبوع. خذ استراحة.", "action": "life_coach"}
            elif dominant == "joy":
                return {"type": "emotional_boost", "message": "أنت في قمة طاقتك! استغلها في مشاريعك.", "action": "suggest_action"}
        except: pass
        return None

    async def _analyze_dreams_mood(self, user_id: str) -> Dict:
        if not TCMA_AVAILABLE: return None
        try:
            insights = await get_user_insights(user_id, min_confidence=0.5)
            dreams = [i for i in insights.get("insights", []) if i.get("type") == "dream"]
            if len(dreams) >= 3:
                return {"type": "dream_pattern", "message": "أحلامك المتكررة تحمل رسالة. هل نناقشها؟", "action": "dreams"}
        except: pass
        return None

    async def _analyze_relationships_support(self, db, user_id: str) -> Dict:
        try:
            people = db.table("person_nodes").select("name,importance_score").eq("user_id", user_id).gte("importance_score", 60).execute()
            if people.data:
                return {"type": "social_support", "message": f"لديك {len(people.data)} أشخاص مقربين. تواصل معهم هذا الأسبوع.", "action": "social"}
        except: pass
        return None

    def _generate_summary(self, insights: List[Dict]) -> str:
        if not insights:
            return "كل شيء متوازن. استمر!"
        types = [i["type"] for i in insights]
        if "emotional_impact" in types:
            return "اهتم بصحتك النفسية هذا الأسبوع."
        if "life_balance" in types:
            return "حاول موازنة وقتك بين أولوياتك."
        return "لديك بعض الملاحظات. راجعها."

analyzer = CrossFeatureAnalyzer()
logger.info("✅ CrossFeatureAnalyzer v2.0 initialized")
