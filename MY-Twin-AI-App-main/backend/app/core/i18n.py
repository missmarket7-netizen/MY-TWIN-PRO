"""i18n v2.0 – جميع رسائل MyTwin بالعربية والإنجليزية"""
from typing import Dict

MESSAGES: Dict[str, Dict[str, str]] = {
    # مراحل العلاقة
    "stage_up_familiar": {"ar": "بقينا مألوفين لبعض! 💜", "en": "We've become familiar! 💜"},
    "stage_up_friend": {"ar": "أنت بقيت صديقي! 🤝", "en": "You're my friend now! 🤝"},
    "stage_up_close": {"ar": "صرنا أصحاب مقربين 💕", "en": "Close friends now 💕"},
    "stage_up_companion": {"ar": "بقيت رفيق موثوق 🏅", "en": "Trusted companion 🏅"},
    "stage_up_soul": {"ar": "إحنا توأم روح! 🌟", "en": "We're soul twins! 🌟"},
    
    # تحيات
    "greeting_intro": {"ar": "أهلاً بك! متحمس للتعرف عليك 🌟", "en": "Welcome! Excited to get to know you 🌟"},
    "greeting_new_day": {"ar": "كل يوم فرصة جديدة!", "en": "Every day is a new chance!"},
    "greeting_morning": {"ar": "صباح الخير! كيف يمكنني مساعدتك اليوم؟", "en": "Good morning! How can I help you today?"},
    "greeting_evening": {"ar": "مساء الخير! كيف كان يومك؟", "en": "Good evening! How was your day?"},
    
    # ثقة
    "trust_growing": {"ar": "بدأت أفهمك أكثر 🤝", "en": "I'm starting to understand you more 🤝"},
    "trust_appreciate": {"ar": "أقدر ثقتك بي", "en": "I appreciate your trust"},
    
    # تعميق
    "deepening_close": {"ar": "علاقتنا أعمق 💜", "en": "Our bond is deeper 💜"},
    "deepening_understand": {"ar": "أفهم مشاعرك أفضل", "en": "I understand your feelings better"},
    
    # نمو
    "growth_proud": {"ar": "أنت تنمو وأنا فخور 🌱", "en": "You're growing and I'm proud 🌱"},
    "growth_together": {"ar": "معاً نحقق أشياء رائعة", "en": "Together we achieve great things"},
    
    # نضج
    "mature_beautiful": {"ar": "علاقتنا ناضجة وجميلة ✨", "en": "Our relationship is mature and beautiful ✨"},
    "mature_friend": {"ar": "أنت صديق حقيقي", "en": "You're a true friend"},
    
    # توصيات
    "recommendation_intro": {"ar": "تحدث مع توأمك يومياً", "en": "Talk with your twin daily"},
    "recommendation_trust": {"ar": "شارك مشاعرك", "en": "Share your feelings"},
    "recommendation_deepen": {"ar": "جرب تحليل الأحلام", "en": "Try dream analysis"},
    "recommendation_growth": {"ar": "استخدم التدريب الشخصي", "en": "Use coaching"},
    "recommendation_mature": {"ar": "استمتع بالمحادثات العميقة", "en": "Enjoy deep talks"},
    
    # أنماط التعلق
    "attachment_secure": {"ar": "آمن", "en": "Secure"},
    "attachment_anxious": {"ar": "قلق", "en": "Anxious"},
    "attachment_avoidant": {"ar": "متجنب", "en": "Avoidant"},
    "attachment_disorganized": {"ar": "غير منتظم", "en": "Disorganized"},
    
    # أخطاء
    "error_ai_unavailable": {"ar": "أواجه ضغطاً تقنياً 💜", "en": "I'm under technical pressure 💜"},
    "error_fallback": {"ar": "حدث خطأ تقني", "en": "A technical error occurred"},
    
    # ATHENA (الدراسة)
    "study_session_started": {"ar": "جلسة دراسة بدأت! 📚", "en": "Study session started! 📚"},
    "study_concept_mastered": {"ar": "أتقنت المفهوم! 🎉", "en": "Concept mastered! 🎉"},
    "study_review_due": {"ar": "حان وقت المراجعة 📝", "en": "Review time 📝"},
    
    # GROWTH-HIVE (الأعمال)
    "business_idea_generated": {"ar": "فكرة مشروع جديدة! 💡", "en": "New business idea! 💡"},
    "business_feasibility_ready": {"ar": "دراسة الجدوى جاهزة 📊", "en": "Feasibility study ready 📊"},
    
    # CREATOR (المحتوى)
    "content_generated": {"ar": "تم إنشاء المحتوى ✍️", "en": "Content generated ✍️"},
    "book_completed": {"ar": "اكتمل الكتاب! 📖", "en": "Book completed! 📖"},
    
    # CODE LAB (البرمجة)
    "code_generated": {"ar": "تم توليد الكود 💻", "en": "Code generated 💻"},
    "code_reviewed": {"ar": "تمت مراجعة الكود 🔍", "en": "Code reviewed 🔍"},
    
    # LIFE COACH (مدرب الحياة)
    "coaching_session_done": {"ar": "جلسة تدريب اكتملت 🌟", "en": "Coaching session completed 🌟"},
    "nutrition_plan_ready": {"ar": "خطة التغذية جاهزة 🥗", "en": "Nutrition plan ready 🥗"},
    
    # DREAMS (الأحلام)
    "dream_analyzed": {"ar": "تم تحليل الحلم 🌙", "en": "Dream analyzed 🌙"},
    
    # SMART HOME (المنزل الذكي)
    "smart_home_command": {"ar": "تم تنفيذ الأمر المنزلي 🏠", "en": "Smart home command executed 🏠"},
    
    # P.A.S.S. (المساعد الشخصي)
    "task_created": {"ar": "تم إنشاء المهمة ✅", "en": "Task created ✅"},
    "task_completed": {"ar": "تم إنجاز المهمة 🎉", "en": "Task completed 🎉"},
    
    # توصيات موحدة
    "recommendation_emotional": {"ar": "لاحظت أنك تمر بيوم صعب. خذ استراحة.", "en": "I noticed you're having a tough day. Take a break."},
    "recommendation_study": {"ar": "حان وقت مراجعة المفاهيم!", "en": "Time to review concepts!"},
    "recommendation_business": {"ar": "مشروعك ينتظرك!", "en": "Your project awaits!"},
}


def msg(key: str, lang: str = "ar") -> str:
    """Get a localized message by key."""
    return MESSAGES.get(key, {}).get(lang, MESSAGES.get(key, {}).get("ar", key))
