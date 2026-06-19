"""
Dream Service – professional dream analysis (AR/EN).
Uses Gemini for interpretation, stores via repository, emits events.
"""
import logging, json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.infrastructure.ai.gemini_client import GEMINI_API_KEY
from app.repositories.memory_repository import store_memory
from app.models.event import EventType, create_event
from app.events.event_bus import emit

logger = logging.getLogger("dream_service")

async def analyze(user_id: str, dream_text: str, lang: str = "ar") -> Dict[str, Any]:
    if not dream_text or not dream_text.strip():
        return {"interpretation": "", "symbols": [], "emotions": [], "reflection_question": ""}

    if not GEMINI_API_KEY:
        return {
            "interpretation": "عذراً، خدمة تحليل الأحلام غير متاحة حالياً." if lang == "ar" else "Dream analysis unavailable.",
            "symbols": [], "emotions": [], "reflection_question": ""
        }

    prompt_ar = f"""أنت محلل أحلام خبير ومتعاطف. حلل الحلم وأعد ONLY JSON:
{{
  "interpretation": "تفسير الحلم بالعامية (3-4 جمل)",
  "symbols": ["رمز1", "رمز2", "رمز3"],
  "emotions": ["مشاعر1", "مشاعر2", "مشاعر3"],
  "reflection_question": "سؤال تأملي واحد"
}}
الحلم: "{dream_text}"
JSON:"""

    prompt_en = f"""You are an expert dream analyst. Analyze this dream and return ONLY JSON:
{{
  "interpretation": "dream interpretation in 3-4 sentences",
  "symbols": ["symbol1", "symbol2", "symbol3"],
  "emotions": ["emotion1", "emotion2", "emotion3"],
  "reflection_question": "one reflective question"
}}
Dream: "{dream_text}"
JSON:"""

    prompt = prompt_ar if lang == "ar" else prompt_en

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        text = response.text.strip() if response and response.text else ""
        if text.startswith("```json"): text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"): text = text.split("```")[1].split("```")[0].strip()
        result = json.loads(text)

        # Store as memory
        await store_memory(org_id=None, user_id=user_id, content=f"حلم: {dream_text[:300]}",
                          memory_type="dream", importance=0.7, emotion=result.get("emotions", ["neutral"])[0])

        # Emit event
        await emit(create_event(EventType("reflection_completed"), user_id,
                               summary=result.get("interpretation", "")[:200], lang=lang))

        return result
    except Exception as e:
        logger.error(f"Dream analysis failed: {e}")
        return {
            "interpretation": "لم أتمكن من تحليل حلمك حالياً. حاول مرة أخرى لاحقاً." if lang == "ar" else "Could not analyze your dream right now.",
            "symbols": [], "emotions": [], "reflection_question": ""
        }
