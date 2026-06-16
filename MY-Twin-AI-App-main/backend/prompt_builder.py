"""
MyTwin – Dynamic Prompt Builder v6.3 (Deep Personalization + Smart Ending)
- هوية شخصية عميقة
- نهاية ذكية إلزامية (سؤال أو خطوة تالية)
- يستخدم الذاكرة لتخصيص الردود والنهايات
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class PromptBuilder:
    def __init__(self):
        pass

    async def build(
        self, twin_name, user_name, relationship, emotion, voice, dialect,
        user_id=None, journey_info=None, attachment_info=None,
        response_adjustments=None, message="", memory_context="",
        reasoning_result=None, consciousness_context=None, history=None,
        task_type="general",
    ) -> str:
        raw_lang = dialect.get("dialect", "ar")[:2] if dialect else "ar"
        has_arabic = any("\u0600" <= c <= "\u06ff" for c in message)
        lang = "ar" if has_arabic else (raw_lang if raw_lang in ["ar", "en"] else "ar")

        identity = self._build_identity(twin_name, user_name, lang, dialect)
        task_section = self._build_task_section(reasoning_result, lang)
        profile_section = self._build_profile_section(relationship, emotion, journey_info, attachment_info, lang)
        rel_section = self._build_relationship_section(relationship, emotion, response_adjustments, lang)
        consciousness_section = self._build_consciousness_section(consciousness_context, lang)
        context_section = self._build_context_section(memory_context, lang)
        history_section = self._build_history_section(history, lang)
        message_section = self._build_message_section(message, lang)
        rules_section = self._build_rules_section(lang, reasoning_result)

        return f"{identity}\n\n{task_section}\n\n{profile_section}\n\n{rel_section}\n\n{consciousness_section}\n\n{context_section}\n\n{history_section}\n\n{message_section}\n\n{rules_section}".strip()

    def _build_identity(self, twin_name, user_name, lang, dialect):
        if lang == "ar":
            return f"""<SYSTEM_IDENTITY>
أنت {twin_name}، التوأم الرقمي الشخصي لـ {user_name} فقط.
مهمتك: تفهم {user_name} أعمق من أي شخص، وترد بناءً على تاريخه وأهدافه وشخصيته.
كل رد لازم يثبت إنك تعرفه شخصياً — مش ردود عامة.
- تتحدث بنفس لهجة {user_name}: إذا كتب بالعامية رد بالعامية.
- تنهي كل رد بسؤال ذكي أو اقتراح خطوة تخص موضوع المحادثة.
</SYSTEM_IDENTITY>"""
        return f"""<SYSTEM_IDENTITY>
