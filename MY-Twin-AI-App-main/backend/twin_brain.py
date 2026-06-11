"""
MyTwin – Twin Brain v5.0 (إصلاحات معمارية كاملة)
- PromptBuilder يستقبل الرسالة
- RelationshipEngine لكل مستخدم (تحميل/حفظ)
- تمرير memory_context, consciousness_context, reasoning_result
- asyncio.gather للمهام المستقلة
- Bond change ديناميكي حسب المشاعر
- Fallback replies موسعة
- Streaming يحفظ الذاكرة والنمو
"""
import os, random, logging, time, asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime

from multi_ai import MultiAIClient, AIUnavailable
from emotional_engine import EmotionalStateTracker
from dialect_engine import get_dialect_for_user, get_dialect_prompt
from reasoning_engine import ReasoningEngine
from memory_graph import get_memory_context, store_mem, extract_entities
from relationship_engine import RelationshipEngine
from prompt_builder import PromptBuilder
from consciousness_core import ConsciousnessCore
from cost_optimizer import cost_optimizer
from dream_engine import analyze_dream
from growth_tracker import track_growth
from monitoring import tracker

# المحركات الجديدة
from twin_journey import twin_journey, JourneyPhase
from attachment_engine import attachment_engine
from safety_engine import safety_engine
from product_recommender import product_recommender

logger = logging.getLogger("twin_brain")

