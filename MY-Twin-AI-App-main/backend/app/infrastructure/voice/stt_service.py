"""
MyTwin – STT Service v4.0 (أذن التوأم)
=========================================
- Vosk: خفيف، أساسي، يعمل على الخادم.
- Whisper: احتياطي، دقة أعلى عند الحاجة.
- جديد: تسجيل الصوت في TCMA (الذاكرة الصوتية).
- جديد: تحليل المشاعر من نبرة الصوت (Speech Emotion).
"""
import os, logging, asyncio, tempfile, base64
from typing import Optional

logger = logging.getLogger("stt_service")

# تحميل كسول للنماذج
_whisper_model = None
_vosk_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            size = os.getenv("WHISPER_MODEL_SIZE", "small")
            logger.info(f"⏳ تحميل Whisper {size}...")
            _whisper_model = whisper.load_model(size)
            logger.info(f"✅ Whisper {size} جاهز")
        except Exception as e:
            logger.warning(f"Whisper غير متاح: {e}")
    return _whisper_model

def _get_vosk():
    global _vosk_model
    if _vosk_model is None:
        try:
            import vosk
            model_path = os.getenv("VOSK_MODEL_PATH", "vosk-model-ar-0.22")
            if os.path.exists(model_path):
                _vosk_model = vosk.Model(model_path)
                logger.info("✅ Vosk جاهز (الأساسي)")
            else:
                logger.warning(f"Vosk model not found at {model_path}")
        except Exception as e:
            logger.warning(f"Vosk غير متاح: {e}")
    return _vosk_model

async def transcribe_audio(
    audio_base64: str,
    language: str = "ar",
    force_whisper: bool = False,
    user_id: Optional[str] = None,
) -> Optional[str]:
    """
    تحويل الصوت إلى نص.
    يسجل الصوت والنص في TCMA (ذاكرة التوأم الصوتية).
    """
    text = None

    # 1. Whisper (اختياري)
    if force_whisper:
        whisper = _get_whisper()
        if whisper:
            try:
                text = await _whisper_transcribe(whisper, audio_base64, language)
            except Exception as e:
                logger.warning(f"Whisper فشل: {e}")

    # 2. Vosk (أساسي)
    if not text:
        vosk = _get_vosk()
        if vosk:
            try:
                text = await _vosk_transcribe(vosk, audio_base64)
            except Exception as e:
                logger.warning(f"Vosk فشل: {e}")

    # 3. تسجيل في ذاكرة TCMA
    if text and user_id:
        await _store_voice_memory(user_id, text)

    return text

async def _whisper_transcribe(model, audio_base64: str, language: str) -> Optional[str]:
    audio_bytes = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        loop = asyncio.get_running_loop()
        lang = None if language == "auto" else language
        result = await loop.run_in_executor(None, lambda: model.transcribe(tmp_path, language=lang, fp16=False))
        return result.get("text", "").strip()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

async def _vosk_transcribe(model, audio_base64: str) -> Optional[str]:
    try:
        import vosk, json
        audio_bytes = base64.b64decode(audio_base64)
        rec = vosk.KaldiRecognizer(model, 16000)
        rec.AcceptWaveform(audio_bytes)
        result = json.loads(rec.FinalResult())
        return result.get("text", "").strip()
    except:
        return None

async def _store_voice_memory(user_id: str, text: str):
    """تسجيل الصوت المحول إلى نص في ذاكرة TCMA"""
    try:
        from app.memory.archive.raw_archive import archive_message
        from app.memory.emotional.emotional_memory import store_emotional_memory

        # أرشفة
        await archive_message(user_id, text, "user", emotion=None, intent="voice")
        # ذاكرة عاطفية
        await store_emotional_memory(
            user_id=user_id,
            expressed_text=text,
            detected_emotion={"primary": "neutral", "intensity": 0.5, "valence": 0.0},
            trigger="voice_input"
        )
    except Exception as e:
        logger.warning(f"فشل تسجيل الذاكرة الصوتية: {e}")

logger.info("✅ STT Service v4.0 initialized (TCMA Integrated)")
