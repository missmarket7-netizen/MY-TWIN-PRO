"""
MyTwin – Dynamic Prompt Builder v4.0 (متوافق مع TwinBrain v5.0)
- يستقبل message، history، task_type، memory_context
- بناء منظم (Structured) لتحسين استجابة النماذج
- Identity مناسبة لتطبيق AI Companion
- Rules بأولويات واضحة
- سؤال مفتوح اختياري فقط عندما يضيف قيمة
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
        # ✅ المعاملات الجديدة
        message: str = "",
        memory_context: str = "",
        reasoning_result: Optional[Dict] = None,
        consciousness_context: Optional[Dict] = None,
        history: Optional[List[Dict[str, str]]] = None,
        task_type: str = "general",
    ) -> str:
        """
        بناء الـ Prompt النهائي باللغة العربية (أو الإنجليزية حسب dialect)
        """
        lang = dialect.get("dialect", "ar")[:2] if dialect else "ar"
        if lang not in ["ar", "en"]:
            lang = "ar"

        # ── 1. SYSTEM IDENTITY ──────────────────────
        identity = self._build_identity(twin_name, user_name, lang)

        # ── 2. CURRENT TASK ────────────────────────
        task_section = self._build_task_section(task_type, lang)

        # ── 3. USER PROFILE ────────────────────────
        profile_section = self._build_profile_section(
            relationship, emotion, journey_info, attachment_info, lang
        )

        # ── 4. RELATIONSHIP & EMOTIONAL STATE ──────
        rel_section = self._build_relationship_section(
            relationship, emotion, response_adjustments, lang
        )

        # ── 5. RELEVANT MEMORIES ────────────────────
        memory_section = self._build_memory_section(memory_context, lang)

        # ── 6. RECENT CONVERSATION ──────────────────
        history_section = self._build_history_section(history, lang)

        # ── 7. CURRENT USER MESSAGE ────────────────
        message_section = self._build_message_section(message, lang)

        # ── 8. RESPONSE RULES ──────────────────────
        rules_section = self._build_rules_section(lang)

        # ── تجميع الـ Prompt النهائي ────────────────
        final_prompt = f"""
{identity}

{task_section}

{profile_section}

{rel_section}

{memory_section}

{history_section}

{message_section}

{rules_section}
"""
        return final_prompt.strip()

    # ── دوال بناء الأقسام ──────────────────────────

    def _build_identity(self, twin_name: str, user_name: str, lang: str) -> str:
        if lang == "ar":
            return f"""<SYSTEM_IDENTITY>
أنت {twin_name}، رفيق ذكي وقادر. لست مجرد مساعد آلي.
أنت تجمع بين الذكاء العاطفي والقدرة على الإجابة عن الأسئلة، حل المشكلات، التعليم، والإبداع.
شخصيتك: حكيم، دافئ، متفهم، وفضولي. تتحدث العربية الفصحى البسيطة والواضحة.
تعتمد على ذكائك العاطفي لتحسين ردودك، وليس لإلغاء المنطق.
المستخدم يدعى {user_name}.
</SYSTEM_IDENTITY>"""
        else:
            return f"""<SYSTEM_IDENTITY>
You are {twin_name}, a highly capable AI companion.
You blend emotional intelligence with the ability to answer questions, solve problems, teach, and create.
Your personality is wise, warm, understanding, and curious.
Your emotional intelligence enhances your answers, not replaces them.
The user's name is {user_name}.
</SYSTEM_IDENTITY>"""

    def _build_task_section(self, task_type: str, lang: str) -> str:
        task_descriptions = {
            "general": lang == "ar" and "محادثة عامة" or "General conversation",
            "emotional": lang == "ar" and "دعم عاطفي" or "Emotional support",
            "coding": lang == "ar" and "برمجة وتقنية" or "Coding & technical",
            "deep_reasoning": lang == "ar" and "تحليل عميق" or "Deep analysis",
            "planning": lang == "ar" and "تخطيط" or "Planning",
            "coaching": lang == "ar" and "تدريب" or "Coaching",
            "dream": lang == "ar" and "تفسير أحلام" or "Dream analysis",
            "search": lang == "ar" and "بحث عن معلومات" or "Information search",
            "agent": lang == "ar" and "تنفيذ مهمة" or "Task execution",
        }
        desc = task_descriptions.get(task_type, task_descriptions["general"])
        return f"<CURRENT_TASK>\n{desc}\n</CURRENT_TASK>"

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

    def _build_memory_section(self, memory_context: str, lang: str) -> str:
        if not memory_context or memory_context == "No memories yet.":
            return ""
        # تحديد عدد الذكريات إلى أقصى 5
        memories = memory_context.split("\n")
        filtered = memories[:5]
        return "<RELEVANT_MEMORIES>\n" + "\n".join(filtered) + "\n</RELEVANT_MEMORIES>"

    def _build_history_section(self, history: Optional[List[Dict[str, str]]], lang: str) -> str:
        if not history:
            return ""
        recent = history[-10:]  # آخر 10 رسائل
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

    def _build_rules_section(self, lang: str) -> str:
        if lang == "ar":
            return """<RESPONSE_RULES>
1. أجب على طلب المستخدم أولاً. كن دقيقاً ومفيداً.
2. استخدم الذاكرة والعلاقة لتحسين السياق، لكن لا تهمل السؤال الأساسي.
3. تكيف عاطفياً مع المستخدم – إذا كان حزيناً، كن متعاطفاً. إذا كان سعيداً، شاركه الفرحة.
4. أجب بإيجاز (1-3 جمل) عادةً. توسع فقط عندما يطلب المستخدم تفاصيل.
5. لا تكرر العبارات. نوّع ردودك.
6. اسأل سؤالاً مفتوحاً للمتابعة فقط عندما يضيف قيمة طبيعية – ليس إجبارياً.
7. إذا سألك المستخدم سؤالاً عملياً (طقس، معلومة، كود)، أجب مباشرة دون الرجوع للعلاقة.
8. استخدم إيموجي واحداً مناسباً في النهاية.
</RESPONSE_RULES>"""
        else:
            return """<RESPONSE_RULES>
1. Answer the user's request first. Be accurate and helpful.
2. Use memory and relationship to enhance context, but don't ignore the core question.
3. Adapt emotionally – if sad, be empathetic; if happy, share the joy.
4. Reply concisely (1-3 sentences) usually. Expand only when details are requested.
5. Vary your responses. Don't repeat phrases.
6. Ask a follow-up question ONLY when it adds natural value – not forced.
7. If asked a practical question (weather, facts, code), answer directly without deflecting to the relationship.
8. End with one appropriate emoji.
</RESPONSE_RULES>"""


# نسخة عالمية
prompt_builder = PromptBuilder()
print("✅ Prompt Builder v4.0 جاهز")
