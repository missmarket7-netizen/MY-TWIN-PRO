"""Gemini Streaming Client."""
import os, logging
from typing import AsyncGenerator

logger = logging.getLogger("gemini_client")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

async def generate_stream(system_prompt: str, user_message: str, context: str = "", lang: str = "ar") -> AsyncGenerator[str, None]:
    if not GEMINI_API_KEY:
        yield "أنا هنا معك 💜 (API غير مضبوط)"
        return
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        full_prompt = f"{system_prompt}\n\n{context}\n\n<MESSAGE>\n{user_message}\n</MESSAGE>" if context else user_message
        response = client.models.generate_content_stream(model="gemini-2.5-flash", contents=full_prompt)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Gemini stream error: {e}")
        yield "أواجه صعوبة تقنية 💜"
