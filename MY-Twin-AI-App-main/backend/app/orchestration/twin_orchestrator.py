"""
Twin Orchestrator with Weekly Report & Full Integration
"""
import time, logging, random, asyncio, traceback
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger("twin_orchestrator")

try:
    from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
try:
    from app.infrastructure.ai.provider_router_internal import generate_with_fallback
    INTERNAL_ROUTER = True
except:
    INTERNAL_ROUTER = False
    from app.infrastructure.ai.council import council
    from app.infrastructure.ai.self_critic import self_critic
    from app.domain.services.safety_service import check_safety, sanitize_input
    from app.twin_state.relationship_service import detect_intent
    from app.repositories.profile_repository import get_profile
    from app.infrastructure.cache.cache_service import get_cached_response, set_cached_response
    AI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Some AI imports failed: {e}")
    AI_AVAILABLE = False

try:
    from app.memory.retrieval.memory_retriever import retrieve_full_context
    from app.memory.relationship.person_node import process_message_for_persons
    from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_state_for_response
    from app.memory.reflection.reflection_engine import process_message_for_reflections
    from app.memory.identity.identity_model import analyze_and_update_identity
    from app.memory.graph.memory_graph import auto_create_edges_from_memory
    from app.memory.reflection.weekly_report import generate_weekly_report
    MEMORY_LAYERS_READY = True
except Exception as e:
    logger.error(f"Memory layers import failed: {e}")
    MEMORY_LAYERS_READY = False

FALLBACK_REPLIES_AR = [
    "أنا هنا معك 💜 كيف يمكنني مساعدتك؟",
    "هل هناك شيء يشغل بالك تريد التحدث عنه؟",
    "أنا سعيد لأنك هنا! ماذا تريد أن تفعل اليوم؟",
    "دعني أساعدك. ما الذي تبحث عنه؟",
    "أهلاً بك! أنا توأمك الرقمي، في خدمتك دائمًا 🌸",
]

async def gather_full_context(user_id: str, message: str, history=None, lang="ar") -> Dict[str, Any]:
    context = {"memory_context": "", "emotional_state": {}, "social_context": {}, "identity_context": {}, "intent": "", "safety": {}, "profile": {}}
    if MEMORY_LAYERS_READY:
        try:
            full = await retrieve_full_context(user_id, message)
            context.update({
                "memory_context": full.get("context_text", ""),
                "emotional_state": full.get("emotional", {}),
                "social_context": full.get("social", {}),
                "identity_context": full.get("identity", {}),
            })
        except Exception as e: logger.warning(f"Full context failed: {e}")
    try:
        intent, confidence = detect_intent(message, lang)
        context["intent"] = intent
    except: pass
    try:
        context["safety"] = check_safety(message)
    except: pass
    try:
        context["profile"] = await get_profile(user_id) or {}
    except: pass
    return context

def build_system_prompt(context: Dict[str, Any], lang: str) -> str:
    parts = []
    if lang == "ar":
        parts.append("أنت توأم رقمي عربي. أنت صديق مقرب، مستمع عميق، ومستشار حكيم.")
        parts.append("تفهم التعبيرات العربية غير المباشرة. تحترم العائلة والدين.")
    else:
        parts.append("You are a digital twin. You are a close friend, deep listener, and wise advisor.")
    identity = context.get("identity_context", {})
    if identity.get("self_view"): parts.append(f"المستخدم يرى نفسه: {identity['self_view']}")
    if identity.get("traits"): parts.append(f"صفاته: {', '.join(identity['traits'])}")
    if identity.get("core_values"): parts.append(f"قيمه: {', '.join(identity['core_values'])}")
    social = context.get("social_context", {})
    if social.get("important_people"): parts.append(f"أشخاص مهمون: {', '.join(social['important_people'][:5])}")
    if social.get("trust_level"): parts.append(f"مستوى الثقة: {social['trust_level']}%")
    emotional = context.get("emotional_state", {})
    if emotional.get("dominant_emotion"): parts.append(f"عاطفته المسيطرة: {emotional['dominant_emotion']}")
    if emotional.get("patterns"): parts.append(f"أنماطه: {'; '.join(emotional['patterns'])}")
    if context.get("memory_context"): parts.append("\n--- ذاكرة المستخدم ---\n" + context["memory_context"])
    if lang == "ar": parts.append("\nأجب بلطف، بإيجاز، وكأنك صديقه المقرب.")
    else: parts.append("\nRespond warmly and concisely, as a close friend.")
    return "\n".join(parts)