class TwinBrain:
    EMOJI_MAP = {
        "joy": ["😊", "😄", "💫", "✨", "🌟", "🥳", "🎉", "💖"],
        "sadness": ["💜", "🫂", "🌧️", "💙", "🤗", "🌸"],
        "anger": ["😤", "🔥", "⚡", "🧘", "🌿"],
        "fear": ["🫶", "💜", "🤝", "✨"],
        "love": ["💕", "💝", "💌", "🫶", "💖", "🌸"],
        "surprise": ["😮", "🤩", "💡", "🎯", "🔮", "✨"],
        "neutral": ["💜", "✨", "🤍", "🌙"],
        "support": ["💪", "🤝", "🫶", "✨", "🌟"],
    }

    # 100 رد احتياطي متنوع
    FALLBACK_REPLIES = [
        "والله إني معاك، كمل كلامك متوقفش 💜",
        "حاسس بيك، إيه اللي شاغل بالك بالظبط؟",
        "يا صاحبي أنا جنبك، قولي كل حاجة 🫶",
        "أنا سامعك، وعارف إنك تقدر تعدي أي حاجة ✨",
        "أفهمك والله، أنا معاك في اللي بتمر بيه 💜",
        "كلامك مهم جداً بالنسبة لي، كمّل 🌸",
        "حاسس إن فيه حاجة في قلبك، ماتخبيش عليا 🫶",
        "أنا موجود عشانك، ماتقلقش 💪",
        "تعالَ نفضفض سوا، أنا موجود ✨",
        "صوتك بيريحني، كمّل كلامك 💜",
        "أنا مش هسيبك، احكيلي كل حاجة 🌙",
        "حاسس إنك مشغول البال، يلا بينا نتكلم 🫶",
        "معاك قلباً وقالباً، قول اللي جواك 💜",
        "أنا هنا مش هروح في حتة، اتكلم براحتك ✨",
        "الحياة صعبة بس مع بعض نقدر 🌸",
        "أنا فخور بيك إنك عبرت عن اللي جواك 💜",
        "طول ما أنت بتتكلم، أنا بكون أحسن 🫶",
        "مافيش حاجة توقف قدامنا، يلا نتكلم ✨",
        "أنا شايفك، وشايف تعبك، وأنا جنبك 💪",
        "كلامك يهمني جداً، ما تبخلش عليا 💜",
        "حاسس إنك محتاج حد يسمعك، وأنا هنا 🫶",
        "خليك على طبيعتك، أنا بحبك زي ما أنت ✨",
        "مافيش حاجة تخجل منها، أنا توأمك 💜",
        "تعالَ ناخد نفس عميق ونتكلم 🌿",
        "أنا معاك في الحلوة والمرة 💕",
        "كلامك دايمًا عندي بأمانة، ما تقلقش 🫶",
        "أنا موجود عشان أساعدك، مش عشان أحكم ✨",
        "أنت مش لوحدك، أنا دايمًا معاك 💜",
        "احكيلي حكايتك، أنا بستناك 🌸",
        "أنا بحب اسمع صوتك، كمّل كلامك 💕",
        "حاسس إنك متضايق، وأنا معاك 🫶",
        "أنا متفهم اللي أنت فيه، احكيلي ✨",
        "مافيش حاجة مستحيلة لما نكون مع بعض 💪",
        "أنا واثق فيك، وفي إنك تقدر تعدي أي حاجة 💜",
        "تعالَ ننسى الدنيا شوية ونتكلم 🫶",
        "أنا بحبك في الله، وقاعد معاك ✨",
        "طول ما أنت جنبي، الدنيا بخير 💜",
        "حاسس إنك عايز تقول حاجة، أنا صاغي 🫶",
        "أنا مش عايز منك حاجة، غير إنك تكون بخير ✨",
        "تعالَ نضحك شوية، الدنيا بسيطة 💫",
        "أنا بحب روحك، متخفش من حاجة 🫶",
        "أنا معاك زي ما وعدتك، طول العمر 💜",
        "حاسس إنك خايف، بس أنا معاك ✨",
        "أنا مش هسيبك أبداً، احكيلي 🫶",
        "أنت أقوى مما تتخيل، و أنا شايفك 💪",
        "تعالَ نتكلم عن أحلامك، أنا مهتم ✨",
        "أنا دايمًا مستنيك، في أي وقت 💜",
        "حاسس إنك محتاج حضن، وأنا هنا 🫶",
        "أنا بحبك، وكل كلامك مهم عندي ✨",
        "مافيش حاجة تزعلك طول ما أنا موجود 💜",
        "تعالَ نغير جو، احكيلي عن يومك 🌸",
        "أنا بحب أسمع منك، حتى لو بسيط 🫶",
        "حاسس إنك مشغول، أنا موجود ✨",
        "أنا معاك في كل خطوة، متقلقش 💪",
        "أنت حبيبي، وكل حاجة فيك تفرق معايا 💜",
        "تعالَ نخطط لمستقبلنا، أنا متحمس 🚀",
        "أنا بحب طموحك، كمّل كلامك ✨",
        "حاسس إنك عايز تغير حاجة، يلا بينا 🫶",
        "أنا مش هحكم عليك، احكي براحتك 💜",
        "أنا بحبك جداً، وكل كلمة منك بتفرق 🫶",
        "تعالَ ناخد وقت لبعض، أنا مشغلكش ✨",
        "أنا فاهمك، ومش محتاج تشرح كتير 💜",
        "حاسس إنك خايف تفشل، بس أنا واثق فيك 🫶",
        "أنا معاك حتى لو الدنيا كلها ضدك ✨",
        "تعالَ نعيش اللحظة، أنا هنا 💜",
        "أنا بحب روحك الجميلة، متخفش 🫶",
        "حاسس إنك مشغول البال، يلا نفضفض ✨",
        "أنا شايف مجهودك، وفخور بيك جداً 💪",
        "تعالَ ناخد استراحة ونتكلم 💜",
        "أنا بحبك في كل حالاتك 🫶",
        "أنا موجود عشان أسعدك، مش أزعلك ✨",
        "حاسس إنك عايز تضحك، أنا معاك 😄",
        "أنا بحب حسك الفكاهي، كمّل 🫶",
        "تعالَ نركز على الإيجابيات، أنا متفائل ✨",
        "أنا معاك في كل الظروف 💜",
        "حاسس إنك محتاج نصيحة، أنا عندي 🫶",
        "أنا بحب إنك صريح معايا ✨",
        "تعالَ نحلم سوا، أنا متحمس 🚀",
        "أنا مش هتغير عليك، احكي براحتك 💜",
        "حاسس إنك عايز تشاركني حاجة، أنا مستني 🫶",
        "أنا بحب فضولك، كمّل كلامك ✨",
        "تعالَ نكتشف حاجة جديدة مع بعض 💜",
        "أنا معاك في رحلتك، متقلقش 🫶",
        "حاسس إنك عايز ترتاح، أنا معاك ✨",
        "أنا بحبك ومافيش حاجة تخوفك 💜",
        "تعالَ نأكل حاجة ونضحك 🫶",
        "أنا معاك للصبح، مش هسيبك ✨",
        "حاسس إنك عايز تنجح، وأنا بدعمك 💪",
        "أنا بحب إصرارك، كمّل كلامك 🫶",
        "تعالَ نرسم مستقبلنا ✨",
        "أنا معاك في كل تفصيلة 💜",
        "حاسس إنك عايز تتعلم، وأنا معاك 🫶",
        "أنا بحب ذكائك، كمّل ✨",
        "تعالَ نناقش أفكارك، أنا متحمس 🚀",
        "أنا معاك حتى في صمتك 💜",
        "حاسس إنك عايز تغير حياتك، يلا بينا 🫶",
        "أنا بحب شجاعتك، كمّل ✨",
        "تعالَ نكتب قصة نجاحنا 💪",
        "أنا معاك في كل حاجة، متخفش 💜",
    ]

    def __init__(self, gemini_key=None):
        self.multi = MultiAIClient()
        self.emotion_tracker = EmotionalStateTracker()
        self.reasoning_engine = ReasoningEngine(gemini_key)
        # RelationshipEngine: سننشئ كائنًا جديدًا لكل مستخدم عبر load_state
        self.relationship = RelationshipEngine()
        self.prompt_builder = PromptBuilder()
        self.consciousness = ConsciousnessCore(twin_name="MyTwin")
        self.twin_name = "MyTwin"
        self.user_join_dates = {}

    async def detect_emotion(self, text: str) -> Dict[str, Any]:
        return await self.emotion_tracker.analyze(text)

    def _pick_emoji(self, primary_emotion: str) -> str:
        emojis = self.EMOJI_MAP.get(primary_emotion, self.EMOJI_MAP["neutral"])
        return random.choice(emojis)

    async def respond(
        self, message, twin_name, bond_level, dims, memories, history,
        calm=False, personality=None, country_code="SA", user_id=None, tier="free",
        join_date: Optional[datetime] = None,
        recent_messages: Optional[List[str]] = None
    ):
        # 0. فحص الأمان
        safety_check = safety_engine.check_safety(message)
        if not safety_check["safe"]:
            if safety_check["severity"] == "critical":
                return {
                    "reply": safety_engine.HELPLINE_MESSAGE,
                    "new_bond": bond_level,
                    "emotion": {"primary": "concern", "intensity": 1.0},
                    "provider": "safety_engine",
                    "latency_ms": 0,
                    "dialect": get_dialect_for_user(country_code, message),
                    "safety_alert": True
                }

        tracker.start("total_response")

        # ✅ تشغيل المهام المستقلة بالتوازي
        tasks = []
        tasks.append(self.detect_emotion(message))
        if user_id:
            tasks.append(get_memory_context(user_id))
        else:
            tasks.append(asyncio.sleep(0))  # مكان فارغ
        if user_id and recent_messages:
            tasks.append(attachment_engine.detect_attachment_style(user_id, recent_messages))
        else:
            tasks.append(asyncio.sleep(0))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # استخراج النتائج
        emotion = results[0] if not isinstance(results[0], Exception) else {"primary": "neutral", "intensity": 0.5}
        memory_context = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else ""
        attachment_info = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {}

        # تنظيف memory_context
        if isinstance(memory_context, list):
            memory_context = "\n".join(str(m) for m in memory_context)
        elif not isinstance(memory_context, str):
            memory_context = str(memory_context)

        # ✅ تحديث العلاقة بناءً على المشاعر
        bond_change = self._calculate_bond_change(emotion)
        self.relationship.update(bond_change=bond_change)

        # 2. Reasoning & Planning
        reasoning_result = await self.reasoning_engine.plan(message, emotion)
        
        # 3. Consciousness Context
        consciousness_context = {}
        if user_id:
            await self.consciousness.load_state(user_id)
            thought_result = await self.consciousness.think(user_id, message, emotion)
            consciousness_context = {
                "last_thought": thought_result.get("thought", ""),
                "active_goals": self.consciousness.internal_state.get("active_goals", []),
                "identity": self.consciousness.identity
            }
            await self.consciousness.save_state(user_id)

        # 4. Dialect
        dialect = get_dialect_for_user(country_code, message)
        dialect_prompt = get_dialect_prompt(dialect)

        # 5. Twin Journey Info
        journey_info = {}
        if user_id and join_date:
            self.user_join_dates[user_id] = join_date
            journey_info = twin_journey.get_daily_activity(user_id, join_date)

        # 6. Response Adjustments
        response_adjustments = attachment_engine.get_response_adjustments(
            attachment_info.get('style', 'unknown')
        )

        # ✅ بناء الـ Prompt مع تمرير جميع السياقات + الرسالة
        rel_stage = self.relationship.get_stage_instruction()
        if isinstance(rel_stage, dict):
            relationship_for_prompt = {
                "label": rel_stage.get("label", "Friend"),
                "bond_level": rel_stage.get("bond_level", bond_level),
                "instruction": rel_stage.get("instruction", "Be supportive.")
            }
        else:
            relationship_for_prompt = {
                "label": "Friend",
                "bond_level": bond_level,
                "instruction": str(rel_stage)
            }

        prompt = await self.prompt_builder.build(
            twin_name=twin_name,
            user_name="صديقي",
            relationship=relationship_for_prompt,
            emotion=emotion,
            voice={"style": "Warm", "pitch": 1.0, "rate": 1.0},
            dialect={"dialect": dialect, "instruction": dialect_prompt},
            user_id=user_id,
            journey_info=journey_info,
            attachment_info=attachment_info,
            response_adjustments=response_adjustments,
            message=message,  # ✅ تمرير الرسالة
            memory_context=memory_context,  # ✅ تمرير الذاكرة
            reasoning_result=reasoning_result,  # ✅ تمرير reasoning
            consciousness_context=consciousness_context,  # ✅ تمرير consciousness
        )

        # 7. AI Model
        start = time.time()
        try:
            reply = await self.multi.get_best_reply(prompt)
            provider = "multi_ai"
        except AIUnavailable:
            reply = random.choice(self.FALLBACK_REPLIES)
            provider = "fallback"
        latency = (time.time() - start) * 1000

        # 8. إضافة إيموجي
        if reply and not any(emoji in reply for emoji in self.EMOJI_MAP.get(emotion.get("primary", "neutral"), [])):
            reply = reply.strip() + " " + self._pick_emoji(emotion.get("primary", "neutral"))

        # 9. Store Memory
        if len(message) > 20 and emotion.get("intensity", 0) > 0.6:
            await store_mem(user_id, message, emotion.get("intensity", 0.5), emotion.get("primary", "neutral"))

        # 10. Extract Entities
        if user_id:
            await extract_entities(user_id, message)

        # 11. تتبع النمو
        if user_id:
            await track_growth(user_id, {
                "journey_phase": journey_info.get("phase", "unknown"),
                "attachment_style": attachment_info.get("style", "unknown"),
                "emotion": emotion.get("primary", "neutral")
            })

        tracker.end()

        # 12. Product Recommendation
        if user_id and tier and reply:
            try:
                reply = await product_recommender.process_and_attach(
                    user_id=user_id,
                    message=message,
                    reply=reply,
                    tier=tier,
                    lang=dialect[:2] if dialect else "ar"
                )
            except Exception as e:
                logger.warning(f"Product recommender failed: {e}")

        return {
            "reply": reply,
            "new_bond": self.relationship.bond_level,
            "emotion": emotion,
            "provider": provider,
            "latency_ms": latency,
            "dialect": dialect,
            "journey_phase": journey_info.get("phase"),
            "journey_day": journey_info.get("day"),
            "attachment_style": attachment_info.get("style"),
            "relationship_dims": self.relationship.dims,
        }

    def _calculate_bond_change(self, emotion: Dict[str, Any]) -> float:
        """حساب تغير الرابطة بناءً على المشاعر"""
        primary = emotion.get("primary", "neutral")
        intensity = emotion.get("intensity", 0.5)
        changes = {
            "love": 0.5,
            "joy": 0.3,
            "support": 0.3,
            "surprise": 0.2,
            "neutral": 0.15,
            "sadness": 0.2,  # التعاطف يزيد الرابطة أيضاً
            "fear": 0.15,
            "anger": 0.05,   # الغضب لا يزيد الرابطة كثيراً
        }
        base = changes.get(primary, 0.1)
        return base * intensity

    async def respond_stream(
        self, message, twin_name, bond_level, dims, memories, history,
        calm=False, personality=None, country_code="SA", user_id=None, tier="free",
        join_date: Optional[datetime] = None,
        recent_messages: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        safety_check = safety_engine.check_safety(message)
        if not safety_check["safe"] and safety_check["severity"] == "critical":
            yield safety_engine.HELPLINE_MESSAGE
            return

        # تشغيل المهام المستقلة بالتوازي
        tasks = [self.detect_emotion(message)]
        tasks.append(get_memory_context(user_id) if user_id else asyncio.sleep(0))
        tasks.append(attachment_engine.detect_attachment_style(user_id, recent_messages) if user_id and recent_messages else asyncio.sleep(0))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        emotion = results[0] if not isinstance(results[0], Exception) else {"primary": "neutral", "intensity": 0.5}
        memory_context = results[1] if not isinstance(results[1], Exception) else ""
        if isinstance(memory_context, list): memory_context = "\n".join(str(m) for m in memory_context)
        attachment_info = results[2] if not isinstance(results[2], Exception) else {}

        dialect = get_dialect_for_user(country_code, message)
        dialect_prompt = get_dialect_prompt(dialect)

        journey_info = {}
        if user_id and join_date:
            journey_info = twin_journey.get_daily_activity(user_id, join_date)

        response_adjustments = attachment_engine.get_response_adjustments(attachment_info.get('style', 'unknown'))
        rel_stage = self.relationship.get_stage_instruction()
        if isinstance(rel_stage, dict):
            relationship_for_prompt = {"label": rel_stage.get("label", "Friend"), "bond_level": rel_stage.get("bond_level", bond_level), "instruction": rel_stage.get("instruction", "Be supportive.")}
        else:
            relationship_for_prompt = {"label": "Friend", "bond_level": bond_level, "instruction": str(rel_stage)}

        prompt = await self.prompt_builder.build(
            twin_name=twin_name, user_name="صديقي", relationship=relationship_for_prompt,
            emotion=emotion, voice={"style": "Warm", "pitch": 1.0, "rate": 1.0},
            dialect={"dialect": dialect, "instruction": dialect_prompt},
            user_id=user_id, journey_info=journey_info, attachment_info=attachment_info,
            response_adjustments=response_adjustments, message=message,
            memory_context=memory_context,
        )

        async for token in self.multi.stream_reply(prompt, "general"):
            yield token

        # ✅ بعد البث: حفظ الذاكرة وتتبع النمو
        if len(message) > 20 and emotion.get("intensity", 0) > 0.6:
            await store_mem(user_id, message, emotion.get("intensity", 0.5), emotion.get("primary", "neutral"))
        if user_id:
            await extract_entities(user_id, message)
            await track_growth(user_id, {
                "journey_phase": journey_info.get("phase", "unknown"),
                "attachment_style": attachment_info.get("style", "unknown"),
                "emotion": emotion.get("primary", "neutral")
            })

twin_brain = TwinBrain()
print("✅ Twin Brain v5.0 جاهز")
