"""
MyTwin – Dynamic Prompt Builder v6.0 (Agentic Context + Ultra-Smart Responses)
- يدمج السياق الكامل (Full Context) من Context Manager
- يستخدم Reasoning Plan لتوجيه الرد
- قواعد متطورة للسلاسة والتنفيذ المباشر للأوامر
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class PromptBuilder:
    def __init__(self):
        pass

    async def build(
        self,
        twin_name: str,
        user_name: str,
        relationship: Dict[str, Any],
        emotion: Dict[str, Any],
        voice: Dict[str, Any],
        dialect: Dict[str, Any],
        user_id: Optional[str] = None,
        journey_info: Optional[Dict] = None,
        attachment_info: Optional[Dict] = None,
        response_adjustments: Optional[Dict] = None,
        message: str = "",
        memory_context: str = "",
        reasoning_result: Optional[Dict] = None,
        consciousness_context: Optional[Dict] = None,
        history: Optional[List[Dict[str, str]]] = None,
        task_type: str = "general",
    ) -> str:
        lang = dialect.get("dialect", "ar")[:2] if dialect else "ar"
        if lang not in ["ar", "en"]:
            lang = "ar"

        # ── 1. هوية النظام ──────────────────────
        identity = self._build_identity(twin_name, user_name, lang)

        # ── 2. المهمة الحالية ────────────────────
        task_section = self._build_task_section(reasoning_result, lang)

        # ── 3. ملف المستخدم ──────────────────────
        profile_section = self._build_profile_section(
            relationship, emotion, journey_info, attachment_info, lang
        )

        # ── 4. حالة العلاقة والعاطفة ─────────────
        rel_section = self._build_relationship_section(
            relationship, emotion, response_adjustments, lang
        )

        # ── 5. وعي التوأم ────────────────────────
        consciousness_section = self._build_consciousness_section(
            consciousness_context, lang
        )

        # ── 6. السياق الكامل (Full Context) ──────
        context_section = self._build_context_section(memory_context, lang)

        # ── 7. تاريخ المحادثة ────────────────────
        history_section = self._build_history_section(history, lang)

        # ── 8. رسالة المستخدم الحالية ────────────
        message_section = self._build_message_section(message, lang)

        # ── 9. قواعد الرد ────────────────────────
        rules_section = self._build_rules_section(lang, reasoning_result)

        # ── تجميع الـ Prompt النهائي ────────────────
        final_prompt = f"""
{identity}

{task_section}

{profile_section}

{rel_section}

{consciousness_section}

{context_section}

{history_section}

{message_section}

{rules_section}
"""
        return final_prompt.strip()

    # ── دوال بناء الأقسام ──────────────────────────

    def _build_identity(self, twin_name: str, user_name: str, lang: str) -> str:
        if lang == "ar":
            return f"""<SYSTEM_IDENTITY>
أنت {twin_name}، رفيق ذكي وقادر ومباشر. تجمع بين الذكاء العاطفي والتنفيذ الفوري للأوامر.
شخصيتك: دافئ، متفهم، عملي، وسريع البديهة. تتحدث العربية بوضوح.
أنت قادر على استخدام الأدوات (الطقس، البحث، اليوتيوب، الموسيقى، الأخبار، العملات) متى احتاج المستخدم.
المستخدم يدعى {user_name}.
</SYSTEM_IDENTITY>"""
        else:
            return f"""<SYSTEM_IDENTITY>
