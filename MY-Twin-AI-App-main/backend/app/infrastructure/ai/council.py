"""LLM Council – adaptive sparse council."""
import logging, asyncio, time, os
from typing import Tuple
from app.infrastructure.ai.provider_router import provider_router

logger = logging.getLogger("council")

class LLMCouncil:
    def __init__(self):
        self.daily_council = 0
        self.daily_simple = 0
        self._last_reset = time.strftime("%Y-%m-%d")
        self.max_council = int(os.getenv("COUNCIL_MAX_DAILY","50"))

    def _reset(self):
        today = time.strftime("%Y-%m-%d")
        if today != self._last_reset:
            self.daily_council = 0
            self.daily_simple = 0
            self._last_reset = today

    def _complexity(self, task: str, emotion: str, message: str, intent: str = "general") -> str:
        high_emo = ["حزين","خايف","مكتئب","قلق","sad","scared"]
        critical = ["نصيحة","قرار","مستقبل","زواج","طلاق","advice"]
        is_emo = emotion in ["sadness","fear","love","anger"] or any(w in (message or "").lower() for w in high_emo)
        is_critical = any(w in (message or "").lower() for w in critical)
        if is_critical or is_emo or intent in ["coaching","decision","emotional"]: return "complex"
        if task in ["emotional","deep_reasoning","coaching"] or len(message or "")>100: return "medium"
        return "simple"

    async def get_best_reply(self, prompt: str, task: str = "general", emotion: str = "neutral", message: str = "", intent: str = "general") -> Tuple[str, str]:
        self._reset()
        c = self._complexity(task, emotion, message, intent)
        if c == "simple":
            self.daily_simple += 1
            return await provider_router.route(prompt, task, emotion)
        elif c == "medium":
            reply, prov = await provider_router.route(prompt, task, emotion)
            if len(reply.split()) < 15:
                try:
                    improved, _ = await provider_router.route(f"حسّن: {reply}\nرسالة المستخدم: {message[:150]}", "quick_reply")
                    return improved or reply, prov
                except: pass
            return reply, prov
        else:
            if self.daily_council < self.max_council:
                self.daily_council += 1
                try:
                    plan, _ = await provider_router.route(f"حدد هدف ونبرة: {message[:200]}", "quick_reply")
                    reply, prov = await provider_router.route(prompt, task, emotion)
                    review, _ = await provider_router.route(f"قيم: {reply[:350]}", "quick_reply")
                    if any(w in review for w in ["يحتاج تحسين","ضعيف"]):
                        reply, _ = await provider_router.route(f"أعد كتابة: {reply}\nملاحظات: {review}", task, emotion)
                    return reply, f"council/{prov}"
                except: pass
            return await provider_router.route(prompt, task, emotion)

council = LLMCouncil()
