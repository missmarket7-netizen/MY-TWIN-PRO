"""
MyTwin – STT Engine v2.0 (Whisper أساسي + Vosk احتياطي)
- Whisper: مجاني، دقة عالية، كل اللهجات
- Vosk: احتياطي، بدون إنترنت، خفيف
"""
import os, logging, asyncio, tempfile, base64
from typing import Optional

logger = logging.getLogger("stt_engine")

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
                logger.info("✅ Vosk جاهز")
            else:
                logger.warning("Vosk model not found")
        except Exception as e:
            logger.warning(f"Vosk غير متاح: {e}")
    return _vosk_model

async def transcribe_audio(audio_base64: str, language: str = "ar") -> Optional[str]:
    """تحويل الصوت إلى نص - يجرب Whisper ثم Vosk"""
    
    # 1. تجربة Whisper
    whisper = _get_whisper()
    if whisper:
        try:
            text = await _whisper_transcribe(whisper, audio_base64, language)
            if text:
                return text
        except Exception as e:
            logger.warning(f"Whisper failed: {e}")

    # 2. تجربة Vosk كاحتياطي
    vosk = _get_vosk()
    if vosk:
        try:
            text = await _vosk_transcribe(vosk, audio_base64)
            if text:
                return text
        except Exception as e:
            logger.warning(f"Vosk failed: {e}")

    return None

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
