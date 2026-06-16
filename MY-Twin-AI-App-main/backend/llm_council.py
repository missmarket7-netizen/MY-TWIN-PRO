"""
MyTwin – Adaptive Sparse LLM Council v4.0 (اقتصادي وذكي)
- 80% Groq مباشر (أسرع وأرخص)
- 15% Generator + Critic
- 5% مجلس كامل (Planner + Generator + Critic + Repair)
- يتكيف مع عدد المستخدمين لتجنب استنزاف الحصة
"""
import logging, asyncio, time, os
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger("llm_council")

class LLMCouncil:
    def __init__(self, multi_client):
        self.multi = multi_client
        self.daily_council_uses = 0
        self.daily_simple_uses = 0

        # حدود ديناميكية حسب الباقة (تُقرأ من المتغيرات أو افتراضية)
        self.max_daily_council = int(os.getenv("COUNCIL_MAX_DAILY", "50"))
        self.max_daily_simple = int(os.getenv("SIMPLE_MAX_DAILY", "500"))

        # أدوار المجلس
        self.roles = {
            "planner": ["gemini", "groq"],
            "generator": ["gemini", "groq"],
            "critic": ["gemini", "groq"],
            "repair": ["groq", "gemini"],
        }

    async def get_best_reply(
        self, prompt: str, task_type: str = "general",
        emotion: str = "neutral", message: str = "",
        context: str = ""
    ) -> Tuple[str, str]:
        """يختار أفضل استراتيجية للرد بناءً على تعقيد الرسالة"""
        start = time.time()

        # 1. تحديد مستوى التعقيد
        complexity = self._assess_complexity(task_type, emotion, message)

        # 2. اختيار الاستراتيجية
        if complexity == "simple" or self.daily_simple_uses < self.max_daily_simple:
            self.daily_simple_uses += 1
            return await self._fast_reply(prompt, task_type)

        elif complexity == "medium":
            return await self._medium_reply(prompt, task_type, emotion, message)

        elif complexity == "complex":
            if self.daily_council_uses < self.max_daily_council:
                self.daily_council_uses += 1
                return await self._full_council(prompt, task_type, emotion, message, context)

        # Fallback
        return await self._fast_reply(prompt, task_type)

    def _assess_complexity(self, task_type: str, emotion: str, message: str) -> str:
        """يقيم تعقيد الرسالة لتحديد مستوى المجلس"""
        # كلمات تدل على تعقيد
        high_emotion_words = ["حزين", "خايف", "مكتئب", "قلق", "وحيد", "محتار",
                             "sad", "scared", "depressed", "anxious", "lonely"]
        critical_words = ["نصيحة", "قرار", "مستقبل", "علاقة", "زواج", "طلاق",
                         "advice", "decision", "future", "relationship", "job", "career"]

        is_emotional = emotion in ["sadness", "fear", "love", "anger"] or \
                      any(w in message.lower() for w in high_emotion_words)
        is_critical = any(w in message.lower() for w in critical_words)
        is_complex_task = task_type in ["emotional", "deep_reasoning", "coaching", "dream"]
        is_long = len(message) > 100

        if is_critical or is_emotional:
            return "complex"
        if is_complex_task or is_long:
            return "medium"
        return "simple"

    async def _fast_reply(self, prompt: str, task_type: str) -> Tuple[str, str]:
        """رد سريع عبر Groq (80% من الحالات)"""
        try:
            return await self.multi.get_best(prompt, preferred_providers=["groq"], task=task_type)
        except:
            return await self.multi.get_best(prompt, task=task_type)

    async def _medium_reply(self, prompt: str, task_type: str, emotion: str, message: str) -> Tuple[str, str]:
        """Generator + Critic (15% من الحالات)"""
        # 1. توليد الرد
        try:
            reply, provider = await self.multi.get_best(
                prompt, preferred_providers=["gemini", "groq"], task=task_type
            )
        except:
            return await self._fast_reply(prompt, task_type)

        # 2. مراجعة سريعة إذا كان الرد قصيراً جداً
        if len(reply) < 30:
            critic_prompt = f"حسّن هذا الرد القصير ليكون أكثر فائدة: {reply}"
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
        """مجلس كامل للمهام الحرجة (5% من الحالات)"""
        logger.info(f"🧠 Full Council activated for: {task_type}")

        # 1. Planner + Generator بالتوازي
        planner_task = asyncio.create_task(self._run_planner(message, context))
        generator_task = asyncio.create_task(self._run_generator(prompt, task_type))

        plan, (reply, provider) = await asyncio.gather(planner_task, generator_task)

        # 2. Critic
        if len(reply) > 20:
            critic_result = await self._run_critic(reply, message, emotion)
            if critic_result.get("needs_repair"):
                reply = await self._run_repair(reply, critic_result, emotion)

        return reply, f"council/{provider}"

    async def _run_planner(self, message: str, context: str) -> str:
        """يخطط للرد (بسيط وسريع)"""
        plan_prompt = f"""حدد باختصار:
1. نية المستخدم من: "{message[:200]}"
2. النبرة المناسبة"""
        try:
            result, _ = await self.multi.get_best(
                plan_prompt, preferred_providers=self.roles["planner"], task="general"
            )
            return result or ""
        except:
            return ""

    async def _run_generator(self, prompt: str, task_type: str) -> Tuple[str, str]:
        """يولد الرد الأساسي"""
        return await self.multi.get_best(
            prompt, preferred_providers=self.roles["generator"], task=task_type
        )

    async def _run_critic(self, reply: str, message: str, emotion: str) -> Dict[str, Any]:
        """يراجع جودة الرد"""
        critic_prompt = f"""راجع هذا الرد:
المستخدم: {message[:150]}
الرد: {reply[:300]}

هل الرد:
- متعاطف؟
- دقيق؟
- غير مكرر؟

إذا سيء، اكتب "يحتاج تحسين". إذا ممتاز، اكتب "ممتاز"."""
        try:
            review, _ = await self.multi.get_best(
                critic_prompt, preferred_providers=self.roles["critic"], task="general"
            )
            return {"review": review, "needs_repair": "يحتاج تحسين" in review}
        except:
            return {"review": "", "needs_repair": False}

    async def _run_repair(self, original: str, critic: Dict, emotion: str) -> str:
        """يصلح الرد بناءً على ملاحظات الناقد"""
        repair_prompt = f"""أعد كتابة هذا الرد ليكون أفضل:
الرد الأصلي: {original}
ملاحظات: {critic.get('review', '')}"""
        try:
            improved, _ = await self.multi.get_best(
                repair_prompt, preferred_providers=self.roles["repair"], task="general"
            )
            return improved or original
        except:
            return original
