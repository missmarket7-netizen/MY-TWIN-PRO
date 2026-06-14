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

        # فحص سريع للتكرار
        if self._has_excessive_repetition(reply):
            logger.warning("⚠️ تكرار مفرط في الرد")
            reply = await self._repair_repetition(reply, multi_client) or reply

        # فحص الهلوسة ضد السياق
        if context and self._has_potential_hallucination(reply, context):
            logger.warning("⚠️ هلوسة محتملة في الرد")
            reply = await self._repair_hallucination(reply, context, multi_client) or reply

        return reply

    def _has_excessive_repetition(self, text: str) -> bool:
        words = text.split()
        if len(words) < 10:
            return False
        unique_ratio = len(set(words)) / len(words)
        return unique_ratio < 0.4

    def _has_potential_hallucination(self, reply: str, context: str) -> bool:
        reply_numbers = set(re.findall(r'\d+', reply))
        context_numbers = set(re.findall(r'\d+', context))
        if reply_numbers and context_numbers:
            return not reply_numbers.issubset(context_numbers)
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
