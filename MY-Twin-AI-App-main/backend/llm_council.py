"""
MyTwin – LLM Council v3.0 (مخصص لـ 9 APIs)
- يوزع الحمل على 3 مفاتيح لكل مزود
- يستخدم Council كامل للمهام المهمة فقط
- بقية المهام: Groq أساسي (أرخص وأسرع)
"""
import logging, asyncio, time, random
from typing import Tuple, Optional, Dict, Any, List

logger = logging.getLogger("llm_council")

class LLMCouncil:
    def __init__(self, multi_client):
        self.multi = multi_client
        self.daily_council_uses = 0
        self.max_daily_council = 100  # حد يومي للمجلس الكامل

        # توزيع الأدوار على المزودين
        self.roles = {
            "planner": ["gemini", "openrouter"],      # Gemini أساسي، OpenRouter احتياطي
            "main": ["gemini", "groq", "openrouter"], # Gemini أساسي للمشاعر، Groq للسرعة
            "critic": ["openrouter", "gemini"],       # OpenRouter للتحليل، Gemini احتياطي
            "repair": ["gemini", "groq"],             # Gemini للتعاطف، Groq احتياطي
        }

        # عتبات تفعيل المجلس
        self.council_triggers = {
            "emotional": True,       # دائماً مجلس للمشاعر
            "deep_reasoning": True,  # دائماً مجلس للتحليل
            "coaching": True,        # دائماً مجلس للتدريب
            "dream": True,           # دائماً مجلس للأحلام
            "general": False,        # بدون مجلس للمحادثات العادية
            "search": False,         # بدون مجلس للبحث
        }

    async def get_best_reply(
        self, prompt: str, task_type: str = "general",
        emotion: str = "neutral", message: str = "",
        context: str = ""
    ) -> Tuple[str, str]:
        """
        المجلس الذكي: يستخدم Council فقط عند الحاجة
        """
        start = time.time()
        needs_council = self._should_use_council(task_type, emotion, message)

        if not needs_council or self.daily_council_uses >= self.max_daily_council:
            # استخدام Groq مباشرة (أسرع وأرخص)
            return await self._quick_reply(prompt, task_type)

        self.daily_council_uses += 1
        logger.info(f"🧠 Council #{self.daily_council_uses} لـ {task_type}")

        # 1. Planner + Main بالتوازي
        planner_task = asyncio.create_task(self._run_planner(message, context, task_type))
        main_task = asyncio.create_task(self._run_main(prompt, task_type, emotion))

        planner_result, main_result = await asyncio.gather(planner_task, main_task)

        # 2. Critic يراجع الرد
        critic_result = await self._run_critic(main_result[0], message, emotion, context)

        # 3. Repair إذا لزم الأمر
        if critic_result.get("needs_repair"):
            final = await self._run_repair(main_result[0], critic_result, prompt, emotion)
        else:
            final = critic_result.get("improved", main_result[0])

        elapsed = (time.time() - start) * 1000
        logger.info(f"⏱️ Council: {elapsed:.0f}ms")
        return final, f"council/{main_result[1]}"

    def _should_use_council(self, task_type: str, emotion: str, message: str) -> bool:
        """تحديد ما إذا كانت المهمة تستحق Council كامل"""
        # محفزات المجلس
        high_emotion_words = ["حزين", "خايف", "مكتئب", "قلق", "وحيد", "محتار",
                             "sad", "scared", "depressed", "anxious", "lonely"]
        critical_words = ["نصيحة", "قرار", "مستقبل", "علاقة", "زواج", "طلاق",
                         "advice", "decision", "future", "relationship"]

        is_important = self.council_triggers.get(task_type, False)
        is_emotional = emotion in ["sadness", "fear", "love", "anger"] or \
                      any(w in message.lower() for w in high_emotion_words)
        is_critical = any(w in message.lower() for w in critical_words)

        return is_important or is_emotional or is_critical

    async def _quick_reply(self, prompt: str, task_type: str) -> Tuple[str, str]:
        """رد سريع عبر Groq"""
        try:
            return await self.multi.get_best(prompt, preferred_providers=["groq"], task=task_type)
        except:
            return await self.multi.get_best(prompt, task=task_type)

    async def _run_planner(self, message: str, context: str, task_type: str) -> str:
        """يخطط لكيفية الرد"""
        plan_prompt = f"""أنت مخطط ذكي. حدد باختصار (جملة أو جملتين):
1. الهدف من الرد على: "{message[:300]}"
2. النبرة المناسبة
3. هل يحتاج أدوات خارجية؟

السياق: {context[:500]}"""
        try:
            result, _ = await self.multi.get_best(plan_prompt, preferred_providers=self.roles["planner"], task="general")
            return result or ""
        except:
            return ""

    async def _run_main(self, prompt: str, task_type: str, emotion: str) -> Tuple[str, str]:
        """يولد الرد الأساسي"""
        return await self.multi.get_best(prompt, preferred_providers=self.roles["main"], task=task_type)

    async def _run_critic(self, reply: str, message: str, emotion: str, context: str) -> Dict:
        """يراجع جودة الرد"""
        critic_prompt = f"""راجع هذا الرد على رسالة المستخدم: "{message[:200]}"

الرد: {reply}

قيّم (من 1-10):
1. التعاطف
2. الدقة
3. الطول المناسب
4. عدم التكرار

إذا التقييم أقل من 7 لأي معيار، اكتب التحسين المطلوب.
إذا الرد ممتاز، اكتب "ممتاز" فقط.

التقييم:"""
        try:
            review, _ = await self.multi.get_best(critic_prompt, preferred_providers=self.roles["critic"], task="general")
            needs_repair = "ممتاز" not in review and "excellent" not in review.lower()
            return {"review": review, "needs_repair": needs_repair, "improved": reply}
        except:
            return {"review": "", "needs_repair": False, "improved": reply}

    async def _run_repair(self, original: str, critic: Dict, prompt: str, emotion: str) -> str:
        """يصلح الرد بناءً على ملاحظات الناقد"""
        repair_prompt = f"""الرد الأصلي: {original}

ملاحظات المراجع: {critic.get('review', '')}

أعد كتابة الرد ليكون أفضل مع الحفاظ على المعنى الأصلي.
كن متعاطفاً ومفيداً."""
        try:
            improved, _ = await self.multi.get_best(repair_prompt, preferred_providers=self.roles["repair"], task="general")
            return improved or original
        except:
            return original
