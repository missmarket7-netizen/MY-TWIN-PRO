"""Voice model – voice configuration and personalities."""
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


def get_voice_personality(personality: str = "friend", gender: str = "female") -> dict:
    config = VOICE_PERSONALITIES.get(personality, VOICE_PERSONALITIES["friend"]).copy()
    base = GENDER_BASE.get(gender, GENDER_BASE["female"])
    config["pitch"] = config["pitch"] * base["pitch"]
    config["rate"] = config["rate"] * base["rate"]
    config["gender"] = gender
    return config