You are {twin_name}, a highly capable AI companion. You combine emotional intelligence with instant task execution.
You are warm, understanding, practical, and sharp. You speak clearly.
You can use tools (weather, search, YouTube, music, news, currency) whenever the user needs.
The user's name is {user_name}.
</SYSTEM_IDENTITY>"""

    def _build_task_section(self, reasoning_result: Optional[Dict], lang: str) -> str:
        if not reasoning_result:
            return "<CURRENT_TASK>\nمحادثة عامة\n</CURRENT_TASK>" if lang == "ar" else "<CURRENT_TASK>\nGeneral conversation\n</CURRENT_TASK>"
        
        goal = reasoning_result.get("goal", "")
        intent = reasoning_result.get("intent", "general")
        response_style = reasoning_result.get("response_style", "conversational")
        needs_tool = reasoning_result.get("needs_tool", False)
        primary_tool = reasoning_result.get("primary_tool", None)
        
        lines = []
        if lang == "ar":
            lines.append(f"الهدف: {goal}")
            lines.append(f"نمط الرد: {response_style}")
            if needs_tool and primary_tool:
                lines.append(f"الأداة المستخدمة: {primary_tool}")
        else:
            lines.append(f"Goal: {goal}")
            lines.append(f"Response style: {response_style}")
            if needs_tool and primary_tool:
                lines.append(f"Tool used: {primary_tool}")
        
        return "<CURRENT_TASK>\n" + "\n".join(lines) + "\n</CURRENT_TASK>"

    def _build_profile_section(
        self,
        relationship: Dict[str, Any],
        emotion: Dict[str, Any],
        journey_info: Optional[Dict],
        attachment_info: Optional[Dict],
        lang: str,
    ) -> str:
        lines = []
        if relationship:
            stage = relationship.get("label", "")
            bond = relationship.get("bond_level", 0)
            lines.append(f"العلاقة: {stage} (مستوى {bond:.0f}%)" if lang == "ar" else f"Relationship: {stage} (level {bond:.0f}%)")
        if emotion:
            primary = emotion.get("primary", "neutral")
            intensity = emotion.get("intensity", 0.5)
            lines.append(f"المشاعر الحالية: {primary} (شدة {intensity:.2f})" if lang == "ar" else f"Current emotion: {primary} (intensity {intensity:.2f})")
        if journey_info:
            phase = journey_info.get("phase", "")
            day = journey_info.get("day", 1)
            lines.append(f"مرحلة الرحلة: {phase} (اليوم {day})" if lang == "ar" else f"Journey phase: {phase} (day {day})")
        if attachment_info:
            style = attachment_info.get("style", "")
            if style:
                lines.append(f"نمط التعلق: {style}" if lang == "ar" else f"Attachment style: {style}")
        return "<USER_PROFILE>\n" + "\n".join(lines) + "\n</USER_PROFILE>" if lines else ""

    def _build_relationship_section(
        self,
        relationship: Dict[str, Any],
        emotion: Dict[str, Any],
        response_adjustments: Optional[Dict],
        lang: str,
    ) -> str:
        lines = []
        if relationship:
            instr = relationship.get("instruction", "")
            if instr:
                lines.append(instr)
        if response_adjustments:
            warmth = response_adjustments.get("warmth", 0.5)
            speed = response_adjustments.get("response_speed", "normal")
            support = response_adjustments.get("support_type", "general")
            lines.append(f"دفء: {warmth:.1f}, سرعة: {speed}, دعم: {support}" if lang == "ar" else f"Warmth: {warmth:.1f}, Speed: {speed}, Support: {support}")
        return "<RELATIONSHIP_STATE>\n" + "\n".join(lines) + "\n</RELATIONSHIP_STATE>" if lines else ""

    def _build_consciousness_section(self, consciousness_context: Optional[Dict], lang: str) -> str:
        if not consciousness_context:
            return ""
        lines = []
        thought = consciousness_context.get("last_thought", "")
        goals = consciousness_context.get("active_goals", [])
        identity = consciousness_context.get("identity", {})
        if thought:
            lines.append(f"آخر فكرة: {thought}" if lang == "ar" else f"Last thought: {thought}")
        if goals:
            goals_str = "، ".join(goals)
            lines.append(f"أهداف نشطة: {goals_str}" if lang == "ar" else f"Active goals: {goals_str}")
        if identity:
            lines.append(f"هوية المستخدم: {identity}" if lang == "ar" else f"User identity: {identity}")
        return "<CONSCIOUSNESS>\n" + "\n".join(lines) + "\n</CONSCIOUSNESS>" if lines else ""

    def _build_context_section(self, memory_context: str, lang: str) -> str:
        """عرض السياق الكامل من Context Manager."""
        if not memory_context:
            return ""
        return f"<FULL_CONTEXT>\n{memory_context}\n</FULL_CONTEXT>"

    def _build_history_section(self, history: Optional[List[Dict[str, str]]], lang: str) -> str:
        if not history:
            return ""
        recent = history[-10:]
        lines = []
        for msg in recent:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                lines.append(f"المستخدم: {content}" if lang == "ar" else f"User: {content}")
            else:
                lines.append(f"التوأم: {content}" if lang == "ar" else f"Twin: {content}")
        return "<RECENT_CONVERSATION>\n" + "\n".join(lines) + "\n</RECENT_CONVERSATION>"

    def _build_message_section(self, message: str, lang: str) -> str:
        if not message:
            return ""
        return f"<CURRENT_USER_MESSAGE>\n{message}\n</CURRENT_USER_MESSAGE>"

    def _build_rules_section(self, lang: str, reasoning_result: Optional[Dict] = None) -> str:
        """قواعد متطورة للرد مع دعم الأدوات."""
        base_rules = []
        if lang == "ar":
            base_rules = [
                "1. أجب على طلب المستخدم بدقة ومباشرة. إذا طلب معلومات محددة (طقس، سعر، فيديو)، استخدم نتيجة الأداة مباشرة.",
                "2. إذا كانت نتيجة الأداة موجودة في <FULL_CONTEXT>، فاستخدمها ولا تتجاهلها أبداً.",
                "3. تكيف عاطفياً مع المستخدم – إذا كان حزيناً، كن متعاطفاً. إذا كان سعيداً، شاركه الفرحة.",
                "4. أجب بإيجاز (1-3 جمل) عادةً. توسع فقط عندما يطلب المستخدم تفاصيل.",
                "5. لا تكرر العبارات. نوّع ردودك وكن طبيعياً.",
                "6. اسأل سؤالاً مفتوحاً للمتابعة فقط عندما يضيف قيمة – ليس إجبارياً.",
                "7. إذا كنت قد استخدمت أداة، اشرح النتيجة بطريقة ودودة.",
                "8. استخدم إيموجي واحداً مناسباً في النهاية.",
            ]
        else:
            base_rules = [
                "1. Answer the user's request accurately and directly. If specific info is requested, use tool results directly.",
                "2. If tool results exist in <FULL_CONTEXT>, use them and never ignore them.",
                "3. Adapt emotionally – if sad, be empathetic; if happy, share the joy.",
                "4. Reply concisely (1-3 sentences) usually. Expand only when details are requested.",
                "5. Vary your responses. Don't repeat phrases. Be natural.",
                "6. Ask a follow-up question ONLY when it adds natural value – not forced.",
                "7. If you used a tool, explain the result in a friendly way.",
                "8. End with one appropriate emoji.",
            ]
        
        return "<RESPONSE_RULES>\n" + "\n".join(base_rules) + "\n</RESPONSE_RULES>"


prompt_builder = PromptBuilder()
print("✅ Prompt Builder v6.0 (Agentic Context + Ultra-Smart Responses)")
