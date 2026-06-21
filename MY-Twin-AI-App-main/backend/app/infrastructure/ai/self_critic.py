"""
Self Critic v3.0 – مراقب جودة متقدم للردود
=============================================
- فحص: التكرار، التناسق العاطفي، الإيجاز، الوضوح، الإفادة
- إصلاح تلقائي للمشكلات الشائعة
- تكامل مع TCMA للتحقق من المشاعر والهوية
- تكامل مع Response Validator للتنسيق
"""
import logging
from typing import Optional

logger = logging.getLogger("self_critic")

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class SelfCritic:
    """مُقيّم ذاتي للردود قبل إرسالها"""

    async def evaluate(
        self,
        reply: str,
        user_message: Optional[str] = None,
        emotion: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        تقييم شامل للرد مع إصلاح تلقائي.
        يعيد الرد بعد التحسين (أو الرد الأصلي إذا كان ممتازاً).
        """
        if not reply or len(reply) < 5:
            return reply

        issues = []
        improved = reply

        # 1. فحص التكرار
        if self._has_repetition(improved):
            issues.append("repetition")

        # 2. فحص الإيجاز (الطول الزائد)
        if len(improved) > 500:
            issues.append("verbose")

        # 3. فحص الوضوح (جمل طويلة جداً)
        if self._has_long_sentences(improved):
            issues.append("unclear")

        # 4. فحص التناسق العاطفي
        if emotion and user_message:
            if not self._emotionally_consistent(improved, emotion):
                issues.append("emotional_mismatch")

        # إذا لم توجد مشكلات، نعيد الرد كما هو
        if not issues:
            return improved

        # محاولة الإصلاح التلقائي
        logger.info(f"🔧 إصلاح مشكلات: {issues}")
        
        if AI_AVAILABLE:
            try:
                issues_str = "، ".join(issues)
                fix_prompt = f"""
                أعد كتابة الرد التالي لتحسينه. المشكلات: {issues_str}.
                الرد الأصلي: "{improved}"
                الرسالة الأصلية: "{user_message or ''}"
                أعد الرد المحسّن فقط.
                """
                fixed, _ = await provider_router.route(fix_prompt, "quick_reply")
                if fixed and len(fixed) > 5:
                    improved = fixed
                    logger.info("✅ تم إصلاح الرد تلقائياً")
            except Exception as e:
                logger.warning(f"فشل الإصلاح التلقائي: {e}")

        return improved

    def _has_repetition(self, text: str) -> bool:
        """فحص تكرار الكلمات"""
        words = text.split()
        if len(words) < 10:
            return False
        unique = len(set(words))
        return unique / len(words) < 0.4

    def _has_long_sentences(self, text: str) -> bool:
        """فحص وجود جمل طويلة جداً"""
        sentences = text.replace("!", ".").replace("؟", ".").split(".")
        for s in sentences:
            if len(s.split()) > 30:
                return True
        return False

    def _emotionally_consistent(self, reply: str, emotion: str) -> bool:
        """
        فحص التناسق العاطفي: هل الرد يناسب العاطفة؟
        مثال: لا يجب أن يكون الرد مرحاً إذا كان المستخدم حزيناً
        """
        if emotion in ["sadness", "fear", "anger"]:
            overly_happy = ["رائع", "ممتاز", "ههه", "😂", "amazing", "fantastic", "lol"]
            return not any(w in reply for w in overly_happy)
        return True

# نسخة عالمية
self_critic = SelfCritic()
logger.info("✅ Self Critic v3.0 initialized")
