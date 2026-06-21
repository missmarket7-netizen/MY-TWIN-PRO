"""
L.I.F.E. C.O.A.C.H. v3.0 – مدرب الحياة المتكامل
=====================================================
فريق من 3 متخصصين + تكامل عميق مع TCMA.
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("life_coach_v3")

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from app.memory.identity.identity_model import get_identity
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response, store_emotional_memory
    from app.memory.reflection.reflection_engine import process_message_for_reflections
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

# ============================================================
# المعالج السلوكي المعرفي (CBT)
# ============================================================
class CognitiveBehavioralTherapist:
    async def analyze(self, text: str, profile: Dict, lang: str) -> Dict[str, Any]:
        if not AI_AVAILABLE:
            return {"intervention": "أنا هنا لأستمع إليك. كيف يمكنني مساعدتك؟"}
        
        emotion = profile.get("emotion", "neutral")
        prompt = f"""
أنت معالج سلوكي معرفي (CBT). العميل يتحدث عن: "{text}".
حالته الحالية: {emotion}. صفاته: {', '.join(profile.get('traits', []))}.

اتبع الخطوات:
1. استمع وتفهم (Empathy)
2. حدد نمط التفكير السلبي (Cognitive Distortion)
3. تحدى الفكرة بلطف
4. قدم تمريناً عملياً للأسبوع
اللغة: {lang}.
"""
        intervention = await provider_router.generate(prompt, language=lang)
        return {"intervention": intervention, "method": "CBT"}

# ============================================================
# أخصائي التغذية
# ============================================================
class Nutritionist:
    def create_plan(self, goal: str, restrictions: str, lang: str) -> Dict[str, Any]:
        plans = {
            "فقدان دهون": {"daily_calories": "1800-2000", "meals": [{"name": "فطور", "suggestion": "شوفان + بيض"}, {"name": "غداء", "suggestion": "صدر دجاج + خضار"}, {"name": "عشاء", "suggestion": "زبادي + مكسرات"}]},
            "بناء عضلات": {"daily_calories": "2500-2800", "meals": [{"name": "فطور", "suggestion": "عجة + خبز أسمر"}, {"name": "غداء", "suggestion": "لحم + أرز + خضار"}, {"name": "عشاء", "suggestion": "تونة + سلطة"}]},
            "تحسين صحة": {"daily_calories": "2000-2200", "meals": [{"name": "فطور", "suggestion": "فواكه + زبادي"}, {"name": "غداء", "suggestion": "سمك + كينوا"}, {"name": "عشاء", "suggestion": "شوربة خضار"}]},
        }
        return plans.get(goal, plans["تحسين صحة"])

# ============================================================
# المدرب الرياضي
# ============================================================
class FitnessCoach:
    def create_plan(self, goal: str, level: str, equipment: str, lang: str) -> Dict[str, Any]:
        plans = {
            "beginner": {"weekly_schedule": [{"day": "السبت", "workout": "مشي 30 دقيقة"}, {"day": "الاثنين", "workout": "تمارين وزن الجسم (10 دقائق)"}, {"day": "الأربعاء", "workout": "يوغا خفيفة"}]},
            "intermediate": {"weekly_schedule": [{"day": "السبت", "workout": "جري 5 كم"}, {"day": "الاثنين", "workout": "تمارين مقاومة (30 دقيقة)"}, {"day": "الأربعاء", "workout": "HIIT (20 دقيقة)"}]},
        }
        return plans.get(level, plans["beginner"])

# ============================================================
# المايسترو
# ============================================================
class LifeCoachOrchestrator:
    def __init__(self):
        self.cbt = CognitiveBehavioralTherapist()
        self.nutritionist = Nutritionist()
        self.fitness = FitnessCoach()

    async def build_client_profile(self, user_id: str) -> Dict[str, Any]:
        if not TCMA_AVAILABLE: return {}
        try:
            identity = await get_identity(user_id)
            emotion = await get_emotional_state_for_response(user_id, "")
            return {
                "traits": identity.get("traits", []) if identity else [],
                "emotion": emotion.get("current_emotion", "neutral") if emotion else "neutral"
            }
        except: return {}

    async def start_session(self, user_id: str, topic: str, lang: str = "ar") -> Dict[str, Any]:
        profile = await self.build_client_profile(user_id)
        analysis = await self.cbt.analyze(topic, profile, lang)
        
        if TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=topic,
                detected_emotion={"primary": profile.get("emotion", "neutral"), "intensity": 0.8, "valence": 0.1},
                trigger="life_coaching"
            )
            await process_message_for_reflections(
                user_id=user_id, message=f"جلسة حياة: {topic[:50]}",
                language=lang, detected_emotion=profile.get("emotion", "neutral")
            )
        
        return {
            "profile_summary": profile,
            "psychological_analysis": analysis,
            "coach_reply": analysis.get("intervention", "سأكون هنا لدعمك.")
        }

    async def get_nutrition_plan(self, user_id: str, goal: str, restrictions: str = "", lang: str = "ar") -> Dict[str, Any]:
        plan = self.nutritionist.create_plan(goal, restrictions, lang)
        if TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=f"طلب خطة تغذية: {goal}",
                detected_emotion={"primary": "motivated", "intensity": 0.8, "valence": 0.7},
                trigger="nutrition_plan"
            )
        return {"goal": goal, "plan": plan}

    async def get_fitness_plan(self, user_id: str, goal: str, level: str = "beginner", equipment: str = "none", lang: str = "ar") -> Dict[str, Any]:
        plan = self.fitness.create_plan(goal, level, equipment, lang)
        if TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=f"طلب خطة تمارين: {goal}",
                detected_emotion={"primary": "motivated", "intensity": 0.8, "valence": 0.7},
                trigger="fitness_plan"
            )
        return {"goal": goal, "plan": plan}

life_coach = LifeCoachOrchestrator()
logger.info("✅ L.I.F.E. C.O.A.C.H. v3.0 Production Ready")
