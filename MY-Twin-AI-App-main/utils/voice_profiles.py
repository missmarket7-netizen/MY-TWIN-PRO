"""
MyTwin – Voice Personality v3.0 (Production Ready)
====================================================
- إدارة شخصيات الصوت (Mentor, Friend, Romantic, Energetic, Calm, GenZ).
- دعم الأصوات حسب الجنس (ذكر/أنثى) واللغة (عربي/إنجليزي).
- تكامل مع إعدادات الصوت (VoiceConfig) ونظام الباقة.
- تعديل pitch, rate, pause, emotion بناءً على الشخصية والجنس.
"""
from typing import Dict, Any, Optional, List

# ============================================================
# شخصيات الصوت (تمت إضافة نمط GenZ العصري)
# ============================================================
VOICE_PERSONALITIES: Dict[str, Dict[str, Any]] = {
    "mentor": {
        "label_ar": "مرشد",
        "label_en": "Mentor",
        "pitch": 0.95,
        "rate": 0.85,
        "pause": 0.8,
        "emotion": "calm",
        "style": "حكيم، واضح، ملهم"
    },
    "friend": {
        "label_ar": "صديق",
        "label_en": "Friend",
        "pitch": 1.0,
        "rate": 1.0,
        "pause": 0.5,
        "emotion": "neutral",
        "style": "دافئ، قريب، مرح"
    },
    "romantic": {
        "label_ar": "رومانسي",
        "label_en": "Romantic",
        "pitch": 1.05,
        "rate": 0.9,
        "pause": 0.7,
        "emotion": "loving",
        "style": "ناعم، عاطفي، حالم"
    },
    "energetic": {
        "label_ar": "حيوي",
        "label_en": "Energetic",
        "pitch": 1.1,
        "rate": 1.15,
        "pause": 0.2,
        "emotion": "excited",
        "style": "سريع، مشجع، مفعم بالطاقة"
    },
    "calm": {
        "label_ar": "هادئ",
        "label_en": "Calm",
        "pitch": 0.85,
        "rate": 0.75,
        "pause": 0.9,
        "emotion": "calm",
        "style": "بطيء، مريح، مطمئن"
    },
    "genz": {
        "label_ar": "عصري (Gen Z)",
        "label_en": "Gen Z",
        "pitch": 1.05,
        "rate": 1.1,
        "pause": 0.4,
        "emotion": "excited",
        "style": "سريع، مرح، مليء بالإيموجي"
    }
}

# ============================================================
# دعم الأصوات حسب الجنس واللغة (Edge TTS افتراضياً)
# ============================================================
GENDER_VOICE_MAPPING: Dict[str, Dict[str, Any]] = {
    "male": {
        "voice_name": "ذكر",
        "label_ar": "ذكر",
        "label_en": "Male",
        "base_pitch": 0.85,   # صوت أخفض للذكور
        "base_rate": 0.95,
        "pitch_range": (0.7, 1.0),
        "rate_range": (0.8, 1.1),
        "default_voice_id": {
            "ar": "ar-SA-HamedNeural",
            "en": "en-US-GuyNeural"
        }
    },
    "female": {
        "voice_name": "أنثى",
        "label_ar": "أنثى",
        "label_en": "Female",
        "base_pitch": 1.1,    # صوت أعلى للإناث
        "base_rate": 1.0,
        "pitch_range": (0.9, 1.3),
        "rate_range": (0.9, 1.2),
        "default_voice_id": {
            "ar": "ar-EG-SalmaNeural",
            "en": "en-US-JennyNeural"
        }
    }
}

# ============================================================
# وظائف الحصول على الإعدادات
# ============================================================

def get_voice_personality(personality: str, gender: Optional[str] = None, lang: str = "ar") -> Dict[str, Any]:
    """
    إرجاع إعدادات الصوت للشخصية المحددة مع مراعاة الجنس واللغة.
    """
    # 1. إعدادات الشخصية الأساسية
    config = VOICE_PERSONALITIES.get(personality, VOICE_PERSONALITIES["friend"]).copy()
    
    # 2. تعديل حسب الجنس
    if gender and gender in GENDER_VOICE_MAPPING:
        gender_config = GENDER_VOICE_MAPPING[gender]
        config["pitch"] = config["pitch"] * gender_config["base_pitch"]
        config["rate"] = config["rate"] * gender_config["base_rate"]
        config["voice_id"] = gender_config["default_voice_id"].get(lang, gender_config["default_voice_id"]["ar"])
        config["voice_name"] = gender_config["voice_name"]
        config["gender"] = gender
        config["pitch_range"] = gender_config["pitch_range"]
        config["rate_range"] = gender_config["rate_range"]
    else:
        # افتراضي أنثى عربية
        config["voice_id"] = GENDER_VOICE_MAPPING["female"]["default_voice_id"]["ar"]
        config["voice_name"] = "أنثى"
        config["gender"] = "female"
        
    return config


def get_voice_config(relationship_stage: str = "friend", emotion: str = "neutral", gender: Optional[str] = None, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    اختيار الشخصية المناسبة بناءً على مرحلة العلاقة، المشاعر، وتفضيلات المستخدم.
    """
    # 1. إذا كان المستخدم قد خصص الإعدادات، نستخدمها
    if user_preferences and user_preferences.get("voice_personality"):
        return get_voice_personality(user_preferences["voice_personality"], gender, user_preferences.get("lang", "ar"))
        
    # 2. تحديد الشخصية بناءً على المشاعر
    if emotion in ["sadness", "fear", "anger"]:
        personality = "calm"
    elif emotion in ["joy", "surprise", "excited"]:
        personality = "energetic"
    # 3. أو بناءً على مرحلة العلاقة
    elif relationship_stage in ["close_friend", "trusted_companion", "soul_twin"]:
        personality = "friend" # الأصدقاء المقربون يتحدثون بود
    else:
        personality = "mentor" # افتراضي للمرشد

    return get_voice_personality(personality, gender)


def get_available_genders() -> List[Dict[str, str]]:
    """إرجاع قائمة بالأجناس المتاحة."""
    return [
        {"id": gid, "label_ar": gconfig["label_ar"], "label_en": gconfig["label_en"]}
        for gid, gconfig in GENDER_VOICE_MAPPING.items()
    ]

def get_available_personalities() -> List[Dict[str, str]]:
    """إرجاع قائمة بالشخصيات المتاحة."""
    return [
        {"id": pid, "label_ar": config["label_ar"], "label_en": config["label_en"], "emotion": config["emotion"]}
        for pid, config in VOICE_PERSONALITIES.items()
    ]

# ============================================================
# اختبار سريع
# ============================================================
if __name__ == "__main__":
    print("✅ Voice Personality v3.0")
    print("\n1. شخصية mentor مع ذكر:")
    print(get_voice_personality("mentor", "male"))
    print("\n2. شخصية genz مع أنثى:")
    print(get_voice_personality("genz", "female"))
    print("\n3. الأجناس المتاحة:")
    print(get_available_genders())
