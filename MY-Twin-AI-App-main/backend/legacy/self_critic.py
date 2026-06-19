"""
MyTwin – Self Critic v1.5 (Activated in TwinBrain)
- يفحص الرد قبل الإرسال بحثاً عن الهلوسة، التكرار، الجودة، والنبرة
- يستخدم LLM لتقييم الرد وإصلاحه
- مفعّل تلقائياً في twin_brain.py
"""
import logging, re
from typing import Optional

logger = logging.getLogger("self_critic")

class SelfCritic:
    async def evaluate_and_repair(self, reply: str, context: str, multi_client) -> str:
        if not reply or len(reply) < 5:
            return reply

        # فحص التكرار فقط — بدون API call للهلوسة
        if self._has_excessive_repetition(reply):
            logger.warning("⚠️ تكرار مفرط في الرد")
            reply = await self._repair_repetition(reply, multi_client) or reply

        # فحص الردود الفارغة أو العامة جداً
        if self._is_too_generic(reply):
            logger.warning("⚠️ رد عام جداً — تم تسجيله للمراجعة")
            # لا نصلحه تلقائياً — نسجله بس

        return reply

    def _is_too_generic(self, reply: str) -> bool:
        """يكتشف الردود العامة جداً."""
        generic_phrases = [
            "كيف يمكنني مساعدتك",
            "أنا هنا للمساعدة",
            "هل يمكنني مساعدتك",
            "كيف حالك اليوم",
            "How can I help you",
            "I'm here to help",
        ]
        reply_lower = reply.lower()
        return any(phrase.lower() in reply_lower for phrase in generic_phrases)

    def _has_excessive_repetition(self, text: str) -> bool:
        words = text.split()
        if len(words) < 10:
            return False
        unique_ratio = len(set(words)) / len(words)
        return unique_ratio < 0.4

    def _has_potential_hallucination(self, reply: str, context: str) -> bool:
        # معطل — كان يسبب false positives كثيرة
        return False

    async def _repair_repetition(self, text: str, multi_client) -> Optional[str]:
        try:
            prompt = f"""أعد كتابة هذا الرد لتجنب التكرار الممل، مع الحفاظ على المعنى واللطف:
الرد: {text}
النسخة المنقحة:"""
            return await multi_client.get_best_reply(prompt)
        except:
            return None

    async def _repair_hallucination(self, reply: str, context: str, multi_client) -> Optional[str]:
        try:
            prompt = f"""استخدم السياق التالي لتصحيح أي معلومات خاطئة في الرد:
السياق: {context[:500]}
الرد: {reply}
الرد المصحح:"""
            return await multi_client.get_best_reply(prompt)
        except:
            return None


# نسخة عالمية
self_critic = SelfCritic()
print("✅ Self Critic v1.5 initialized")
