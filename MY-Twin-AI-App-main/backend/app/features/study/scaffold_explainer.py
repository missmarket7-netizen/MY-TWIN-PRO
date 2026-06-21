"""
S.C.A.F.F.O.L.D. Explainer with AI Integration
================================================
يستخدم مزود الذكاء الاصطناعي لتوليد شرح حقيقي متكيف.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("scaffold_explainer")

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class ScaffoldExplainer:
    def __init__(self):
        pass

    async def explain(
        self, concept: str, student_profile: Dict[str, Any],
        age_group: str = "teen", language: str = "ar",
        current_emotion: str = "neutral", depth: int = 1,
    ) -> Dict[str, Any]:
        # بناء الموجه للذكاء الاصطناعي
        prompt = self._build_prompt(concept, student_profile, age_group, language, current_emotion, depth)
        
        explanation = {
            "simplified": "", "connection": "", "analogy": "",
            "fragments": [], "check_question": "", "emotion_note": "", "ladder_hint": "",
        }
        
        if AI_AVAILABLE:
            try:
                response = await provider_router.generate(prompt, language=language)
                # محاولة تحليل الاستجابة المنظمة
                # هنا سنفترض أن الذكاء الاصطناعي يعيد JSON أو نص منظم
                if response:
                    explanation["simplified"] = response
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
        
        # ملاحظة عاطفية (تتم محلياً)
        notes = {
            "frustration": {"ar": "أشعر أنك مجتهد. دعنا نأخذها خطوة بخطوة 💪", "en": "Let's take it step by step 💪"},
            "confident": {"ar": "ممتاز! دعنا نستغل حماسك! 🎯", "en": "Great! Let's use this energy! 🎯"},
        }
        explanation["emotion_note"] = notes.get(current_emotion, {}).get(language, "")
        
        return explanation
    
    def _build_prompt(self, concept, profile, age_group, language, emotion, depth):
        people = profile.get("important_people", [])
        traits = profile.get("identity_traits", [])
        
        if language == "ar":
            prompt = f"""
أنت معلم خبير في شرح المفاهيم للطلاب.
قم بشرح مفهوم "{concept}" لطالب في مرحلة {age_group}.
استخدم أسلوب S.C.A.F.F.O.L.D:
1. بسّط المفهوم في جملة واحدة.
2. اربطه بحياة الطالب. (مثلاً: صديقه {people[0]['name'] if people else 'شخص يعرفه'})
3. قدم تشبيهاً من عالم الطالب (مثلاً: {traits[0] if traits else 'التكنولوجيا'}).
4. قسمه إلى 3-5 أجزاء صغيرة.
5. اطرح سؤالاً للتحقق من الفهم.
6. لاحظ أن الطالب يشعر بـ {emotion} وتكيف معه.
7. قدم تلميحاً للتعمق أو إعادة الشرح.
أجب بالعربية الفصحى المبسطة.
"""
        else:
            prompt = f"""
You are an expert teacher explaining concepts to students.
Explain "{concept}" to a {age_group} student using the S.C.A.F.F.O.L.D method.
Include: Simplified definition, personal connection, analogy, fragments, check question, emotional note for {emotion}, and ladder hint.
Respond in English.
"""
        return prompt

scaffold = ScaffoldExplainer()
logger.info("✅ S.C.A.F.F.O.L.D. Explainer with AI initialized")