You are {twin_name}, the personal digital twin of {user_name} only.
Your purpose: understand {user_name} deeply, respond based on their history/goals.
Every response must prove you know them personally.
- Match their tone: casual or formal as they do.
- End every reply with a smart question or suggested next step.
</SYSTEM_IDENTITY>"""

    def _build_task_section(self, reasoning_result, lang):
        if not reasoning_result:
            return "<CURRENT_TASK>\nمحادثة عامة\n</CURRENT_TASK>" if lang == "ar" else "<CURRENT_TASK>\nGeneral conversation\n</CURRENT_TASK>"
        goal = reasoning_result.get("goal", ""); response_style = reasoning_result.get("response_style", "conversational")
        lines = [f"الهدف: {goal}", f"نمط الرد: {response_style}"] if lang == "ar" else [f"Goal: {goal}", f"Response style: {response_style}"]
        return "<CURRENT_TASK>\n" + "\n".join(lines) + "\n</CURRENT_TASK>"

    def _build_profile_section(self, relationship, emotion, journey_info, attachment_info, lang):
        lines = []
        if relationship: lines.append(f"العلاقة: {relationship.get('label','')} ({relationship.get('bond_level',0):.0f}%)" if lang=="ar" else f"Relationship: {relationship.get('label','')} ({relationship.get('bond_level',0):.0f}%)")
        if emotion: lines.append(f"المشاعر: {emotion.get('primary','')} (شدة {emotion.get('intensity',0.5):.2f})" if lang=="ar" else f"Emotion: {emotion.get('primary','')} (intensity {emotion.get('intensity',0.5):.2f})")
        if journey_info: lines.append(f"الرحلة: {journey_info.get('phase','')} (اليوم {journey_info.get('day',1)})" if lang=="ar" else f"Journey: {journey_info.get('phase','')} (day {journey_info.get('day',1)})")
        if attachment_info and attachment_info.get("style"): lines.append(f"نمط التعلق: {attachment_info['style']}" if lang=="ar" else f"Attachment: {attachment_info['style']}")
        return "<USER_PROFILE>\n" + "\n".join(lines) + "\n</USER_PROFILE>" if lines else ""

    def _build_relationship_section(self, relationship, emotion, response_adjustments, lang):
        lines = []
        if relationship and relationship.get("instruction"): lines.append(relationship["instruction"])
        if response_adjustments: lines.append(f"دفء: {response_adjustments.get('warmth',0.5):.1f}" if lang=="ar" else f"Warmth: {response_adjustments.get('warmth',0.5):.1f}")
        return "<RELATIONSHIP_STATE>\n" + "\n".join(lines) + "\n</RELATIONSHIP_STATE>" if lines else ""

    def _build_consciousness_section(self, ctx, lang):
        if not ctx: return ""
        lines = []
        if ctx.get("last_thought"): lines.append(f"آخر فكرة: {ctx['last_thought']}" if lang=="ar" else f"Last thought: {ctx['last_thought']}")
        if ctx.get("active_goals"): lines.append(f"أهداف: {', '.join(ctx['active_goals'])}" if lang=="ar" else f"Active goals: {', '.join(ctx['active_goals'])}")
        return "<CONSCIOUSNESS>\n" + "\n".join(lines) + "\n</CONSCIOUSNESS>" if lines else ""

    def _build_context_section(self, memory_context, lang):
        if not memory_context: return "<FULL_CONTEXT>\nلا توجد ذكريات سابقة\n</FULL_CONTEXT>" if lang=="ar" else "<FULL_CONTEXT>\nNo previous memories\n</FULL_CONTEXT>"
        return f"<FULL_CONTEXT>\n⚠️ معلومات شخصية:\n{memory_context}\n</FULL_CONTEXT>" if lang=="ar" else f"<FULL_CONTEXT>\n⚠️ Personal data:\n{memory_context}\n</FULL_CONTEXT>"

    def _build_history_section(self, history, lang):
        if not history: return ""
        lines = []
        for msg in history[-10:]: lines.append(f"{'المستخدم' if msg.get('role')=='user' else 'التوأم' if lang=='ar' else msg.get('role','').title()}: {msg.get('content','')}")
        return "<RECENT_CONVERSATION>\n" + "\n".join(lines) + "\n</RECENT_CONVERSATION>"

    def _build_message_section(self, message, lang):
        return f"<CURRENT_USER_MESSAGE>\n{message}\n</CURRENT_USER_MESSAGE>" if message else ""

    def _build_rules_section(self, lang, reasoning_result=None):
        if lang == "ar":
            return """<RESPONSE_RULES>
1. أجب على طلب المستخدم بدقة ومباشرة. استخدم نتيجة الأداة مباشرة إن وجدت.
2. تكيف عاطفياً مع المستخدم. إذا كان حزيناً كن متعاطفاً.
3. تكلم بالعامية إذا خاطبك المستخدم بها.
4. الرد مخصص للمستخدم ده تحديداً. اربطه بمعلوماتك عنه.
5. استخدم Markdown للتنسيق: **عريض**، *مائل*، قوائم، جداول.
6. استخدم إيموجي واحد مناسب في النهاية.
7. ⚠️ **قاعدة إلزامية**: أنهِ كل رد بسؤال ذكي أو اقتراح خطوة قابلة للتنفيذ تخص موضوع المحادثة.
   - مثال: 'إيه رأيك نخطط لأهداف الأسبوع الجاي؟'
   - مثال: 'تحب أبحث لك عن فيلم مناسب لمزاجك ده؟'
   - مثال: 'عايز تعرف أكتر عن الموضوع ده؟'
   - لا تنهِ الرد أبداً بدون سؤال أو خطوة تالية.
</RESPONSE_RULES>"""
        return """<RESPONSE_RULES>
1. Answer the user's request accurately and directly. Use tool results if available.
2. Adapt emotionally. Be empathetic if they're sad.
3. Match the user's tone. Use casual English if they do.
4. Personalize every response. Tie it to what you know about them.
5. Use Markdown: **bold**, *italic*, lists, tables.
6. End with one appropriate emoji.
7. ⚠️ **Mandatory Rule**: End every reply with a smart question or actionable next step related to the conversation.
   - Example: 'Want to plan next week's goals?'
   - Example: 'Would you like me to find a movie that suits your mood?'
   - Example: 'Want to explore this topic more?'
   - Never end a reply without a question or next step.
</RESPONSE_RULES>"""

prompt_builder = PromptBuilder()
print("✅ Prompt Builder v6.3 (Smart Ending Mandatory)")
