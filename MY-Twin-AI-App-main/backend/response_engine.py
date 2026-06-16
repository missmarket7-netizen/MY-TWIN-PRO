"""
MyTwin – Unified Response Engine v1.0
- Formatter + Styler مدمجين
- دعم عربي عميق (RTL، علامات ترقيم)
- تحويل ذكي للجداول والقوائم
"""
import re
import logging

logger = logging.getLogger("response_engine")

EMOJI_MAP = {
    "weather": "🌤️", "music": "🎵", "news": "📰", "goals": "🎯",
    "support": "💜", "general": "💬", "search": "🔍",
    "coding": "💻", "comparison": "📊", "emotional": "💕",
}

class ResponseEngine:
    def process(self, reply: str, intent: str = "general", lang: str = "ar") -> str:
        """يعالج الرد بالكامل: تنسيق + تجميل"""
        if not reply:
            return reply

        # 1. تنظيف المسافات الزائدة
        reply = re.sub(r'\n{3,}', '\n\n', reply)
        reply = re.sub(r' {2,}', ' ', reply)

        # 2. تحسين الفقرات العربية
        if lang == "ar":
            # مسافة بعد الفاصلة العربية
            reply = re.sub(r'،([^\s])', r'، \1', reply)
            # مسافة بعد الفاصلة المنقوطة
            reply = re.sub(r'؛([^\s])', r'؛ \1', reply)

        # 3. تحويل الجداول النصية إلى Markdown (إذا وجدت)
        reply = self._text_to_table(reply)

        # 4. تحويل الخطوات المرقمة إلى Markdown
        reply = self._number_steps(reply)

        # 5. إضافة إيموجي مناسب (حد أقصى 1)
        reply = self._add_emoji(reply, intent)

        # 6. التأكد من وجود نهاية ذكية
        reply = self._ensure_smart_ending(reply, lang)

        return reply.strip()

    def _text_to_table(self, text: str) -> str:
        """تحويل نص يقارن بين شيئين إلى جدول Markdown"""
        if "مقارنة" in text or "قارن" in text or "compare" in text.lower():
            # المنطق هنا: إذا وجد كلمات مفتاحية، نضيف تلميحاً للجدول
            # لكن النموذج هو من يقرر التنسيق النهائي
            pass
        return text

    def _number_steps(self, text: str) -> str:
        """تحويل الخطوات إلى Markdown مرقم"""
        # إذا كان النص يحتوي على "الخطوة" أو "step"
        if re.search(r'(الخطوة|خطوة|step)\s*\d', text, re.IGNORECASE):
            text = re.sub(r'(الخطوة|خطوة|Step)\s*(\d)', r'\n**\1 \2:**', text)
        return text

    def _add_emoji(self, text: str, intent: str) -> str:
        """إضافة إيموجي واحد إذا لم يكن موجوداً"""
        emoji = EMOJI_MAP.get(intent)
        if emoji and emoji not in text[-10:]:
            # إضافة قبل آخر سطر
            lines = text.split('\n')
            if lines:
                lines[-1] = lines[-1].rstrip() + f" {emoji}"
            return '\n'.join(lines)
        return text

    def _ensure_smart_ending(self, text: str, lang: str) -> str:
        """التأكد من وجود سؤال أو خطوة تالية"""
        endings_ar = ["؟", "🎯", "💭", "🌟", "💜", "📝", "🎵", "🌤️"]
        endings_en = ["?", "🎯", "💭", "🌟", "💜", "📝", "🎵", "🌤️"]
        endings = endings_ar if lang == "ar" else endings_en

        # إذا كان آخر حرف ليس استفهاماً أو إيموجي، نضيف سؤالاً عاماً
        if not any(text.rstrip().endswith(e) for e in endings):
            if lang == "ar":
                text += "\n\nإيه رأيك في الموضوع ده؟ 💭"
            else:
                text += "\n\nWhat do you think about this? 💭"
        return text


response_engine = ResponseEngine()
print("✅ Unified Response Engine v1.0")
