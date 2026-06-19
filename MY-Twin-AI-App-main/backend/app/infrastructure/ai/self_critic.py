"""Self Critic – post-generation quality check."""
import logging
from app.infrastructure.ai.provider_router import provider_router

logger = logging.getLogger("self_critic")

class SelfCritic:
    async def evaluate(self, reply: str) -> str:
        if not reply or len(reply)<5: return reply
        if self._has_repetition(reply):
            try:
                improved, _ = await provider_router.route(f"أعد كتابة لتجنب التكرار: {reply}", "quick_reply")
                return improved or reply
            except: pass
        return reply

    def _has_repetition(self, text: str) -> bool:
        words = text.split()
        return len(words)>=10 and len(set(words))/len(words)<0.4

self_critic = SelfCritic()
