"""Twin Service – full orchestration with background queue."""
import time, logging
from typing import AsyncGenerator, Dict, Any, Optional
from app.infrastructure.ai.gemini_client import generate_stream
from app.infrastructure.ai.prompt_builder import prompt_builder
from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
from app.infrastructure.ai.council import council
from app.infrastructure.ai.self_critic import self_critic
from app.domain.services.memory_service import get_memory_context
from app.domain.services.context_service import build_context, format_context_for_prompt
from app.domain.services.relationship_service import update_relationship, detect_intent
from app.domain.services.attachment_service import detect_style, get_adjustments
from app.domain.services.background_tasks import schedule_post_reply
from app.domain.services.safety_service import check_safety, sanitize_input

logger = logging.getLogger("twin_service")

async def generate_twin_reply(
    message: str, user_id: str, twin_name: str = "توأمك",
    bond_level: float = 0.0, emotion: Optional[Dict] = None,
    history: Optional[list] = None, lang: str = "ar",
    tier: str = "free", intent: str = "general",
) -> AsyncGenerator[str, None]:
    start = time.time()

    # Safety check
    safety = check_safety(message)
    if not safety["safe"] and safety["severity"] == "critical":
        yield safety["helpline"]
        return

    message = sanitize_input(message)
    if not intent or intent == "general":
        intent, _ = detect_intent(message, lang)

    ctx = await build_context(user_id, message, emotion, history, lang, tier, intent)
    context_str = format_context_for_prompt(ctx, lang)

    recent_texts = [h.get("content","") for h in (history or [])[-20:]]
    attachment = await detect_style(recent_texts)
    adjustments = get_adjustments(attachment.get("style","unknown"))

    prompt = await prompt_builder.build(
        twin_name=twin_name, user_name="صديقي",
        relationship=ctx.get("relationship", {}),
        emotion=emotion or {}, voice={}, dialect={},
        message=message, memory_context=context_str,
        consciousness_context=ctx.get("consciousness", {}),
        history=history, intent=intent,
    )

    try:
        result, provider = await council.get_best_reply(
            prompt=prompt, task=intent,
            emotion=emotion.get("primary","neutral") if emotion else "neutral",
            message=message, intent=intent,
        )
    except AIUnavailable:
        result, provider = "أواجه ضغطاً تقنياً 💜", "fallback"

    result = await self_critic.evaluate(result)
    yield result

    latency = (time.time() - start) * 1000
    logger.info(f"Reply: {len(result)} chars, {latency:.0f}ms via {provider}")

    # Schedule background tasks (non-blocking)
    await schedule_post_reply(
        user_id=user_id, message=message, reply=result,
        history=history, twin_name=twin_name,
        emotion=emotion, context_data=ctx,
    )
