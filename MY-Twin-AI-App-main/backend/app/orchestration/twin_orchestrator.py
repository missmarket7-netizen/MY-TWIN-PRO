"""
MyTwin – Twin Orchestrator v12.3 (Hexagonal Architecture)
Central conductor for all AI reasoning and response generation.
"""
import time, logging, asyncio
from typing import Dict, Any, Optional

from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
from app.infrastructure.ai.council import council
from app.infrastructure.ai.self_critic import self_critic
from app.infrastructure.ai.prompt_builder import prompt_builder
from app.infrastructure.ai.dialect_service import get_dialect_for_user, get_dialect_prompt
from app.domain.services.safety_service import check_safety, sanitize_input
from app.domain.services.cost_service import get_best_provider
from app.twin_state.relationship_service import detect_intent, load as load_relationship, update as update_relationship
from app.twin_state.attachment_service import detect as detect_attachment, get_adjustments
from app.twin_state.emotional_service import emotional_service
from app.twin_state.consciousness_service import load as load_consciousness, reflect
from app.twin_state.identity_service import get_identity
from app.twin_state.journey_service import get_phase, get_behavior
from app.memory.memory_retriever import retrieve_and_summarize
from app.memory.memory_service import save as save_memory
from app.repositories.profile_repository import get_profile, update_last_active, update_energy
from app.background.tasks import schedule_post_reply
from app.events.event_bus import emit
from app.models.event import MessageEvent, StageChangeEvent, TrustEvent, AttachmentEvent, ReflectionEvent
from app.core.i18n import msg

logger = logging.getLogger("twin_orchestrator")

async def orchestrate(
    user_id: str,
    message: str,
    history: Optional[list] = None,
    lang: str = "ar",
    tier: str = "free",
    calm_mode: bool = False,
    voice_enabled: bool = False,
) -> str:
    start_time = time.time()
    provider_name = "unknown"
    
    try:
        # 1. Safety Check
        safety = check_safety(message)
        if not safety["safe"] and safety["severity"] == "critical":
            return safety.get("helpline", msg("error_fallback", lang))
        clean_message = sanitize_input(message)
        
        # 2. Load Profile & State
        profile, relationship, consciousness = await asyncio.gather(
            get_profile(user_id),
            load_relationship(user_id),
            load_consciousness(user_id),
        )
        
        if profile:
            tier = profile.tier if hasattr(profile, 'tier') else tier
            lang = profile.lang if hasattr(profile, 'lang') else lang
            twin_name = profile.twin_name if hasattr(profile, 'twin_name') else "توأمك"
        else:
            twin_name = "توأمك"
        
        # 3. Detect Intent & Emotion
        intent, intent_conf = detect_intent(clean_message, lang)
        emotion = await emotional_service.analyze(clean_message, user_id)
        
        # 4. Memory & Attachment
        recent_texts = [h.get("content", "") for h in (history or [])[-20:]]
        memories, attachment = await asyncio.gather(
            retrieve_and_summarize([], user_id, top_k=3),
            detect_attachment(recent_texts, None),
        )
        adjustments = await get_adjustments(attachment.get("style", "unknown")) if attachment else {}
        
        # 5. Journey & Identity
        journey_phase = await get_phase(relationship.bond_level if relationship else 0)
        identity = await get_identity(user_id, twin_name, lang)
        
        # 6. Detect Dialect
        dialect, _ = get_dialect_for_user("SA", clean_message)
        dialect_instruction = get_dialect_prompt(dialect)
        
        # 7. Build Prompt
        context_data = _build_context(
            relationship=relationship, consciousness=consciousness,
            memories=memories, attachment=attachment, identity=identity,
            journey_phase=journey_phase, emotion=emotion,
            dialect=dialect, dialect_instruction=dialect_instruction,
        )
        
        prompt = await prompt_builder.build(
            twin_name=twin_name,
            user_name=profile.full_name if profile else "صديقي",
            relationship={"bond_level": relationship.bond_level if relationship else 0, "label": getattr(relationship, 'stage', 'stranger')},
            emotion=emotion,
            voice={}, dialect={"dialect": dialect, "instruction": dialect_instruction},
            message=clean_message,
            memory_context=context_data.get("memory_context", ""),
            consciousness_context=consciousness.get_state_summary(user_id) if consciousness else {},
            history=history, intent=intent,
        )
        
        # 8. Reasoning
        try:
            response, provider_name = await council.get_best_reply(
                prompt=prompt, task=intent,
                emotion=emotion.get("primary", "neutral"),
                message=clean_message, intent=intent,
            )
        except AIUnavailable:
            response = msg("error_ai_unavailable", lang)
            provider_name = "fallback"
        
        # 9. Self-Critic
        response = await self_critic.evaluate(response)
        
        # 10. Emit Events
        await emit(MessageEvent(user_id=user_id, content=clean_message[:200], intent=intent, lang=lang))
        
        if attachment and attachment.get("style") != "unknown":
            await emit(AttachmentEvent(user_id=user_id, style=attachment["style"], confidence=attachment.get("confidence", 0)))
        
        # 11. Update Relationship
        old_bond = relationship.bond_level if relationship else 0
        old_stage = getattr(relationship, 'stage', 'stranger') if relationship else 'stranger'
        stage_up = await update_relationship(
            user_id=user_id, emotion=emotion, message=clean_message,
            journey_phase=journey_phase,
            attachment_style=attachment.get("style") if attachment else None,
        )
        
        if stage_up:
            new_relationship = await load_relationship(user_id)
            await emit(StageChangeEvent(
                user_id=user_id, old_stage=old_stage,
                new_stage=getattr(new_relationship, 'stage', 'stranger'),
                message_ar=stage_up.get("ar", ""), message_en=stage_up.get("en", ""),
            ))
        
        new_bond = getattr((await load_relationship(user_id)), 'bond_level', 0)
        if new_bond > old_bond:
            await emit(TrustEvent(user_id=user_id, old_bond=old_bond, new_bond=new_bond))
        
        await emit(ReflectionEvent(user_id=user_id, summary=clean_message[:200], lang=lang))
        
        # 12. Background Tasks
        await schedule_post_reply(user_id=user_id, message=clean_message, reply=response, history=history, twin_name=twin_name)
        
        # 13. Update Profile
        if profile:
            await update_last_active(user_id)
            new_energy = max(0, (getattr(profile, 'twin_energy', 100) or 100) - 5)
            new_msg = (getattr(profile, 'daily_messages_used', 0) or 0) + 1
            await update_energy(user_id, new_energy, new_msg, getattr(profile, 'daily_tokens_used', 0) or 0)
        
        latency = (time.time() - start_time) * 1000
        logger.info(f"✅ Orchestrated: {len(response)} chars, {latency:.0f}ms, intent={intent}, provider={provider_name}")
        
        return response
        
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        return msg("error_fallback", lang)

def _build_context(**kwargs) -> Dict[str, Any]:
    """Build context dictionary for prompt."""
    parts = []
    rel = kwargs.get("relationship")
    if rel:
        parts.append(f"Bond: {getattr(rel, 'bond_level', 0):.0f}%")
    
    memories = kwargs.get("memories", {})
    if isinstance(memories, dict) and memories.get("memories"):
        mem_lines = [f"- {m.content[:200]}" for m in memories["memories"][:3] if hasattr(m, 'content')]
        parts.append("<MEMORIES>\n" + "\n".join(mem_lines) + "\n</MEMORIES>")
    
    dialect = kwargs.get("dialect_instruction", "")
    if dialect:
        parts.append(dialect)
    
    return {"memory_context": "\n".join(parts)}
