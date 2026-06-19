"""Voice Service – TTS per tier with Egyptian Arabic."""
import os, logging
from typing import Optional

logger = logging.getLogger("voice_service")

ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY","")
VOICE_IDS = {"arabic_female":os.getenv("ELEVENLABS_FEMALE_VOICE_ID","21m00Tcm4TlvDq8ikWAM"),"arabic_male":os.getenv("ELEVENLABS_MALE_VOICE_ID","")}
EDGE_VOICES = {"male":{"ar":"ar-EG-ShakirNeural","en":"en-US-GuyNeural"},"female":{"ar":"ar-EG-SalmaNeural","en":"en-US-JennyNeural"}}

async def speak(text: str, tier: str="free", gender: str="female", emotion: str="neutral", lang: str="ar") -> Optional[bytes]:
    if not text.strip(): return None
    is_premium = tier in ["premium","pro","yearly"]
    if is_premium and ELEVENLABS_KEY:
        result = await _elevenlabs(text, gender, lang, emotion)
        if result: return result
    return await _edge_tts(text, gender, lang, emotion)

async def _elevenlabs(text, gender, lang, emotion):
    if not ELEVENLABS_KEY: return None
    try:
        import httpx
        voice = VOICE_IDS.get(f"{lang}_{gender}", VOICE_IDS["arabic_female"])
        stability = 0.4 if emotion=="sadness" else 0.5 if emotion=="joy" else 0.45
        async with httpx.AsyncClient(timeout=30) as c:
            resp = await c.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                json={"text":text,"voice_settings":{"stability":stability,"similarity_boost":0.75},"model_id":"eleven_multilingual_v2"},
                headers={"xi-api-key":ELEVENLABS_KEY})
            return resp.content if resp.status_code==200 else None
    except Exception as e: logger.warning(f"ElevenLabs: {e}"); return None

async def _edge_tts(text, gender, lang, emotion):
    try:
        import edge_tts
        voice = EDGE_VOICES.get(gender,EDGE_VOICES["female"]).get(lang,"ar-EG-SalmaNeural")
        rate = "+5%" if emotion in ["joy","anger"] else "-5%" if emotion=="sadness" else "+0%"
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"]=="audio": chunks.append(chunk["data"])
        return b"".join(chunks) if chunks else None
    except Exception as e: logger.warning(f"Edge TTS: {e}"); return None

def get_voice_personality(personality: str="friend", gender: str="female") -> dict:
    configs = {"mentor":{"pitch":0.95,"rate":0.85},"friend":{"pitch":1.0,"rate":1.0},"romantic":{"pitch":1.05,"rate":0.9},"energetic":{"pitch":1.1,"rate":1.15},"calm":{"pitch":0.85,"rate":0.75}}
    return configs.get(personality, configs["friend"])
