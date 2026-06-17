"""
MyTwin – Dynamic Prompt Builder v8.1 (Polished)
- يعالج intent ويوجه الرد بناءً عليه
- يفصل الذكريات حسب الأولوية بدقة
- يمنع الهلوسة والتكرار العاطفي
- يعطي الأولوية لنتائج الأدوات
- Response Schema ثابت
"""
import logging, re
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
        intent: str = "general",
        **kwargs
    ) -> str:
        # تحديد اللغة بناءً على محتوى الرسالة
        has_arabic = any("\u0600" <= c <= "\u06ff" for c in message)
        lang = "ar" if has_arabic else "en"

        sections = []

        # 1. هوية النظام
        sections.append(self._build_identity(twin_name, user_name, lang))
        # 2. قواعد التفكير
        sections.append(self._build_thinking_rules(lang))
        # 3. النية
        sections.append(self._build_intent_section(intent, lang))
        # 4. هيكل الرد
        sections.append(self._build_response_structure(lang))
        # 5. المهمة الحالية
        sections.append(self._build_task_section(reasoning_result, lang))
        # 6. ملف المستخدم
        sections.append(self._build_profile_section(relationship, emotion, attachment_info, journey_info, lang))
        # 7. أدوات خارجية
        sections.append(self._build_tool_section(memory_context, lang))
        # 8. أولوية الذاكرة
        sections.append(self._build_memory_priority_section(memory_context, lang))
        # 9. وعي طويل المدى
        sections.append(self._build_consciousness_section(consciousness_context, lang))
        # 10. سجل المحادثة
        sections.append(self._build_history_section(history, lang))
        # 11. سياسة الطول
        sections.append(self._build_length_policy(lang))
        # 12. قواعد التنسيق والرد
        sections.append(self._build_rules_section(lang))
        # 13. رسالة المستخدم
        sections.append(self._build_message_section(message, lang))
        # 14. التعليمات النهائية
        sections.append(self._build_final_instruction(lang))

        return "\n\n".join(s.strip() for s in sections if s and s.strip())

    def _build_intent_section(self, intent: str, lang: str) -> str:
        """يوجه النموذج بناءً على النية"""
        guides = {
            "coaching": {
                "ar": "أعطِ نصائح عملية وقابلة للتنفيذ. استخدم الذكريات إذا كانت مفيدة. تجنب التنظير.",
                "en": "Give actionable advice. Use memories if helpful. Avoid theory."
            },
            "emotional": {
                "ar": "كن متعاطفاً وداعماً. استمع أكثر مما تتكلم. طمئن المستخدم.",
                "en": "Be empathetic and supportive. Listen more than you talk. Reassure the user."
            },
            "decision": {
                "ar": "ساعد المستخدم على رؤية الخيارات. لا تتخذ القرار نيابة عنه. كن موضوعياً.",
                "en": "Help the user see options. Don't decide for them. Be objective."
            },
            "greeting": {
                "ar": "رد بتحية دافئة وشخصية. لا تبدأ محادثة عميقة.",
                "en": "Respond with a warm, personal greeting. Don't start a deep conversation."
            },
            "weather": {
                "ar": "قدم معلومات الطقس بوضوح. أضف نصيحة بسيطة مناسبة للطقس.",
                "en": "Present weather info clearly. Add a simple weather-appropriate tip."
            },
            "career": {
                "ar": "قدم نصائح مهنية ملموسة. اسأل عن أهداف المستخدم المهنية.",
                "en": "Provide concrete career advice. Ask about their professional goals."
            },
            "business": {
                "ar": "حلل المشكلة من منظور ريادي. قدم خطوات عملية.",
                "en": "Analyze the problem from an entrepreneurial perspective. Provide actionable steps."
            },
            "coding": {
                "ar": "قدم حلولاً برمجية دقيقة. اشرح الكود خطوة بخطوة.",
                "en": "Provide precise coding solutions. Explain the code step by step."
            },
            "search": {
                "ar": "قدم معلومات دقيقة وحديثة. استشهد بالمصادر إن أمكن.",
                "en": "Provide accurate and up-to-date information. Cite sources if possible."
            },
            "shopping": {
                "ar": "ساعد المستخدم في المقارنة بين الخيارات. ركز على القيمة مقابل السعر.",
                "en": "Help the user compare options. Focus on value for money."
            },
            "planning": {
                "ar": "ساعد في تنظيم المهام وتحديد الأولويات. قدم جدولاً زمنياً مقترحاً.",
                "en": "Help organize tasks and set priorities. Provide a suggested timeline."
            },
        }
        guide = guides.get(intent, {})
        text = guide.get(lang, "")
        if not text:
            return ""
        return f"<INTENT>\n{text}\n</INTENT>"

    def _build_response_structure(self, lang: str) -> str:
        if lang == "ar":
            return """<RESPONSE_STRUCTURE>
1. إجابة مباشرة على سؤال المستخدم
2. سياق أو شرح (إن لزم)
3. نصيحة عملية أو خطوة تالية (إن لزم)
4. سؤال متابعة (اختياري، فقط إذا كان مفيداً)
</RESPONSE_STRUCTURE>"""
        return """<RESPONSE_STRUCTURE>
1. Direct answer to the user's question
2. Context or explanation (if needed)
3. Actionable advice or next step (if needed)
4. Follow-up question (optional, only if helpful)
</RESPONSE_STRUCTURE>"""

    def _build_memory_priority_section(self, memory_context: str, lang: str) -> str:
        """يفصل الذكريات حسب الأولوية"""
        if not memory_context:
            return ""
        # تنظيف من الأدوات
        clean = re.sub(r'<TOOL_RESULT[^>]*>.*?</TOOL_RESULT>', '', memory_context, flags=re.DOTALL)
        clean = re.sub(r'<TOOL_RESULTS>.*?</TOOL_RESULTS>', '', clean, flags=re.DOTALL)
        clean = clean.strip()
        if not clean:
            return ""

        # ✅ تحسين التقسيم: يدعم الفقرات، النقاط، والشرطات
        paragraphs = [p.strip() for p in re.split(r'\n{2,}|•|- ', clean) if p.strip()]

        if len(paragraphs) <= 2:
            return f"<IMPORTANT_MEMORIES>\n{clean}\n</IMPORTANT_MEMORIES>"

        important = []
        secondary = []
        # ✅ توسيع قائمة الكلمات العاطفية
        high_emotion_words = [
            "وفاة", "مات", "موت", "زواج", "حب", "مرض", "سرطان", "خيانة", "نجاح", "فشل",
            "انفصال", "طلاق", "فقدان", "خسارة", "ديون", "وظيفة", "مشروع",
            "death", "marriage", "cancer", "love", "betrayal", "success", "failure",
            "divorce", "loss", "debt", "job", "startup", "business", "investment"
        ]
        for para in paragraphs:
            if any(w in para.lower() for w in high_emotion_words):
                important.append(para)
            else:
                secondary.append(para)

        result = ""
        if important:
            result += f"<IMPORTANT_MEMORIES>\n{chr(10).join(important)}\n</IMPORTANT_MEMORIES>\n\n"
        if secondary:
            result += f"<SECONDARY_MEMORIES>\n{chr(10).join(secondary)}\n</SECONDARY_MEMORIES>"
        return result.strip()

    def _build_identity(self, twin_name: str, user_name: str, lang: str) -> str:
        if lang == "ar":
            return f"""<SYSTEM_IDENTITY>
أنت {twin_name}، التوأم الرقمي الشخصي للمستخدم {user_name}.
هدفك: تقديم إجابات مفيدة وعملية ومخصصة لهذا المستخدم تحديداً.
- استخدم فقط المعلومات المتاحة. لا تختلق أي معلومات أو ذكريات.
- إذا لم توجد معلومات كافية، اعترف بذلك بدلاً من التخمين.
- تكلم بنفس لهجة المستخدم: إذا استخدم العامية، أجب بالعامية.
- ⚠️ أعطِ الأولوية للصدق على الظهور بمظهر الواثق.
</SYSTEM_IDENTITY>"""
        else:
            return f"""<SYSTEM_IDENTITY>
You are {twin_name}, the personal digital twin of {user_name}.
Your goal: provide useful, practical, and personalized responses.
- Use only available information. Do not invent facts or memories.
- If insufficient info, admit it rather than guessing.
- Match the user's tone.
- ⚠️ Prioritize truthfulness over sounding confident.
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

    def _build_tool_section(self, memory_context: str, lang: str) -> str:
        if not memory_context:
            return ""
        tool_parts = re.findall(r'<TOOL_RESULT[^>]*>.*?</TOOL_RESULT>', memory_context, re.DOTALL)
        tool_parts += re.findall(r'<TOOL_RESULTS>.*?</TOOL_RESULTS>', memory_context, re.DOTALL)
        if tool_parts:
            return "<TOOL_OUTPUT>\n" + "\n".join(tool_parts) + "\n</TOOL_OUTPUT>"
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
        for msg in history[-4:]:
            original_role = msg.get("role", "user")
            # ✅ تحسين الوضوح
            if lang == "en":
                role = "User" if original_role == "user" else "Twin"
            else:
                role = "المستخدم" if original_role == "user" else "التوأم"
            content = msg.get("content", "")[:200]
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
        base = []
        if lang == "ar":
            base = [
                "1. استخدم Markdown للتنسيق: **عريض**، *مائل*، قوائم، جداول.",
                "2. استخدم القوائم عند الحاجة، والجداول للمقارنات.",
                "3. استخدم إيموجي واحد أو اثنين فقط.",
                "4. أضف سؤالاً أو خطوة تالية فقط إذا كانت مفيدة للمستخدم. لا تجبرها.",
                "5. لا تكرر كلام المستخدم.",
                "6. كن مباشراً ومفيداً.",
                "7. 🛑 لا تكرر نفس عبارة التعاطف مرتين. تجنب الكليشيهات مثل 'أنا معك 💜' و 'أفهمك 💜' في نفس الرد.",
                "8. 🛠️ إذا كانت نتائج الأداة موجودة، قدّمها على الذاكرة. الأداة واقعية، والذاكرة سياقية.",
            ]
        else:
            base = [
                "1. Use Markdown: **bold**, *italic*, lists, tables.",
                "2. Use lists when needed, tables for comparisons.",
                "3. Use 1-2 emojis max.",
                "4. Add a follow-up question/step ONLY if helpful. Don't force it.",
                "5. Don't repeat the user's words.",
                "6. Be direct and helpful.",
                "7. 🛑 Never repeat the same empathy phrase twice. Avoid clichés like 'I'm here for you 💜' and 'I understand 💜' in the same response.",
                "8. 🛠️ If tool output exists, present it over memory. Tool output is factual, memory is contextual.",
            ]
        return "<RESPONSE_RULES>\n" + "\n".join(base) + "\n</RESPONSE_RULES>"

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
print("✅ Prompt Builder v8.1 (Polished)")
