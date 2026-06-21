"""
Voice Service v3.0 – محرك صوتي متعدد المزودين (إنتاجي)
===========================================================
- Edge TTS (مجاني، افتراضي)
- ElevenLabs (مميز، Premium/Pro)
- تكامل مع إعدادات المستخدم (UserProfile)
- تخزين مؤقت للصوت (Cache) لتجنب إعادة التوليد
"""
import os, logging, hashlib
from typing import Optional

logger = logging.getLogger("voice_service")

# ========== الإعدادات ==========
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY", "")
VOICE_IDS = {
    "arabic_female": os.getenv("ELEVENLABS_FEMALE_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    "arabic_male": os.getenv("ELEVENLABS_MALE_VOICE_ID", ""),
    "english_female": os.getenv("ELEVENLABS_EN_FEMALE_ID", "21m00Tcm4TlvDq8ikWAM"),
    "english_male": os.getenv("ELEVENLABS_EN_MALE_ID", ""),
}
EDGE_VOICES = {
    "male": {"ar": "ar-EG-ShakirNeural", "en": "en-US-GuyNeural"},
    "female": {"ar": "ar-EG-SalmaNeural", "en": "en-US-JennyNeural"},
}

# ========== توليد الصوت ==========
async def speak(
    text: str,
    tier: str = "free",
    gender: str = "female",
    emotion: str = "neutral",
    lang: str = "ar",
    user_id: Optional[str] = None,
    personality: str = "friend",
) -> Optional[bytes]:
    """
    توليد صوت من النص.
    يتحقق من التخزين المؤقت أولاً.
    """
    if not text or not text.strip():
        return None

    # 1. فحص التخزين المؤقت
    cache_key = f"voice:{hashlib.md5(text.encode()).hexdigest()}:{lang}:{gender}:{emotion}"
    try:
        from app.infrastructure.cache.cache_service import get as cache_get
        cached = cache_get(cache_key)
        if cached:
            return cached
    except: pass

    # 2. محاولة ElevenLabs (للمميزين)
    is_premium = tier in ["premium", "pro", "yearly"]
    if is_premium and ELEVENLABS_KEY:
        audio = await _elevenlabs(text, gender, lang, emotion)
        if audio:
            _cache_audio(cache_key, audio)
            return audio

    # 3. Edge TTS (مجاني، الجميع)
    audio = await _edge_tts(text, gender, lang, emotion, personality)
    if audio:
        _cache_audio(cache_key, audio)
    return audio


def _cache_audio(key: str, audio: bytes):
    """تخزين الصوت مؤقتاً"""
    try:
        from app.infrastructure.cache.cache_service import set as cache_set
        cache_set(key, audio, ttl=3600)
    except: pass


# ========== مزود ElevenLabs ==========
async def _elevenlabs(text: str, gender: str, lang: str, emotion: str) -> Optional[bytes]:
    if not ELEVENLABS_KEY:
        return None
    try:
        import httpx
        voice = VOICE_IDS.get(f"{lang}_{gender}", VOICE_IDS["arabic_female"])
        stability = 0.4 if emotion == "sadness" else 0.5 if emotion == "joy" else 0.45
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                json={
                    "text": text,
                    "voice_settings": {"stability": stability, "similarity_boost": 0.75},
                    "model_id": "eleven_multilingual_v2",
                },
                headers={"xi-api-key": ELEVENLABS_KEY},
            )
            return resp.content if resp.status_code == 200 else None
    except Exception as e:
        logger.warning(f"ElevenLabs: {e}")
        return None


# ========== مزود Edge TTS ==========
async def _edge_tts(text: str, gender: str, lang: str, emotion: str, personality: str = "friend") -> Optional[bytes]:
    try:
        import edge_tts
        voice = EDGE_VOICES.get(gender, EDGE_VOICES["female"]).get(lang, "ar-EG-SalmaNeural")

        # تعديل السرعة حسب العاطفة
        rate = "+5%" if emotion in ["joy", "anger"] else "-5%" if emotion == "sadness" else "+0%"
        # تعديل حسب الشخصية
        if personality == "energetic":
            rate = "+10%"
        elif personality == "calm":
            rate = "-10%"

        communicate = edge_tts.Communicate(text, voice, rate=rate)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks) if chunks else None
    except Exception as e:
        logger.warning(f"Edge TTS: {e}")
        return None


# ========== شخصيات الصوت ==========
def get_voice_personality(personality: str = "friend", gender: str = "female") -> dict:
    configs = {
        "mentor": {"pitch": 0.95, "rate": 0.85},
        "friend": {"pitch": 1.0, "rate": 1.0},
        "romantic": {"pitch": 1.05, "rate": 0.9},
        "energetic": {"pitch": 1.1, "rate": 1.15},
        "calm": {"pitch": 0.85, "rate": 0.75},
        "genz": {"pitch": 1.05, "rate": 1.1},
    }
    return configs.get(personality, configs["friend"])


logger.info("✅ Voice Service v3.0 initialized")
