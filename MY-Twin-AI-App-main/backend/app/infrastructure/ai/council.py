"""
LLM Council v3.0 – مجلس ذكي متكامل مع TCMA
=============================================
- تحليل عمق الطلب باستخدام الذاكرة والعاطفة
- تحسين الردود من خلال خطوات: تخطيط ← توليد ← مراجعة ← تحسين
- تكامل كامل مع Observability لتتبع الأداء
"""
import logging, asyncio, time, os
from typing import Tuple, Optional

logger = logging.getLogger("council")

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class LLMCouncil:
    def __init__(self):
        self.daily_council = 0
        self.daily_simple = 0
        self._last_reset = time.strftime("%Y-%m-%d")
        self.max_council = int(os.getenv("COUNCIL_MAX_DAILY", "50"))

    def _reset(self):
        today = time.strftime("%Y-%m-%d")
        if today != self._last_reset:
            self.daily_council = 0
            self.daily_simple = 0
            self._last_reset = today

    async def _complexity(self, task: str, emotion: str, message: str, intent: str = "general", user_id: Optional[str] = None) -> str:
        """
        تحليل درجة تعقيد الطلب.
        """
        # 1. التحليل النصي الأساسي
        high_emo = ["حزين","خايف","مكتئب","قلق","sad","scared","anxious"]
        critical = ["نصيحة","قرار","مستقبل","زواج","طلاق","advice","help me decide"]
        msg_lower = (message or "").lower()
        
        is_emo = emotion in ["sadness","fear","love","anger"] or any(w in msg_lower for w in high_emo)
        is_critical = any(w in msg_lower for w in critical)
        
        # 2. تكامل مع TCMA (إن أمكن)
        if user_id:
            try:
                from app.memory.emotional.emotional_memory import get_emotional_state_for_response
                tcma_emotion = await get_emotional_state_for_response(user_id, message)
                if tcma_emotion and tcma_emotion.get("is_culturally_disguised"):
                    # المستخدم يخفي مشاعره الحقيقية
                    return "complex"
            except: pass

        # 3. تحديد المستوى
        if is_critical or intent in ["coaching","decision","emotional"] or task in ["emotional","deep_reasoning","coaching"]:
            return "complex"
        if is_emo or len(message or "") > 200 or intent in ["business","study","code_lab"]:
            return "medium"
        return "simple"

    async def get_best_reply(
        self,
        prompt: str,
        task: str = "general",
        emotion: str = "neutral",
        message: str = "",
        intent: str = "general",
        user_id: Optional[str] = None
    ) -> Tuple[str, str]:
        self._reset()
        
        # تتبع الخطوات
        try:
            from app.observability.system_monitor import tracker
            tracker.start("council_analysis")
        except: pass
        
        complexity = await self._complexity(task, emotion, message, intent, user_id)
        
        try:
            from app.observability.system_monitor import tracker
            tracker.end()
        except: pass

        # ========== بسيط: إرسال مباشر ==========
        if complexity == "simple":
            self.daily_simple += 1
            reply, prov = await provider_router.route(prompt, task, emotion, user_id=user_id)
            return reply, prov
        
        # ========== متوسط: توليد ← تحسين ← مراجعة ==========
        elif complexity == "medium":
            try:
                from app.observability.system_monitor import tracker
                tracker.start("medium_council_optimize")
            except: pass
            
            reply, prov = await provider_router.route(prompt, task, emotion, user_id=user_id)
            
            # تحسين الردود القصيرة
            if reply and len(reply.split()) < 15:
                try:
                    improved, _ = await provider_router.route(
                        f"حسّن هذا الرد ليكون أكثر تفصيلاً وفائدة:\n{reply}\n\nالرسالة الأصلية: {message[:200]}",
                        "quick_reply", user_id=user_id
                    )
                    reply = improved or reply
                except: pass
            
            try:
                from app.observability.system_monitor import tracker
                tracker.end()
            except: pass
            
            return reply, prov
        
        # ========== معقد: تخطيط ← توليد ← مراجعة ← تحسين ==========
        else:
            if self.daily_council >= self.max_council:
                logger.info("مجلس يومي مكتمل، استخدام عادي")
                return await provider_router.route(prompt, task, emotion, user_id=user_id)
            
            self.daily_council += 1
            
            try:
                from app.observability.system_monitor import tracker
                tracker.start("complex_council_plan")
                tracker.start("complex_council_generate")
                tracker.start("complex_council_review")
            except: pass
            
            try:
                # الخطوة 1: التخطيط
                plan_prompt = f"حدد الهدف والنبرة المناسبة للرد على:\n{message[:300]}\nالعاطفة: {emotion}"
                plan, _ = await provider_router.route(plan_prompt, "deep_reasoning", user_id=user_id)
                
                # الخطوة 2: التوليد
                reply, prov = await provider_router.route(prompt, task, emotion, user_id=user_id)
                
                # الخطوة 3: المراجعة
                review_prompt = f"قيم جودة الرد التالي:\n{reply[:400]}\n\nهل يحتاج تحسيناً؟ أجب: ممتاز، جيد، يحتاج تحسين"
                review, _ = await provider_router.route(review_prompt, "quick_reply", user_id=user_id)
                
                # الخطوة 4: التحسين (إذا لزم)
                if review and any(w in review for w in ["يحتاج تحسين","ضعيف","سيء","needs improvement","bad"]):
                    improve_prompt = f"أعد كتابة الرد بأسلوب أفضل:\nالرد الأصلي: {reply}\nملاحظات: {review}\nالرسالة: {message[:200]}"
                    reply, prov = await provider_router.route(improve_prompt, task, emotion, user_id=user_id)
                    return reply, f"council/{prov}"
                
                return reply, prov
                
            except Exception as e:
                logger.warning(f"فشل المجلس المعقد: {e}")
                return await provider_router.route(prompt, task, emotion, user_id=user_id)
            finally:
                try:
                    from app.observability.system_monitor import tracker
                    tracker.end()
                except: pass

council = LLMCouncil()
logger.info("✅ LLM Council v3.0 initialized")
