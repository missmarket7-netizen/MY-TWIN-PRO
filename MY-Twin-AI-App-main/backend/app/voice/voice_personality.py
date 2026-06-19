"""
MyTwin – Voice Personality v2.0
- إدارة شخصيات الصوت (Mentor, Friend, Romantic, Energetic, Calm).
- دعم الأصوات حسب الجنس (ذكر/أنثى).
- تعديل pitch, rate, pause, emotion بناءً على الشخصية والجنس.
- متوافق مع `voice_engine.py`.
"""
from typing import Dict, Any, Optional

# شخصيات الصوت
VOICE_PERSONALITIES = {
    "mentor": {
        "label_ar": "مرشد",
        "label_en": "Mentor",
        "pitch": 0.95,
        "rate": 0.85,
        "pause": 0.8,
        "emotion": "calm"
    },
    "friend": {
        "label_ar": "صديق",
        "label_en": "Friend",
        "pitch": 1.0,
        "rate": 1.0,
        "pause": 0.5,
        "emotion": "neutral"
    },
    "romantic": {
        "label_ar": "رومانسي",
        "label_en": "Romantic",
        "pitch": 1.05,
        "rate": 0.9,
        "pause": 0.7,
        "emotion": "loving"
    },
    "energetic": {
        "label_ar": "حيوي",
        "label_en": "Energetic",
        "pitch": 1.1,
        "rate": 1.15,
        "pause": 0.2,
        "emotion": "excited"
    },
    "calm": {
        "label_ar": "هادئ",
        "label_en": "Calm",
        "pitch": 0.85,
        "rate": 0.75,
        "pause": 0.9,
        "emotion": "calm"
    },
}

# دعم الأصوات حسب الجنس
GENDER_VOICE_MAPPING = {
    "male": {
        "voice_id": "male_voice_elevenlabs_id",  # يجب تحديثه بمعرف الصوت الفعلي
        "voice_name": "ذكر",
        "label_ar": "ذكر",
        "label_en": "Male",
        "base_pitch": 0.85,   # صوت أخفض للذكور
        "base_rate": 0.95,
        "pitch_range": (0.7, 1.0),
        "rate_range": (0.8, 1.1)
    },
    "female": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # المعرف الافتراضي للأنثى
        "voice_name": "أنثى",
        "label_ar": "أنثى",
        "label_en": "Female",
        "base_pitch": 1.1,    # صوت أعلى للإناث
        "base_rate": 1.0,
        "pitch_range": (0.9, 1.3),
        "rate_range": (0.9, 1.2)
    }
}

def get_voice_personality(personality: str, gender: Optional[str] = None) -> Dict[str, Any]:
    """
    إرجاع إعدادات الصوت للشخصية المحددة مع مراعاة الجنس.
    
    Args:
        personality: نوع الشخصية (mentor, friend, romantic, energetic, calm)
        gender: الجنس (male, female) - اختياري
        
    Returns:
        Dict يحتوي على إعدادات الصوت
    """
    # الحصول على إعدادات الشخصية الأساسية
    config = VOICE_PERSONALITIES.get(personality, VOICE_PERSONALITIES["friend"]).copy()
    
    # تعديل حسب الجنس إذا تم توفيره
    if gender and gender in GENDER_VOICE_MAPPING:
        gender_config = GENDER_VOICE_MAPPING[gender]
        config["pitch"] = config["pitch"] * gender_config["base_pitch"]
        config["rate"] = config["rate"] * gender_config["base_rate"]
        config["voice_id"] = gender_config["voice_id"]
        config["voice_name"] = gender_config["voice_name"]
        config["gender"] = gender
        config["pitch_range"] = gender_config["pitch_range"]
        config["rate_range"] = gender_config["rate_range"]
    else:
        # إعدادات افتراضية إذا لم يتم تحديد الجنس
        config["voice_id"] = GENDER_VOICE_MAPPING["female"]["voice_id"]
        config["voice_name"] = GENDER_VOICE_MAPPING["female"]["voice_name"]
        config["gender"] = "female"
        
    return config

def get_voice_config(relationship_stage: str, emotion: str, gender: Optional[str] = None) -> Dict[str, Any]:
    """
    اختيار الشخصية المناسبة بناءً على مرحلة العلاقة والمشاعر مع دعم الجنس.
    
    Args:
        relationship_stage: مرحلة العلاقة
        emotion: المشاعر الحالية
        gender: الجنس (اختياري)
    """
    # تحديد الشخصية بناءً على المشاعر ومرحلة العلاقة
    if emotion in ["sadness", "fear", "anger"]:
        personality = "calm"
    elif relationship_stage in ["close_friend", "trusted_companion", "soul_twin"]:
        personality = "friend"
    elif emotion in ["joy", "surprise"]:
        personality = "energetic"
    else:
        personality = "mentor"
    
    # إرجاع الإعدادات مع الجنس
    return get_voice_personality(personality, gender)

def get_available_genders() -> list:
    """إرجاع قائمة بالأجناس المتاحة."""
    return [
        {"id": "male", "label_ar": "ذكر", "label_en": "Male"},
        {"id": "female", "label_ar": "أنثى", "label_en": "Female"}
    ]

def get_available_personalities() -> list:
    """إرجاع قائمة بالشخصيات المتاحة."""
    return [
        {
            "id": pid,
            "label_ar": config["label_ar"],
            "label_en": config["label_en"],
            "emotion": config["emotion"]
        }
        for pid, config in VOICE_PERSONALITIES.items()
    ]

if __name__ == "__main__":
    # اختبار سريع
    print("✅ اختبار نظام Voice Personality v2.0:")
    print("\n1. شخصية mentor مع ذكر:")
    print(get_voice_personality("mentor", "male"))
    
    print("\n2. شخصية romantic مع أنثى:")
    print(get_voice_personality("romantic", "female"))
    
    print("\n3. شخصية friend بدون تحديد جنس:")
    print(get_voice_personality("friend"))
    
    print("\n4. الأجناس المتاحة:")
    print(get_available_genders())
    
    print("\n5. الشخصيات المتاحة:")
    print(get_available_personalities())
    
    print("\n✨ تم تحميل النظام بنجاح!")
