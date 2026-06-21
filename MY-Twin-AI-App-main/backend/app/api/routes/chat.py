"""
Chat Routes v3.0 – متوافقة مع Twin Orchestrator v17
========================================================
- محادثة عادية (/chat)
- محادثة متدفقة (/chat/stream)
- تكامل مع Rate Limiter و Metrics Service
"""
import logging, time, asyncio, json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from app.api.dependencies.auth import get_current_user_id, get_user_tier
from app.api.dependencies.rate_limiter import TierRateLimit

logger = logging.getLogger("chat_routes")
router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    lang: str = Field("ar")
    calm_mode: bool = Field(False)
    voice_enabled: bool = Field(False)

@router.post("/chat", dependencies=[Depends(TierRateLimit(feature="chat"))])
async def chat(
    body: ChatRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    tier: str = Depends(get_user_tier),
):
    """محادثة عادية (Non-streaming)"""
    start_time = time.time()
    try:
        from app.orchestration.twin_orchestrator import orchestrate
        
        response = await orchestrate(
            user_id=user_id,
            message=body.message,
            history=body.history,
            lang=body.lang,
            calm_mode=body.calm_mode,
            voice_enabled=body.voice_enabled,
        )
        
        latency = (time.time() - start_time) * 1000
        
        # تسجيل المقياس
        try:
            from app.observability.metrics_service import metrics
            metrics.record_request("/chat", 200, latency, tier)
        except: pass
        
        return {
            "reply": response,
            "provider": "orchestrator",
            "latency_ms": round(latency, 2),
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        
        # تسجيل الخطأ
        try:
            from app.observability.metrics_service import metrics
            metrics.record_request("/chat", 500, (time.time() - start_time) * 1000, tier)
        except: pass
        
        raise HTTPException(500, "حدث خطأ داخلي. حاول مرة أخرى.")

@router.post("/chat/stream", dependencies=[Depends(TierRateLimit(feature="chat"))])
async def chat_stream(
    body: ChatRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    tier: str = Depends(get_user_tier),
):
    """محادثة متدفقة (SSE)"""
    
    async def event_generator():
        try:
            from app.orchestration.twin_orchestrator import orchestrate
            
            response = await orchestrate(
                user_id=user_id,
                message=body.message,
                history=body.history,
                lang=body.lang,
                calm_mode=body.calm_mode,
                voice_enabled=body.voice_enabled,
            )
            
            # محاكاة التدفق (يمكن استبدالها بـ Gemini Streaming لاحقاً)
            words = response.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.03)
            
            yield f"data: {json.dumps({'final': True}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

logger.info("✅ Chat Routes v3.0 initialized")
