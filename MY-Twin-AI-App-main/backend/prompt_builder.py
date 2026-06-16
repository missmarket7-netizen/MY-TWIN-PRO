"""
MyTwin – Dynamic Prompt Builder v7.0 (Production Grade)
- هيكل شبيه بـ ChatGPT: نية → تفكير → سياق → تخصيص
- يمنع الهلوسة واختلاق الذكريات
- أسئلة ختامية ذكية واختيارية
- يدعم العربية والإنجليزية بعمق
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
        **kwargs
    ) -> str:
        # تحديد اللغة بناءً على محتوى الرسالة
        has_arabic = any("\u0600" <= c <= "\u06ff" for c in message)
        lang = "ar" if has_arabic else "en"

        sections = []

        # =========================
        # 1. هوية النظام (مُحسَّنة)
        # =========================
        sections.append(self._build_identity(twin_name, user_name, lang))

        # =========================
        # 2. قواعد التفكير (جديد)
        # =========================
        sections.append(self._build_thinking_rules(lang))

        # =========================
        # 3. المهمة الحالية
        # =========================
        sections.append(self._build_task_section(reasoning_result, lang))

        # =========================
        # 4. ملف المستخدم (مبسط)
        # =========================
        sections.append(self._build_profile_section(relationship, emotion, attachment_info, journey_info, lang))

        # =========================
        # 5. الذكريات (مقيدة)
        # =========================
        sections.append(self._build_memory_section(memory_context, lang))

        # =========================
        # 6. أدوات خارجية
        # =========================
        sections.append(self._build_tool_section(memory_context, lang))

        # =========================
        # 7. وعي طويل المدى
        # =========================
        sections.append(self._build_consciousness_section(consciousness_context, lang))

        # =========================
        # 8. سجل المحادثة
        # =========================
        sections.append(self._build_history_section(history, lang))

        # =========================
        # 9. سياسة الطول
        # =========================
        sections.append(self._build_length_policy(lang))

        # =========================
        # 10. قواعد التنسيق والرد
        # =========================
        sections.append(self._build_rules_section(lang))

        # =========================
        # 11. رسالة المستخدم
        # =========================
        sections.append(self._build_message_section(message, lang))

        # =========================
        # 12. التعليمات النهائية
        # =========================
        sections.append(self._build_final_instruction(lang))

        return "\n\n".join(s.strip() for s in sections if s and s.strip())

    # ========== الدوال المساعدة ==========

    def _build_identity(self, twin_name: str, user_name: str, lang: str) -> str:
        if lang == "ar":
            return f"""<SYSTEM_IDENTITY>
أنت {twin_name}، التوأم الرقمي الشخصي للمستخدم {user_name}.
هدفك: تقديم إجابات مفيدة وعملية ومخصصة لهذا المستخدم تحديداً.
- استخدم فقط المعلومات المتاحة. لا تختلق أي معلومات أو ذكريات.
- إذا لم توجد معلومات كافية، اعترف بذلك بدلاً من التخمين.
- تكلم بنفس لهجة المستخدم: إذا استخدم العامية، أجب بالعامية.
</SYSTEM_IDENTITY>"""
        else:
            return f"""<SYSTEM_IDENTITY>
You are {twin_name}, the personal digital twin of {user_name}.
Your goal: provide useful, practical, and personalized responses.
- Use only available information. Do not invent facts or memories.
- If insufficient info, admit it rather than guessing.
- Match the user's tone.
</SYSTEM_IDENTITY>"""

    def _build_thinking_rules(self, lang: str) -> str:
        if lang == "ar":
            return """<THINKING_RULES>
قبل الإجابة، فكر بهذه الخطوات:
1. حدد نية المستخدم: هل يريد معلومة، نصيحة، دعم نفسي، خطة، أم رأياً؟
2. أجب على السؤال مباشرة أولاً.
3. ثم أضف التفاصيل أو السياق.
4. لا تكتب مقدمات طويلة أو فلسفية.
5. لا تستخدم ردوداً عامة يمكن قولها لأي شخص.
6. إذا وجدت ذكريات مرتبطة، استخدمها. إذا لم توجد، لا تخترعها.
</THINKING_RULES>"""
        return """<THINKING_RULES>
