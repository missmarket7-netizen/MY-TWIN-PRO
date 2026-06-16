"""
MyTwin – Adaptive Sparse LLM Council v4.1 (Deep Integration)
- 80% Groq مباشر، 15% Generator + Critic، 5% مجلس كامل
- متكامل بعمق مع twin_brain.py و prompt_builder.py
- إصلاح جميع الفجوات: التوقيع، إهدار الـ API، الحدود اليومية
"""
import logging, asyncio, time, os, re
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger("llm_council")

class LLMCouncil:
    def __init__(self, multi_client):
        self.multi = multi_client
        self.daily_council_uses = 0
        self.daily_simple_uses = 0
        self._last_reset_day = time.strftime("%Y-%m-%d")

        # حدود ديناميكية
        self.max_daily_council = int(os.getenv("COUNCIL_MAX_DAILY", "50"))
        self.max_daily_simple = int(os.getenv("SIMPLE_MAX_DAILY", "500"))

        # أدوار المجلس
        self.roles = {
            "planner": ["gemini", "groq"],
            "generator": ["gemini", "groq"],
            "critic": ["gemini", "groq"],
            "repair": ["groq", "gemini"],
        }

    def _reset_daily_counters_if_new_day(self):
        today = time.strftime("%Y-%m-%d")
        if today != self._last_reset_day:
            self.daily_council_uses = 0
            self.daily_simple_uses = 0
            self._last_reset_day = today
            logger.info("🔄 تم إعادة تعيين عدادات المجلس اليومية")

    # ✅ إصلاح الفجوة 1: توقيع الدالة متوافق تمامًا مع twin_brain.py
    async def get_best_reply(
        self, prompt: str, task_type: str = "general",
        emotion_primary: str = "neutral", message: str = "",
        context: str = "", multi_client=None, **kwargs
    ) -> Tuple[str, str]:
        self._reset_daily_counters_if_new_day()

        # ✅ إصلاح الفجوة 9: المنطق الصحيح لتوزيع الاستراتيجيات
        complexity = self._assess_complexity(task_type, emotion_primary, message)
        logger.info(f"🧠 Complexity: {complexity} | task={task_type} emotion={emotion_primary}")

        if complexity == "simple":
            self.daily_simple_uses += 1
            return await self._fast_reply(prompt, task_type)

        elif complexity == "medium":
            return await self._medium_reply(prompt, task_type, emotion_primary, message)

        elif complexity == "complex":
            if self.daily_council_uses < self.max_daily_council:
                self.daily_council_uses += 1
                logger.info(f"🧠 Full Council #{self.daily_council_uses}")
                return await self._full_council(prompt, task_type, emotion_primary, message, context)
            else:
                logger.warning("⚠️ Council limit reached, falling back to medium")
                return await self._medium_reply(prompt, task_type, emotion_primary, message)

        return await self._fast_reply(prompt, task_type)

    def _assess_complexity(self, task_type: str, emotion: str, message: str) -> str:
        high_emotion_words = [
            "حزين", "خايف", "مكتئب", "قلق", "وحيد", "محتار",
            "sad", "scared", "depressed", "anxious", "lonely"
        ]
        critical_words = [
            "نصيحة", "قرار", "مستقبل", "علاقة", "زواج", "طلاق",
            "advice", "decision", "future", "relationship", "job", "career"
        ]

        is_emotional = emotion in ["sadness", "fear", "love", "anger"] or \
                      any(w in (message or "").lower() for w in high_emotion_words)
        is_critical = any(w in (message or "").lower() for w in critical_words)
        is_complex_task = task_type in ["emotional", "deep_reasoning", "coaching", "dream"]
        is_long = len(message or "") > 100

        if is_critical or is_emotional:
            return "complex"
        if is_complex_task or is_long:
            return "medium"
        return "simple"

    async def _fast_reply(self, prompt: str, task_type: str) -> Tuple[str, str]:
        try:
            return await self.multi.get_best(prompt, preferred_providers=["groq"], task=task_type)
        except:
            return await self.multi.get_best(prompt, task=task_type)

    async def _medium_reply(self, prompt: str, task_type: str, emotion: str, message: str) -> Tuple[str, str]:
        # ✅ إصلاح الفجوة 5: Critic للردود الضعيفة حتى لو كانت طويلة
        try:
            reply, provider = await self.multi.get_best(
                prompt, preferred_providers=["gemini", "groq"], task=task_type
            )
        except:
            return await self._fast_reply(prompt, task_type)

        # مراجعة إذا كان الرد قصيرًا أو غير مفيد
        if len(reply) < 30 or "لا أعرف" in reply or "sorry" in reply.lower():
            critic_prompt = f"""المستخدم: {message[:150]}
الرد الحالي: {reply}
حسّن هذا الرد ليكون أكثر تفصيلاً وفائدة وتعاطفاً."""
            try:
                improved, _ = await self.multi.get_best(
                    critic_prompt, preferred_providers=["groq"], task="general"
                )
                return improved or reply, provider
            except:
                pass
        return reply, provider

    async def _full_council(self, prompt: str, task_type: str, emotion: str,
                            message: str, context: str) -> Tuple[str, str]:
        # ✅ إصلاح الفجوة 6: Planner يُستخدم فعلاً
        planner_task = asyncio.create_task(self._run_planner(message, context))
        generator_task = asyncio.create_task(self._run_main(prompt, task_type))

        plan_text, (reply, provider) = await asyncio.gather(planner_task, generator_task)

        # توجيه الـ Critic بخطة الـ Planner
        critic_result = await self._run_critic(reply, message, emotion, plan_text)
        if critic_result.get("needs_repair"):
            reply = await self._run_repair(reply, critic_result, emotion)

        return reply, f"council/{provider}"

    async def _run_planner(self, message: str, context: str) -> str:
        plan_prompt = f"""المستخدم: {message[:200]}
السياق: {context[:300] if context else "لا يوجد سياق إضافي"}

حدد باختصار: الهدف، النبرة، وأي نقاط مهمة لتضمينها في الرد."""
        try:
            result, _ = await self.multi.get_best(
                plan_prompt, preferred_providers=self.roles["planner"], task="general"
            )
            return result or ""
        except:
            return ""

    async def _run_main(self, prompt: str, task_type: str) -> Tuple[str, str]:
        return await self.multi.get_best(
            prompt, preferred_providers=self.roles["generator"], task=task_type
        )

    async def _run_critic(self, reply: str, message: str, emotion: str, plan: str) -> Dict[str, Any]:
        # ✅ إصلاح الفجوة 4: معايير تقييم أوسع
        critic_prompt = f"""راجع هذا الرد:
المستخدم: {message[:150]}
الخطة المقترحة: {plan[:200] if plan else "غير متوفرة"}
الرد: {reply[:350]}

قيّم: التعاطف، الدقة، عدم التكرار، وتحقيق هدف المحادثة.
إذا الرد لا يعالج احتياجات المستخدم بشكل كافٍ، اكتب عبارة "يحتاج إلى تحسين".
إذا الرد ممتاز، اكتب "ممتاز"."""
        try:
            review, _ = await self.multi.get_best(
                critic_prompt, preferred_providers=self.roles["critic"], task="general"
            )
            needs_repair = "يحتاج إلى تحسين" in review or "يحتاج تحسين" in review or "ضعيف" in review
            return {"review": review, "needs_repair": needs_repair}
        except:
            return {"review": "", "needs_repair": False}

    async def _run_repair(self, original: str, critic: Dict, emotion: str) -> str:
        repair_prompt = f"""أعد كتابة هذا الرد ليكون أفضل:
الرد الأصلي: {original}
ملاحظات المراجع: {critic.get('review', '')}"""
        try:
            improved, _ = await self.multi.get_best(
                repair_prompt, preferred_providers=self.roles["repair"], task="general"
            )
            return improved or original
        except:
            return original
