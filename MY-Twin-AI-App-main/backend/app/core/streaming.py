"""
Streaming v2.0 – محرك SSE متكامل
==================================
- تدفق الردود من الذكاء الاصطناعي
- دمج مع الذاكرة (TCMA) بعد التدفق
- دعم أحداث مخصصة (تفكير، أدوات، أخطاء)
"""
import json, logging
from typing import AsyncGenerator, Optional, Dict, Any

logger = logging.getLogger("streaming")


class StreamingService:
    """محرك التدفق الموحد لـ MyTwin"""
    
    @staticmethod
    async def sse_generator(
        content_gen: AsyncGenerator[str, None],
        final_data: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """تحويل مولد محتوى إلى تدفق SSE"""
        async for chunk in content_gen:
            if chunk:
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        
        if final_data:
            yield f"data: {json.dumps({'final': True, **final_data}, ensure_ascii=False)}\n\n"
        
        yield "data: [DONE]\n\n"

    @staticmethod
    async def thinking_event(message: str) -> str:
        """إرسال حدث 'تفكير' إلى العميل"""
        return f"data: {json.dumps({'type': 'thinking', 'message': message}, ensure_ascii=False)}\n\n"

    @staticmethod
    async def tool_call_event(tool_name: str, result: str) -> str:
        """إرسال حدث 'استدعاء أداة' إلى العميل"""
        return f"data: {json.dumps({'type': 'tool_call', 'tool': tool_name, 'result': result[:200]}, ensure_ascii=False)}\n\n"

    @staticmethod
    async def error_event(error_message: str) -> str:
        """إرسال حدث 'خطأ' إلى العميل"""
        return f"data: {json.dumps({'type': 'error', 'message': error_message}, ensure_ascii=False)}\n\n"

    @staticmethod
    async def heartbeat() -> str:
        """إرسال نبضة حياة للعميل (كل 15 ثانية)"""
        return f": heartbeat\n\n"

    @staticmethod
    async def stream_ai_response(
        prompt: str,
        language: str = "ar",
        save_to_memory: bool = True,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        تدفق رد الذكاء الاصطناعي مع حفظ في الذاكرة بعد الانتهاء.
        """
        try:
            from app.infrastructure.ai.provider_router import provider_router
        except ImportError:
            yield await StreamingService.error_event("مزود الذكاء الاصطناعي غير متاح")
            return

        full_response = ""
        try:
            # محاولة التدفق من المزود
            async for chunk in provider_router.stream(prompt, language=language):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        except AttributeError:
            # المزود لا يدعم التدفق، نجلب الرد كاملاً
            response = await provider_router.generate(prompt, language=language)
            if response:
                full_response = response
                yield f"data: {json.dumps({'chunk': response}, ensure_ascii=False)}\n\n"

        # حفظ في الذاكرة بعد الانتهاء
        if save_to_memory and user_id and full_response:
            try:
                from app.memory.emotional.emotional_memory import store_emotional_memory
                await store_emotional_memory(
                    user_id=user_id,
                    expressed_text=prompt[:300],
                    detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.0},
                    trigger="chat"
                )
            except Exception as e:
                logger.warning(f"فشل حفظ الذاكرة بعد التدفق: {e}")

        yield f"data: {json.dumps({'final': True, 'length': len(full_response)}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


# دالة مساعدة للتوافق مع القديم
async def sse_generator(
    content_gen: AsyncGenerator[str, None],
    final_data: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """دالة مساعدة للتوافق مع الكود القديم"""
    async for event in StreamingService.sse_generator(content_gen, final_data):
        yield event


streaming = StreamingService()
logger.info("✅ Streaming Engine v2.0 initialized")