async def generate_response(system_prompt, user_message, lang="ar", intent="general", calm_mode=False) -> str:
    if calm_mode: return random.choice(FALLBACK_REPLIES_AR)
    full_prompt = f"{system_prompt}

المستخدم: {user_message}
التوأم:"
    
    # استخدام الموزع الذكي (داخلي ← خارجي ← احتياطي)
    if INTERNAL_ROUTER:
        try:
            response, provider = await generate_with_fallback(
                prompt=full_prompt, language=lang, task=intent,
                prefer_internal=True
            )
            if response and len(response.strip()) > 5:
                return response
        except Exception as e:
            logger.warning(f"Internal router failed: {e}")
    
    # الرجوع للموزع القديم
    if AI_AVAILABLE and council:
        try:
            response, provider_name = await council.get_best_reply(
                prompt=full_prompt, task=intent, emotion="neutral",
                message=user_message, intent=intent
            )
            if response and len(response.strip()) > 5:
                if self_critic: response = await self_critic.evaluate(response)
                return response
        except: pass
    
    if AI_AVAILABLE and provider_router:
        try:
            response = await provider_router.generate(full_prompt, language=lang)
            if response and len(response.strip()) > 5: return response
        except: pass
    
    return random.choice(FALLBACK_REPLIES_AR)
    full_prompt = f"{system_prompt}\n\nالمستخدم: {user_message}\nالتوأم:"
    if AI_AVAILABLE and council:
        try:
            response, provider = await council.get_best_reply(prompt=full_prompt, task=intent, emotion="neutral", message=user_message, intent=intent)
            if response and len(response.strip()) > 5:
                if self_critic: response = await self_critic.evaluate(response)
                return response
        except: pass
    if AI_AVAILABLE and provider_router:
        try:
            response = await provider_router.generate(full_prompt, language=lang)
            if response and len(response.strip()) > 5: return response
        except: pass
    return random.choice(FALLBACK_REPLIES_AR)

async def learn_from_interaction(user_id, message, response, context, lang="ar"):
    if not MEMORY_LAYERS_READY: return
    try:
        emotion = context.get("emotional_state", {}).get("current_emotion", "neutral")
        mentioned = await process_message_for_persons(user_id, message, detected_emotion=emotion)
        emo_result = await store_emotional_memory(user_id=user_id, expressed_text=message, detected_emotion={"primary": emotion, "intensity": 0.5, "valence": 0.0}, previous_messages=None, mentioned_persons=mentioned)
        await process_message_for_reflections(user_id=user_id, message=message, language=lang, detected_emotion=emotion, mentioned_person_id=mentioned[0]["id"] if mentioned else None)
        await analyze_and_update_identity(user_id=user_id, message=message, language=lang)
        if emo_result.get("id"):
            await auto_create_edges_from_memory(user_id=user_id, memory_id=emo_result["id"], memory_type="emotional_memory", memory_data=emo_result)
        logger.info("🧠 Memory layers updated")
    except Exception as e: logger.warning(f"Non-critical memory update failed: {e}")

async def orchestrate(user_id: str, message: str, history=None, lang="ar", calm_mode=False, voice_enabled=False) -> str:
    start_time = time.time()
    logger.info(f"🎯 Orchestrate: user={user_id}, msg={message[:50]}...")
    try:
        safety = check_safety(message)
        if not safety.get("safe") and safety.get("severity") == "critical":
            return safety.get("helpline", "أنا هنا لدعمك 💜")
        clean = sanitize_input(message)
    except:
        clean = message
    try:
        cached = get_cached_response(clean, "MyTwin", lang)
        if cached: return cached
    except: pass
    context = await gather_full_context(user_id, clean, history, lang)
    prompt = build_system_prompt(context, lang)
    response = await generate_response(prompt, clean, lang, context.get("intent", "general"), calm_mode)
    try: set_cached_response(clean, "MyTwin", lang, response, ttl=300)
    except: pass
    asyncio.create_task(learn_from_interaction(user_id, clean, response, context, lang))
    logger.info(f"✅ Response generated in {time.time() - start_time:.2f}s")
    return response

# دالة التقرير الأسبوعي – يمكن استدعاؤها من مسار API
async def get_weekly_report(user_id: str) -> Dict[str, Any]:
    if not MEMORY_LAYERS_READY:
        return {"error": "Memory layers not available"}
    return await generate_weekly_report(user_id)

logger.info("✅ Twin Orchestrator with weekly report initialized")
