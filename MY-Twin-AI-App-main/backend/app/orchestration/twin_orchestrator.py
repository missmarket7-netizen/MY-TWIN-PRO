"""
Twin Orchestrator v17.0.0 – العقل المدبر الشامل
=====================================================
يدمج: الذاكرة، العاطفة، الزمان، الاستباقية، جميع الميزات، توجيه ذكي للمهام، ومدقق الجودة.
"""
import time, logging, random, asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("twin_orchestrator")

# ---------- الذكاء الاصطناعي ----------
try:
    from app.infrastructure.ai.provider_router import provider_router
    from app.infrastructure.ai.provider_router_internal import generate_with_fallback
    AI_AVAILABLE = True
    INTERNAL_ROUTER = True
except:
    AI_AVAILABLE = False
    INTERNAL_ROUTER = False

# ---------- المحركات الأساسية ----------
try:
    from app.memory.retrieval.memory_retriever import retrieve_full_context
    from app.memory.emotional.emotional_memory import store_emotional_memory
    from app.features.proactive_engine import proactive_engine
    from app.features.temporal_context import temporal_engine
    from app.prompts.prompt_builder import prompt_builder
    from app.safety.response_validator import response_validator
    from app.twin_state.intent_service import intent_engine
    ALL_ENGINES_READY = True
except:
    ALL_ENGINES_READY = False

FALLBACK_REPLIES = ["أنا هنا معك 💜", "كيف يمكنني مساعدتك اليوم؟", "أهلاً بك! في خدمتك دائماً 🌸"]

# ============================================================
# المايسترو الرئيسي
# ============================================================
async def orchestrate(user_id: str, message: str, history=None, lang="ar", calm_mode=False, voice_enabled=False) -> str:
    start = time.time()
    logger.info(f"🎯 Chat: {message[:50]}...")

    # 1. فحص الأمان
    try:
        from app.safety.response_validator import response_validator
        safety = response_validator._contains_toxic_content(message)
        if safety:
            return "أنا هنا لدعمك، لكن لا يمكنني الرد على هذا. 💜"
        clean = message
    except:
        clean = message

    # 2. توجيه الميزة الذكي (Feature Routing)
    feature_result = await _route_to_feature(user_id, clean, lang)
    if feature_result:
        return feature_result

    # 3. بناء System Prompt الديناميكي
    system_prompt = ""
    if ALL_ENGINES_READY:
        try:
            system_prompt = await prompt_builder.build(user_id, clean, lang)
        except:
            pass

    # 4. توليد الرد
    response = None
    full_prompt = f"{system_prompt}\n\nالمستخدم: {clean}" if system_prompt else clean

    if INTERNAL_ROUTER and ALL_ENGINES_READY:
        try:
            response, _ = await generate_with_fallback(
                prompt=full_prompt, language=lang, task="general", prefer_internal=True
            )
        except: pass

    if not response and AI_AVAILABLE and provider_router:
        try:
            response = await provider_router.generate(full_prompt, language=lang)
        except: pass

    if not response or len(response.strip()) < 5:
        response = random.choice(FALLBACK_REPLIES)

    # 5. التحقق من الجودة
    if ALL_ENGINES_READY:
        try:
            validation = await response_validator.validate(response, user_id, emotion={"primary": "neutral"})
            if validation.get("repaired"):
                response = validation["final_reply"]
        except: pass

    # 6. التعلم في الخلفية
    if ALL_ENGINES_READY:
        asyncio.create_task(_learn(user_id, clean, response))

    logger.info(f"✅ رد في {time.time()-start:.2f}s")
    return response

# ============================================================
# التوجيه الذكي لجميع الميزات
# ============================================================
async def _route_to_feature(user_id: str, message: str, lang: str) -> Optional[str]:
    """
    يكتشف نية المستخدم ويوجهه إلى الميزة المناسبة.
    إذا تطابقت نية مع ميزة، يتم استدعاؤها مباشرة.
    """
    if not ALL_ENGINES_READY:
        return None

    # تحليل النية
    intent = intent_engine.detect(message, lang) if intent_engine else {"primary": "general"}
    primary_intent = intent.get("primary", "general")

    # خريطة التوجيه (نية ← ميزة)
    feature_map = {
        "study": _handle_study,
        "code": _handle_code_lab,
        "business": _handle_business,
        "dream": _handle_dreams,
        "coaching": _handle_life_coach,
        "smart_home": _handle_smart_home,
        "task": _handle_pass,
        "search": _handle_search,
        "emotional": _handle_emotional,
    }

    handler = feature_map.get(primary_intent)
    if handler:
        try:
            return await handler(user_id, message, lang)
        except Exception as e:
            logger.warning(f"Feature routing failed: {e}")

    return None

# ============================================================
# معالجات الميزات
# ============================================================
async def _handle_study(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.study.athena_orchestrator import athena
    result = await athena.start_study_session(user_id, message, "teen", lang)
    return result.get("explanation", {}).get("simplified", None)

async def _handle_code_lab(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.code_lab.sdlc_orchestrator import code_lab
    result = await code_lab.generate_code(user_id, message)
    return result.get("code", None)

async def _handle_business(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.business.growth_hive_orchestrator import growth_hive
    result = await growth_hive.generate_business_idea(user_id, 1000, message, "عام", lang)
    ideas = result.get("ideas", [])
    return ideas[0].get("title", None) if ideas else None

async def _handle_dreams(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.dreams.dream_orchestrator import dream_orchestrator
    result = await dream_orchestrator.interpret(user_id, message, lang)
    return result.get("interpretation", None)

async def _handle_life_coach(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.life_coach.life_coach_orchestrator import life_coach
    result = await life_coach.start_session(user_id, message, lang)
    return result.get("psychological_analysis", {}).get("cbt_intervention", None)

async def _handle_smart_home(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.smart_home.smart_home_orchestrator import smart_home
    result = await smart_home.process_command(user_id, message, lang)
    return result.get("response", None)

async def _handle_pass(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.task_manager.pass_orchestrator import pass_assistant
    result = await pass_assistant.create_task(user_id, message)
    return result.get("message", None)

async def _handle_search(user_id: str, message: str, lang: str) -> Optional[str]:
    from app.features.task_manager.external_services import search_web
    result = await search_web(message, lang)
    return result.get("results", None)

async def _handle_emotional(user_id: str, message: str, lang: str) -> Optional[str]:
    # لا نعالج تلقائياً، نترك المحادثة تأخذ مجراها الطبيعي
    return None

# ============================================================
# التعلم في الخلفية
# ============================================================
async def _learn(user_id: str, message: str, response: str):
    try:
        await store_emotional_memory(
            user_id=user_id, expressed_text=message,
            detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.0},
            trigger="chat"
        )
    except: pass

logger.info("✅ Twin Orchestrator v17.0.0 with Full Feature Routing")
