"""Chat Routes – streaming and orchestration endpoint."""
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from app.api.dependencies.auth import get_current_user_id
from app.orchestration.twin_orchestrator import orchestrate

logger = logging.getLogger("chat_routes")
router = APIRouter(prefix="/api", tags=["chat"])

class ChatBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    twin_name: str = Field("توأمك")
    history: List[Dict] = Field(default_factory=list)
    lang: str = Field("ar")
    calm_mode: bool = Field(False)
    voice_enabled: bool = Field(False)

@router.post("/chat")
async def chat(body: ChatBody, user_id: str = Depends(get_current_user_id)):
    """Full orchestrated chat endpoint."""
    response = await orchestrate(
        user_id=user_id,
        message=body.message,
        history=body.history,
        lang=body.lang,
        calm_mode=body.calm_mode,
        voice_enabled=body.voice_enabled,
    )
    return {"reply": response}

@router.post("/chat/stream")
async def chat_stream(body: ChatBody, user_id: str = Depends(get_current_user_id)):
    """Streaming chat endpoint."""
    async def event_generator():
        response = await orchestrate(
            user_id=user_id,
            message=body.message,
            history=body.history,
            lang=body.lang,
            calm_mode=body.calm_mode,
            voice_enabled=body.voice_enabled,
        )
        yield f"data: {response}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})
