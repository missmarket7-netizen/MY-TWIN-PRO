"""
Bloom Question Generator with AI - مولد أسئلة بمستويات بلوم
"""
import logging, random
from typing import Dict, Any, List

logger = logging.getLogger("bloom_generator")

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

BLOOM_LEVELS = {
    1: {"name_ar": "تذكُّر", "verbs_ar": ["اذكر", "عدد", "عرّف"]},
    2: {"name_ar": "فهم", "verbs_ar": ["اشرح", "لخص", "قارن"]},
    3: {"name_ar": "تطبيق", "verbs_ar": ["طبق", "استخدم", "حل"]},
    4: {"name_ar": "تحليل", "verbs_ar": ["حلل", "فرق", "استنتج"]},
    5: {"name_ar": "تقييم", "verbs_ar": ["قيّم", "انقد", "برر"]},
    6: {"name_ar": "إبداع", "verbs_ar": ["صمم", "أنشئ", "اخترع"]},
}

class BloomQuestionGenerator:
    def __init__(self):
        pass

    async def generate_question(
        self, concept: str, bloom_level: int = 1,
        age_group: str = "teen", language: str = "ar",
    ) -> Dict[str, Any]:
        level = BLOOM_LEVELS.get(bloom_level, BLOOM_LEVELS[1])
        verb = random.choice(level[f"verbs_{language}" if f"verbs_{language}" in level else "verbs_ar"])
        
        if AI_AVAILABLE:
            prompt = self._build_prompt(concept, verb, age_group, language)
            try:
                question_text = await provider_router.generate(prompt, language=language)
                if not question_text:
                    question_text = f"{verb} {concept}؟"
            except:
                question_text = f"{verb} {concept}؟"
        else:
            question_text = f"{verb} {concept}؟"
        
        return {
            "question": question_text, "bloom_level": bloom_level,
            "bloom_name": level.get("name_ar", ""), "verb_used": verb,
        }

    def _build_prompt(self, concept, verb, age_group, language):
        if language == "ar":
            return f"أنشئ سؤالاً واحداً بمستوى {verb} عن '{concept}' لطالب في مرحلة {age_group}. أجب بالسؤال فقط."
        return f"Create one question at the level of '{verb}' about '{concept}' for a {age_group} student. Answer with the question only."

bloom_gen = BloomQuestionGenerator()
logger.info("✅ Bloom Question Generator with AI initialized")
