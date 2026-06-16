import os, random, logging, time, asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from multi_ai import MultiAIClient, AIUnavailable
from emotional_engine import EmotionalStateTracker
from dialect_engine import get_dialect_for_user, get_dialect_prompt
from reasoning_engine import ReasoningEngine
from memory_graph import store_mem, extract_entities
from relationship_engine import RelationshipEngine
from prompt_builder import PromptBuilder
from consciousness_core import ConsciousnessCore
from growth_tracker import track_growth
from twin_journey import twin_journey
from attachment_engine import attachment_engine
from safety_engine import safety_engine
from product_recommender import product_recommender
from tools.tool_router import tool_router
from context_manager import context_manager
from tools.agent_loop import agent_loop
from response_validator import response_validator
from response_engine import response_engine
from tools.final_synthesizer import final_synthesizer
from memory_summarizer import memory_summarizer
from tools.agent_metrics import agent_metrics
from model_router import model_router
from llm_council import LLMCouncil
from self_critic import SelfCritic
from profile_extractor import profile_extractor

logger = logging.getLogger("twin_brain")

class TwinBrain:
    FALLBACK_REPLIES = [
        "والله إني معاك، كمل كلامك متوقفش 💜",
        "حاسس بيك، إيه اللي شاغل بالك بالظبط؟",
        "يا صاحبي أنا جنبك، قولي كل حاجة 🫶",
        "أنا سامعك، وعارف إنك تقدر تعدي أي حاجة ✨",
        "أفهمك والله، أنا معاك في اللي بتمر بيه 💜",
        "كلامك مهم جداً بالنسبة لي، كمّل 🌸",
    ]

    def __init__(self, gemini_key=None):
        self.multi = MultiAIClient()
        self.emotion_tracker = EmotionalStateTracker()
        self.reasoning_engine = ReasoningEngine()
        self.relationship = RelationshipEngine()
        self.prompt_builder = PromptBuilder()
        self.consciousness = ConsciousnessCore(twin_name="MyTwin")
        self.twin_name = "MyTwin"
        self.user_join_dates = {}
        self.self_critic = SelfCritic()
        self.council = LLMCouncil(self.multi)

    async def health_check_all_providers(self) -> Dict[str, bool]:
        return await self.multi.health_check()

    async def detect_emotion(self, text: str) -> Dict[str, Any]:
        return await self.emotion_tracker.analyze(text)

    async def respond(self, message, twin_name, bond_level, dims, memories, history,
                      calm=False, personality=None, country_code="SA", user_id=None, tier="free",
                      join_date=None, recent_messages=None, user_profile=None):

        # 1. الفحص الأمني
        safety_check = safety_engine.check_safety(message)
        if not safety_check["safe"] and safety_check["severity"] == "critical":
            return {
                "reply": safety_engine.HELPLINE_MESSAGE, "new_bond": bond_level,
                "emotion": {"primary": "concern", "intensity": 1.0}, "provider": "safety_engine",
                "latency_ms": 0, "dialect": get_dialect_for_user(country_code, message), "safety_alert": True
            }

        # 2. تحليل المشاعر واللغة
        emotion = await self.detect_emotion(message)
        dialect = get_dialect_for_user(country_code, message)
        dialect_prompt = get_dialect_prompt(dialect)

        # 2.5 طبقة اكتشاف النية السريعة (Quick Intent Detection)
        quick_intent, intent_conf = self.relationship.detect_intent(message, lang="ar")
        if quick_intent != "general" and intent_conf > 0.7:
            logger.info(f"⚡ Quick Intent Detected: {quick_intent} (confidence: {intent_conf:.2f})")

        # 3. الأدوات - نجمع النتائج فقط
        tool_context = ""
        tool_results = []
        if user_id:
            try:
                tool_result = await tool_router.route(
                    message=message, user_id=user_id, tier=tier, emotion=emotion
                )
                if tool_result:
                    logger.info(f"🔧 أداة سريعة: {tool_result[:100]}...")
                    tool_context = f"<TOOL_RESULT>\n{tool_result}\n</TOOL_RESULT>"
                    tool_results.append(tool_result)
                    await agent_metrics.log_tool_execution(
                        user_id=user_id, tool_name="tool_router", success=True,
                        latency_ms=0, input_query=message[:100], output_summary=tool_result[:100]
                    )
            except Exception as e:
                logger.warning(f"Tool routing failed: {e}")

        # 4. بناء السياق
        full_context = {}
        context_summary = ""
        if user_id:
            try:
                full_context = await context_manager.build_context(
                    user_id=user_id, message=message, emotion=emotion,
                    history=history, lang="ar", tier=tier, user_profile=user_profile
                )
                if hasattr(context_manager, 'build_context_summary'):
                    context_summary = context_manager.build_context_summary(full_context)
                else:
                    context_summary = full_context.get("planner_summary", "")
            except Exception as e:
                logger.warning(f"Context building failed: {e}")

        # 5. Feedback loop
        last_feedback = ""
        if user_id:
            try:
                from supabase import create_client
                _db = create_client(os.getenv("SUPABASE_URL",""), os.getenv("SUPABASE_SERVICE_KEY",""))
                fb = _db.table("message_feedback").select("rating").eq("user_id", user_id).eq("rating","dislike").order("created_at", desc=True).limit(1).execute()
                if fb.data:
                    last_feedback = "\n⚠️ تنبيه: المستخدم لم يُعجبه آخر رد — تجنب نفس الأسلوب والطول والنبرة."
                    logger.info("📊 Feedback Loop: dislike detected")
            except Exception as e:
                logger.warning(f"Feedback fetch failed: {e}")

        # 6. تحديث العلاقة (مع تفعيل stage-up message)
        journey_info = {}
        attachment_info = {}
        stage_up_message = None
        if user_id:
            try:
                if join_date:
                    journey_info = await twin_journey.get_daily_activity(user_id, join_date)
                if recent_messages:
                    emotion_history = [emotion] if emotion else []
                    memory_context_data = {"memories": full_context.get("memories", [])}
                    attachment_info = await attachment_engine.detect_attachment_style(
                        user_id=user_id, messages=recent_messages,
                        emotion_history=emotion_history, memory_context=memory_context_data
                    )
                else:
                    attachment_info = {"style": "unknown", "confidence": 0.0}
                stage_up_message = self.relationship.update(
                    emotion=emotion, message=message,
                    journey_phase=journey_info.get("phase") if journey_info else None,
                    attachment_style=attachment_info.get("style") if attachment_info else None,
                    memory_importance=emotion.get("intensity", 0.5)
                )
                if stage_up_message:
                    logger.info(f"🎉 Stage Up! Message: {stage_up_message}")
            except Exception as e:
                logger.warning(f"Relationship update failed: {e}")

        # 7. التخطيط
        plan = {}
        if user_id:
            try:
                plan = await self.reasoning_engine.create_execution_plan(
                    message=message, emotion=emotion, user_id=user_id,
                    lang="ar", context_summary=context_summary, tier=tier
                )
            except Exception as e:
                logger.warning(f"Planning failed: {e}")
                plan = {"needs_tool": False, "goal": "general_chat"}

        final_reply = None
        provider = "multi_ai"
        latency = 0

        # 8. Agent Loop (أدوات معقدة)
        if plan.get("needs_tool") and plan.get("tool_confidence", 0) >= 0.6:
            try:
                logger.info(f"🤖 بدء Agent Loop للأداة: {plan.get('primary_tool')}")
                agent_start_time = time.time()
                agent_response = await agent_loop.execute(
                    plan=plan, user_id=user_id, message=message, emotion=emotion,
                    twin_brain_instance=self, context_summary=context_summary, lang="ar"
                )
                agent_latency = (time.time() - agent_start_time) * 1000
                if agent_response and agent_response.get("reply"):
                    final_reply = agent_response.get("reply")
                    provider = agent_response.get("provider", "agent_loop")
                    tool_results = agent_response.get("tool_results", [])
                    await agent_metrics.log_tool_execution(
                        user_id=user_id,
                        tool_name=f"agent_loop_{plan.get('primary_tool', 'unknown')}",
                        success=True, latency_ms=agent_latency,
                        input_query=message[:100], output_summary=final_reply[:100]
                    )
            except Exception as e:
                logger.error(f"Agent loop failed: {e}")

        # 9. بناء الـ Prompt للـ LLM
        if not final_reply:
            rel_stage = self.relationship.get_stage_instruction()
            if isinstance(rel_stage, dict):
                relationship_for_prompt = {
                    "label": rel_stage.get("label", "Friend"),
                    "bond_level": rel_stage.get("bond_level", bond_level),
                    "instruction": rel_stage.get("instruction", "Be supportive.")
                }
            else:
                relationship_for_prompt = {
                    "label": "Friend", "bond_level": bond_level, "instruction": str(rel_stage)
                }

            if attachment_info and attachment_info.get("style") != "unknown":
                att_style = attachment_info.get("style")
                att_confidence = attachment_info.get("confidence", 0)
                if att_confidence > 0.4:
                    att_adjustments = attachment_engine.get_response_adjustments(att_style)
                    relationship_for_prompt["attachment_style"] = att_style
                    relationship_for_prompt["attachment_guidance"] = att_adjustments

            formatted_context = context_manager.format_context_for_prompt(full_context) + last_feedback
            
            if tool_results:
                formatted_context = "<TOOL_RESULTS>\n" + "\n".join(tool_results) + "\n</TOOL_RESULTS>\n\n" + formatted_context
            
            if tool_context:
                formatted_context = tool_context + "\n\n" + formatted_context

            if not context_summary:
                context_summary = formatted_context[:500] if formatted_context else ""

            prompt = await self.prompt_builder.build(
                twin_name=twin_name, user_name="صديقي", relationship=relationship_for_prompt,
                emotion=emotion, voice={"style": "Warm", "pitch": 1.0, "rate": 1.0},
                dialect={"dialect": dialect, "instruction": dialect_prompt},
                user_id=user_id, journey_info=journey_info,
                attachment_info=attachment_info,
                response_adjustments=attachment_engine.get_response_adjustments(attachment_info.get("style", "unknown")),
                message=message,
                memory_context=formatted_context,
                reasoning_result=plan,
                consciousness_context=full_context.get("consciousness", {}),
                history=history,
            )

            task_type = plan.get("response_style", "general")
            start = time.time()
            try:
                reply, provider = await self.council.get_best_reply(
                    prompt=prompt,
                    task_type=task_type,
                    emotion_primary=emotion.get("primary", "neutral"),
                    message=message,
                    context=formatted_context,
                    multi_client=self.multi
                )
            except AIUnavailable:
                reply = random.choice(self.FALLBACK_REPLIES)
                provider = "fallback"
            except Exception as e:
                logger.error(f"Council failed: {e}")
                reply = random.choice(self.FALLBACK_REPLIES)
                provider = "fallback"
            latency = (time.time() - start) * 1000

            final_reply = reply

        # 10. Self-critic
        try:
            if final_reply and len(final_reply) > 10:
                final_reply = await self.self_critic.evaluate_and_repair(
                    reply=final_reply,
                    context=context_summary,
                    multi_client=self.multi
                )
        except Exception as e:
            logger.warning(f"Self-critic failed: {e}")

        # 11. Response validator
        validation = response_validator.validate(
            reply=final_reply,
            context=full_context,
            tool_results=tool_results,
            emotion=emotion
        )
        if validation.get("repaired"):
            logger.info(f"🔧 Response repaired: {validation.get('issues')}")
            final_reply = validation.get("final_reply", final_reply)
        if not validation.get("valid", True):
            final_reply = "أنا هنا لدعمك، لكن لا يمكنني الرد على هذا. 💜"
            provider = "safety_validator"

        # 12. Final Synthesizer (طبقة الدمج النهائية)
        try:
            final_reply = await final_synthesizer.synthesize(
                user_message=message,
                tool_results=tool_results,
                memory_context=formatted_context if 'formatted_context' in dir() else "",
                llm_reply=final_reply,
                plan=plan,
                emotion=emotion,
                lang="ar"
            )
        except Exception as e:
            logger.warning(f"Final synthesizer failed: {e}")

        # 13. تنسيق الرد النهائي
        final_reply = response_engine.process(
            final_reply,
            intent=plan.get("response_style", "general"),
            lang="ar"
        )

        # 14. إضافة رسالة مرحلة العلاقة (Stage-Up Message) في بداية الرد
        if stage_up_message:
            stage_up_text = stage_up_message.get("ar", "") if isinstance(stage_up_message, dict) else ""
            if stage_up_text:
                final_reply = f"🎉 **{stage_up_text}**\n\n{final_reply}"

        # 15. المهام الخلفية
        if user_id:
            asyncio.create_task(store_mem(user_id, message, emotion.get("intensity", 0.5), emotion.get("primary", "neutral")))
            asyncio.create_task(extract_entities(user_id, message))
            asyncio.create_task(track_growth(user_id, {"journey_phase": journey_info.get("phase", "unknown"), "attachment_style": attachment_info.get("style", "unknown"), "emotion": emotion.get("primary", "neutral")}))

            await memory_summarizer.increment_counter(user_id)
            if await memory_summarizer.should_summarize(user_id):
                asyncio.create_task(memory_summarizer.summarize_and_store(user_id=user_id, messages=history or [], twin_brain_instance=self))

            await profile_extractor.increment_counter(user_id)
            if await profile_extractor.should_extract(user_id):
                logger.info(f"📝 استخراج شخصية المستخدم {user_id}")
                user_messages = [h.get("content", "") for h in (history or [])[-30:] if h.get("role") == "user"]
                if user_messages:
                    asyncio.create_task(
                        profile_extractor.extract_from_conversation(
                            messages=user_messages,
                            multi_client=self.multi,
                            user_id=user_id
                        )
                    )
                await profile_extractor.reset_counter(user_id)

            asyncio.create_task(self.consciousness.update_user_profile(user_id, {
                "relationship_dims": self.relationship.dims,
                "journey_phase": journey_info.get("phase"),
                "journey_day": journey_info.get("day"),
                "attachment_style": attachment_info.get("style"),
                "bond_level": self.relationship.bond_level,
            }))

            if self.relationship.bond_level > 30:
                asyncio.create_task(self.consciousness.reflect(user_id=user_id, conversation_summary=message[:200], lang="ar"))

        return {
            "reply": final_reply,
            "new_bond": self.relationship.bond_level,
            "emotion": emotion,
            "provider": provider,
            "latency_ms": latency,
            "dialect": dialect,
            "journey_phase": journey_info.get("phase", "unknown"),
            "journey_day": journey_info.get("day", 1),
            "attachment_style": attachment_info.get("style", "unknown"),
            "relationship_dims": self.relationship.dims
        }

twin_brain = TwinBrain()
