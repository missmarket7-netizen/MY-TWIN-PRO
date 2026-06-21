"""
MyTwin – Response Formatter v3.0 (سياقي وذكي)
================================================
- تنسيق متكامل للغة العربية (RTL، علامات ترقيم)
- نهايات ذكية سياقية (بدون أسئلة ثابتة)
- دعم الإيموجي والقوائم والجداول
"""
import re, random, logging
from typing import Optional

logger = logging.getLogger("response_formatter")

# ============================================================
# 1. الإيموجي حسب الفئة
# ============================================================
EMOJI_MAP = {
    "weather": "🌤️", "music": "🎵", "news": "📰", "goals": "🎯",
    "support": "💜", "general": "💬", "search": "🔍",
    "coding": "💻", "comparison": "📊", "emotional": "💕",
    "study": "📚", "business": "💼", "dream": "🌙", "food": "🥗",
    "fitness": "🏋️", "smart_home": "🏠", "task": "✅",
}

# ============================================================
# 2. النهايات الذكية (بدون أسئلة ثابتة)
# ============================================================
SMART_ENDINGS = {
    "study": {
        "ar": [
            "هل تحب نتعمق في نقطة معينة؟ 📚",
            "تقدر تسألني أي سؤال عن الموضوع ده.",
            "فهمت الشرح ولا أشرح بطريقة تانية؟",
        ],
        "en": [
            "Want to dive deeper into this topic? 📚",
            "Feel free to ask any questions about this.",
            "Did this explanation make sense?",
        ],
    },
    "business": {
        "ar": [
            "هل تحب نحلل الفكرة أكثر؟ 💼",
            "تقدر تطلب دراسة جدوى كاملة.",
            "عندك أي استفسار عن المشروع؟",
        ],
        "en": [
            "Want me to analyze this idea further? 💼",
            "You can request a full feasibility study.",
        ],
    },
    "emotional": {
        "ar": [
            "أنا معك دايماً 💜",
            "خد وقتك، أنا موجود.",
            "حابب تحكي أكثر؟",
        ],
        "en": [
            "I'm here with you always 💜",
            "Take your time, I'm here.",
        ],
    },
    "general": {
        "ar": [
            "إيه رأيك؟ 💭",
            "فيه حاجة تانية أقدر أساعدك فيها؟",
            "هل في نقطة معينة حابب تركز عليها؟",
        ],
        "en": [
            "What do you think? 💭",
            "Is there anything else I can help with?",
        ],
    },
}

class ResponseFormatter:
    def process(self, reply: str, intent: str = "general", lang: str = "ar") -> str:
        """يعالج الرد بالكامل: تنسيق + نهاية ذكية"""
        if not reply:
            return reply

        # 1. تنظيف المسافات الزائدة
        reply = re.sub(r'\n{3,}', '\n\n', reply)
        reply = re.sub(r' {2,}', ' ', reply)

        # 2. تحسين علامات الترقيم العربية
        if lang == "ar":
            reply = re.sub(r'،([^\s])', r'، \1', reply)
            reply = re.sub(r'؛([^\s])', r'؛ \1', reply)

        # 3. تحويل الخطوات إلى Markdown
        reply = self._format_steps(reply, lang)

        # 4. إضافة إيموجي مناسب (واحد فقط)
        reply = self._add_emoji(reply, intent)

        # 5. نهاية ذكية سياقية (اختيارية)
        reply = self._add_smart_ending(reply, intent, lang)

        return reply.strip()

    def _format_steps(self, text: str, lang: str) -> str:
        """تحويل الخطوات إلى Markdown مرقم"""
        patterns = [
            (r'(الخطوة|خطوة)\s*(\d+)', r'\n**\1 \2:**'),
            (r'(Step)\s*(\d+)', r'\n**\1 \2:**'),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _add_emoji(self, text: str, intent: str) -> str:
        """إضافة إيموجي مناسب إذا لم يكن موجوداً"""
        emoji = EMOJI_MAP.get(intent)
        if not emoji:
            return text

        # لا نضيف إذا كان هناك إيموجي بالفعل في آخر 20 حرفاً
        last_chars = text[-20:] if len(text) > 20 else text
        if any(ord(c) > 127 for c in last_chars[-3:]):  # فحص وجود إيموجي
            return text

        lines = text.split('\n')
        if lines:
            lines[-1] = lines[-1].rstrip() + f" {emoji}"
        return '\n'.join(lines)

    def _add_smart_ending(self, text: str, intent: str, lang: str) -> str:
        """إضافة نهاية سياقية ذكية (بدون أسئلة ثابتة)"""
        # 1. لا نضيف نهاية إذا كان النص ينتهي بسؤال أصلاً
        if text.rstrip().endswith('?'):
            return text
        if text.rstrip().endswith('؟'):
            return text

        # 2. لا نضيف نهاية إذا كان النص قصيراً جداً
        if len(text) < 50:
            return text

        # 3. لا نضيف نهاية إذا كان هناك إيموجي في آخر سطر
        last_line = text.split('\n')[-1].strip() if '\n' in text else text.strip()
        if any(ord(c) > 127 for c in last_line[-3:]):
            return text

        # 4. اختيار نهاية ذكية حسب الفئة
        endings = SMART_ENDINGS.get(intent, SMART_ENDINGS["general"]).get(lang, [])
        if endings:
            chosen = random.choice(endings)
            return text + f"\n\n{chosen}"

        return text


response_engine = ResponseFormatter()
logger.info("✅ Response Formatter v3.0 initialized")
