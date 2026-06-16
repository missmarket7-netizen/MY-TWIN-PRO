"""
MyTwin – Voice Engine v5.1 (TTS مقسم حسب الباقة)
- Free / Plus: Edge TTS أساسي، Expo Speech احتياطي
- Premium / Pro / Yearly: ElevenLabs أساسي، Edge TTS احتياطي
- دعم العامية المصرية: نصوص + نموذج Multilingual v2 + Stability منخفض
"""
import os, logging, asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger("voice_engine")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_IDS = {
    "arabic_female": os.getenv("ELEVENLABS_FEMALE_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    "arabic_male": os.getenv("ELEVENLABS_MALE_VOICE_ID", ""),
    "english_female": os.getenv("ELEVENLABS_ENGLISH_FEMALE_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    "english_male": os.getenv("ELEVENLABS_ENGLISH_MALE_VOICE_ID", ""),
}

# أصوات مصرية للعامية
EDGE_VOICE_MAPPING = {
    "male": {"ar": "ar-EG-ShakirNeural", "en": "en-US-GuyNeural"},
    "female": {"ar": "ar-EG-SalmaNeural", "en": "en-US-JennyNeural"},
}

def get_elevenlabs_voice(gender: str, language: str) -> str:
    return ELEVENLABS_VOICE_IDS.get(f"{language}_{gender}", ELEVENLABS_VOICE_IDS["arabic_female"])

def get_edge_voice(gender: str, language: str) -> str:
    return EDGE_VOICE_MAPPING.get(gender, EDGE_VOICE_MAPPING["female"]).get(language, "ar-EG-SalmaNeural")

async def speakResponse(text: str, tier: str = "free", gender: str = "female",
                        emotion: str = "neutral", language: str = "ar") -> Optional[bytes]:
    if not text or not text.strip():
        return None

    if gender not in ["male", "female"]:
        gender = "female"
    if language not in ["ar", "en"]:
        language = "ar"

    # تحديد المزود حسب الباقة
    is_premium = tier in ["premium", "pro", "yearly"]

    if is_premium:
        # الباقات المدفوعة: ElevenLabs أساسي
        if ELEVENLABS_API_KEY:
            result = await _elevenlabs_tts(text, gender, language, emotion)
            if result:
                return result
        # Edge TTS احتياطي
        result = await _edge_tts(text, gender, language, emotion)
        if result:
            return result
    else:
        # الباقات المجانية: Edge TTS أساسي
        result = await _edge_tts(text, gender, language, emotion)
        if result:
            return result

    # إشارة للواجهة (تستخدم Expo Speech)
    return None

async def _elevenlabs_tts(text: str, gender: str, language: str, emotion: str) -> Optional[bytes]:
    if not ELEVENLABS_API_KEY:
        return None
    try:
        import httpx
        voice_id = get_elevenlabs_voice(gender, language)
        if not voice_id:
            return None

        stability = 0.4 if emotion == "sadness" else 0.5 if emotion == "joy" else 0.45
        similarity = 0.75

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json={
                    "text": text,
                    "voice_settings": {"stability": stability, "similarity_boost": similarity},
                    "model_id": "eleven_multilingual_v2"
                },
                headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
            )
            if resp.status_code == 200:
                return resp.content
    except Exception as e:
        logger.warning(f"ElevenLabs: {e}")
    return None

async def _edge_tts(text: str, gender: str, language: str, emotion: str) -> Optional[bytes]:
    try:
        import edge_tts
        voice = get_edge_voice(gender, language)
        rate = "+5%" if emotion in ["joy", "anger"] else "-5%" if emotion == "sadness" else "+0%"
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks) if chunks else None
    except Exception as e:
        logger.warning(f"Edge TTS: {e}")
    return None

class VoiceEngine:
    def __init__(self):
        logger.info("✅ Voice Engine v5.1 (مقسم حسب الباقة + مصري)")

    async def speak(self, text, tier="free", emotion="neutral", gender="female", language="ar"):
        return await speakResponse(text, tier, gender, emotion, language)

voice_engine = VoiceEngine()
