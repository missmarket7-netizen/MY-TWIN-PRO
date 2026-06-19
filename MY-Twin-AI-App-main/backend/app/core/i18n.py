"""i18n – centralized Arabic/English messages for the entire backend."""
from typing import Dict

MESSAGES: Dict[str, Dict[str, str]] = {
    "memory_summarized": {"ar": "تم تلخيص الذاكرة", "en": "Memory summarized"},
    "stage_up_familiar": {"ar": "بقينا مألوفين لبعض! 💜", "en": "We've become familiar! 💜"},
    "stage_up_friend": {"ar": "أنت بقيت صديقي! 🤝", "en": "You're my friend now! 🤝"},
    "stage_up_close": {"ar": "صرنا أصحاب مقربين 💕", "en": "Close friends now 💕"},
    "stage_up_companion": {"ar": "بقيت رفيق موثوق 🏅", "en": "Trusted companion 🏅"},
    "stage_up_soul": {"ar": "إحنا توأم روح! 🌟", "en": "We're soul twins! 🌟"},
    "greeting_intro": {"ar": "أهلاً بك! متحمس للتعرف عليك 🌟", "en": "Welcome! Excited to get to know you 🌟"},
    "greeting_new_day": {"ar": "كل يوم فرصة جديدة!", "en": "Every day is a new chance!"},
    "trust_growing": {"ar": "بدأت أفهمك أكثر 🤝", "en": "I'm starting to understand you more 🤝"},
    "trust_appreciate": {"ar": "أقدر ثقتك بي", "en": "I appreciate your trust"},
    "deepening_close": {"ar": "علاقتنا أعمق 💜", "en": "Our bond is deeper 💜"},
    "deepening_understand": {"ar": "أفهم مشاعرك أفضل", "en": "I understand your feelings better"},
    "growth_proud": {"ar": "أنت تنمو وأنا فخور 🌱", "en": "You're growing and I'm proud 🌱"},
    "growth_together": {"ar": "معاً نحقق أشياء رائعة", "en": "Together we achieve great things"},
    "mature_beautiful": {"ar": "علاقتنا ناضجة وجميلة ✨", "en": "Our relationship is mature and beautiful ✨"},
    "mature_friend": {"ar": "أنت صديق حقيقي", "en": "You're a true friend"},
    "recommendation_intro": {"ar": "تحدث مع توأمك يومياً", "en": "Talk with your twin daily"},
    "recommendation_trust": {"ar": "شارك مشاعرك", "en": "Share your feelings"},
    "recommendation_deepen": {"ar": "جرب تحليل الأحلام", "en": "Try dream analysis"},
    "recommendation_growth": {"ar": "استخدم التدريب الشخصي", "en": "Use coaching"},
    "recommendation_mature": {"ar": "استمتع بالمحادثات العميقة", "en": "Enjoy deep talks"},
    "attachment_secure": {"ar": "آمن", "en": "Secure"},
    "attachment_anxious": {"ar": "قلق", "en": "Anxious"},
    "attachment_avoidant": {"ar": "متجنب", "en": "Avoidant"},
    "attachment_disorganized": {"ar": "غير منتظم", "en": "Disorganized"},
    "attachment_unknown": {"ar": "غير معروف", "en": "Unknown"},
    "consciousness_reflection": {"ar": "تأمل", "en": "Reflection"},
    "consciousness_last_thought": {"ar": "آخر فكرة", "en": "Last thought"},
    "consciousness_active_goals": {"ar": "أهداف نشطة", "en": "Active goals"},
    "error_ai_unavailable": {"ar": "أواجه ضغطاً تقنياً 💜", "en": "I'm under technical pressure 💜"},
    "error_fallback": {"ar": "حدث خطأ تقني", "en": "A technical error occurred"},
}


def msg(key: str, lang: str = "ar") -> str:
    """Get a localized message by key."""
    return MESSAGES.get(key, {}).get(lang, MESSAGES.get(key, {}).get("ar", key))
