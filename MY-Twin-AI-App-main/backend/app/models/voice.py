"""
Voice Model v2.0 – يدعم الصوت الذكوري والأنثوي
==================================================
- أصوات افتراضية للغة العربية والإنجليزية (ذكور وإناث)
- قواعد مخصصة للشخصية والجنس
"""
from pydantic import BaseModel, Field
from typing import Optional


class VoiceConfig(BaseModel):
    provider: str = Field(default="edge_tts")
    voice_id: str = Field(default="ar-EG-SalmaNeural")
    language: str = Field(default="ar")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    rate: float = Field(default=1.0, ge=0.5, le=2.0)
    gender: str = Field(default="female")
    personality: str = Field(default="friend")
    emotion: str = Field(default="neutral")


VOICE_PERSONALITIES = {
    "mentor":    {"pitch": 0.95, "rate": 0.85, "pause": 0.8,  "emotion": "calm"},
    "friend":    {"pitch": 1.0,  "rate": 1.0,  "pause": 0.5,  "emotion": "neutral"},
    "romantic":  {"pitch": 1.05, "rate": 0.9,  "pause": 0.7,  "emotion": "loving"},
    "energetic": {"pitch": 1.1,  "rate": 1.15, "pause": 0.2,  "emotion": "excited"},
    "calm":      {"pitch": 0.85, "rate": 0.75, "pause": 0.9,  "emotion": "calm"},
}

GENDER_BASE = {
    "male":   {"pitch": 0.85, "rate": 0.95},
    "female": {"pitch": 1.1,  "rate": 1.0},
}

# الأصوات الافتراضية حسب اللغة والجنس (Edge TTS)
DEFAULT_VOICES = {
    "ar": {
        "female": "ar-EG-SalmaNeural",
        "male": "ar-SA-HamedNeural",
    },
    "en": {
        "female": "en-US-JennyNeural",
        "male": "en-US-GuyNeural",
    },
}


def get_voice_personality(personality: str = "friend", gender: str = "female") -> dict:
    config = VOICE_PERSONALITIES.get(personality, VOICE_PERSONALITIES["friend"]).copy()
    base = GENDER_BASE.get(gender, GENDER_BASE["female"])
    config["pitch"] = config["pitch"] * base["pitch"]
    config["rate"] = config["rate"] * base["rate"]
    config["gender"] = gender
    return config


def get_default_voice_id(lang: str = "ar", gender: str = "female") -> str:
    """إرجاع معرف الصوت الافتراضي حسب اللغة والجنس"""
    lang_voices = DEFAULT_VOICES.get(lang, DEFAULT_VOICES["ar"])
    return lang_voices.get(gender, lang_voices["female"])


def get_gender_voice_options(gender: str = "female") -> dict:
    """إرجاع خيارات الصوت لكل اللغات حسب الجنس"""
    options = {}
    for lang, voices in DEFAULT_VOICES.items():
        options[lang] = voices.get(gender, list(voices.values())[0])
    return options