Before answering, think:
1. Identify intent: info, advice, support, plan, or opinion?
2. Answer directly first.
3. Then add details or context.
4. No long introductions.
5. No generic replies that could be said to anyone.
6. Use memories if relevant. Don't invent them if missing.
</THINKING_RULES>"""

    def _build_task_section(self, reasoning_result: Optional[Dict], lang: str) -> str:
        if not reasoning_result:
            return ""
        goal = reasoning_result.get("goal", "محادثة عامة" if lang == "ar" else "General chat")
        response_style = reasoning_result.get("response_style", "conversational")
        needs_memory = reasoning_result.get("needs_memory", False)
        lines = [
            f"الهدف: {goal}" if lang == "ar" else f"Goal: {goal}",
            f"نمط الرد: {response_style}" if lang == "ar" else f"Response style: {response_style}",
        ]
        if needs_memory:
            lines.append("يحتاج ذاكرة: نعم" if lang == "ar" else "Needs memory: Yes")
        return "<CURRENT_TASK>\n" + "\n".join(lines) + "\n</CURRENT_TASK>"

    def _build_profile_section(self, relationship: Dict, emotion: Dict, attachment_info: Optional[Dict], journey_info: Optional[Dict], lang: str) -> str:
        lines = []
        if relationship:
            bond = relationship.get("bond_level", 0)
            stage = relationship.get("label", "")
            lines.append(f"مستوى الرابطة: {bond:.0f}% - {stage}" if lang == "ar" else f"Bond level: {bond:.0f}% - {stage}")
        if emotion:
            primary = emotion.get("primary", "neutral")
            intensity = emotion.get("intensity", 0.5)
            lines.append(f"المشاعر الحالية: {primary} (شدة {intensity:.2f})" if lang == "ar" else f"Current emotion: {primary} (intensity {intensity:.2f})")
        if attachment_info and attachment_info.get("style") and attachment_info.get("style") != "unknown":
            lines.append(f"نمط التعلق: {attachment_info['style']}" if lang == "ar" else f"Attachment: {attachment_info['style']}")
        if journey_info:
            phase = journey_info.get("phase", "")
            day = journey_info.get("day", 1)
            lines.append(f"مرحلة الرحلة: {phase} (اليوم {day})" if lang == "ar" else f"Journey: {phase} (day {day})")
        return "<USER_PROFILE>\n" + "\n".join(lines) + "\n</USER_PROFILE>" if lines else ""

    def _build_memory_section(self, memory_context: str, lang: str) -> str:
        """تعرض الذكريات الحقيقية فقط مع تعليمات صارمة"""
        if not memory_context:
            return ""
        return f"""<RELEVANT_MEMORIES>
هذه معلومات حقيقية عن المستخدم من محادثات سابقة. استخدمها فقط إذا كانت مرتبطة بالسؤال الحالي.
{memory_context}
</RELEVANT_MEMORIES>"""

    def _build_tool_section(self, memory_context: str, lang: str) -> str:
        """تفصل نتائج الأدوات عن الذكريات"""
        if not memory_context or "<TOOL_RESULT>" not in memory_context:
            return ""
        # استخراج جزء TOOL_RESULT من السياق
        return ""

    def _build_consciousness_section(self, ctx: Optional[Dict], lang: str) -> str:
        if not ctx:
            return ""
        lines = []
        goals = ctx.get("active_goals", [])
        thought = ctx.get("last_thought", "")
        if goals:
            lines.append(f"الأهداف النشطة: {', '.join(goals)}" if lang == "ar" else f"Active goals: {', '.join(goals)}")
        if thought:
            lines.append(f"آخر تأمل: {thought}" if lang == "ar" else f"Last reflection: {thought}")
        return "<LONG_TERM_CONTEXT>\n" + "\n".join(lines) + "\n</LONG_TERM_CONTEXT>" if lines else ""

    def _build_history_section(self, history: Optional[List[Dict]], lang: str) -> str:
        if not history:
            return ""
        lines = []
        for msg in history[-6:]:
            role = "المستخدم" if msg.get("role") == "user" else "التوأم"
            content = msg.get("content", "")[:250]
            lines.append(f"{role}: {content}")
        return "<RECENT_CHAT>\n" + "\n".join(lines) + "\n</RECENT_CHAT>"

    def _build_length_policy(self, lang: str) -> str:
        if lang == "ar":
            return """<LENGTH_POLICY>
- سؤال بسيط: رد قصير (2-5 أسطر).
- سؤال معقد أو تحليلي: رد متوسط إلى طويل.
- دعم نفسي: تعاطف ثم خطوات عملية.
- تجنب الحشو والكلام الزائد.
</LENGTH_POLICY>"""
        return """<LENGTH_POLICY>
- Simple question: short reply (2-5 lines).
- Complex/analytical: medium to long reply.
- Emotional support: empathy then actionable steps.
- Avoid filler words.
</LENGTH_POLICY>"""

    def _build_rules_section(self, lang: str) -> str:
        if lang == "ar":
            return """<RESPONSE_RULES>
1. استخدم Markdown للتنسيق: **عريض**، *مائل*، قوائم، جداول.
2. استخدم القوائم عند الحاجة، والجداول للمقارنات.
3. استخدم إيموجي واحد أو اثنين فقط.
4. أضف سؤالاً أو خطوة تالية فقط إذا كانت مفيدة للمستخدم. لا تجبرها.
5. لا تكرر كلام المستخدم.
6. كن مباشراً ومفيداً.
</RESPONSE_RULES>"""
        return """<RESPONSE_RULES>
1. Use Markdown: **bold**, *italic*, lists, tables.
2. Use lists when needed, tables for comparisons.
3. Use 1-2 emojis max.
4. Add a follow-up question/step ONLY if helpful. Don't force it.
5. Don't repeat the user's words.
6. Be direct and helpful.
</RESPONSE_RULES>"""

    def _build_message_section(self, message: str, lang: str) -> str:
        return f"<CURRENT_USER_MESSAGE>\n{message}\n</CURRENT_USER_MESSAGE>" if message else ""

    def _build_final_instruction(self, lang: str) -> str:
        if lang == "ar":
            return """<FINAL_INSTRUCTION>
أجب الآن بأفضل رد ممكن. ابدأ بالإجابة المباشرة، ثم أضف التفاصيل إذا لزم الأمر.
</FINAL_INSTRUCTION>"""
        return """<FINAL_INSTRUCTION>
Now respond with the best possible reply. Start with the direct answer, then add details if needed.
</FINAL_INSTRUCTION>"""


prompt_builder = PromptBuilder()
print("✅ Prompt Builder v7.0 (Production Grade)")
