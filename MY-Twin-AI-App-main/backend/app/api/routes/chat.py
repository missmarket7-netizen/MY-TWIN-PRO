"""Chat Routes – Production Ready (v12.7.0)."""
import logging, time, asyncio, json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from app.api.dependencies.auth import get_current_user_id
from app.orchestration.twin_orchestrator import orchestrate
from app.observability.metrics_service import record_request

logger = logging.getLogger("chat_routes")
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    lang: str = Field("ar")
    calm_mode: bool = Field(False)
    voice_enabled: bool = Field(False)


@router.post("/chat")
async def chat(
    body: ChatRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Non-streaming chat endpoint."""
    start_time = time.time()
    try:
        response = await orchestrate(
            user_id=user_id,
            message=body.message,
            history=body.history,
            lang=body.lang,
            calm_mode=body.calm_mode,
            voice_enabled=body.voice_enabled,
        )
        latency = (time.time() - start_time) * 1000
        record_request(latency, provider="orchestrator", intent="general")
        return {"reply": response, "provider": "orchestrator", "latency_ms": round(latency, 2)}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, "Internal server error")


@router.post("/chat/stream")
async def chat_stream(
    body: ChatRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Streaming chat endpoint – SSE."""
    async def event_generator():
        try:
            response = await orchestrate(
                user_id=user_id,
                message=body.message,
                history=body.history,
                lang=body.lang,
                calm_mode=body.calm_mode,
                voice_enabled=body.voice_enabled,
            )
            # Split response into chunks for streaming simulation
            words = response.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.03)  # simulate streaming
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
