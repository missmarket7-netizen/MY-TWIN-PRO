"""
Multi-Provider Streaming Client v2.0
=====================================
يدعم: Gemini, Groq, OpenRouter
مع تدفق (Streaming) وتخزين مؤقت للجلسات.
"""
import os, logging, asyncio
from typing import AsyncGenerator, Optional

logger = logging.getLogger("streaming_client")

# ========== إعدادات ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_PROVIDER = os.getenv("STREAMING_PROVIDER", "gemini")

async def generate_stream(
    prompt: str,
    system_prompt: str = "",
    language: str = "ar",
    provider: Optional[str] = None,
    user_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    توليد نص متدفق من الذكاء الاصطناعي.
    يدعم: Gemini, Groq, OpenRouter.
    """
    provider = provider or DEFAULT_PROVIDER

    if provider == "gemini":
        async for chunk in _gemini_stream(prompt, system_prompt, language):
            yield chunk
    elif provider == "groq":
        async for chunk in _groq_stream(prompt, system_prompt, language):
            yield chunk
    elif provider == "openrouter":
        async for chunk in _openrouter_stream(prompt, system_prompt, language):
            yield chunk
    else:
        yield "أنا هنا معك 💜 (المزوّد غير مدعوم)"

async def _gemini_stream(prompt: str, system_prompt: str, lang: str) -> AsyncGenerator[str, None]:
    if not GEMINI_API_KEY:
        yield "خدمة Gemini غير متاحة حالياً 💜"
        return
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Gemini stream error: {e}")
        yield "أواجه صعوبة تقنية 💜"

async def _groq_stream(prompt: str, system_prompt: str, lang: str) -> AsyncGenerator[str, None]:
    if not GROQ_API_KEY:
        yield "خدمة Groq غير متاحة حالياً 💜"
        return
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"Groq stream error: {e}")
        yield "أواجه صعوبة تقنية 💜"

async def _openrouter_stream(prompt: str, system_prompt: str, lang: str) -> AsyncGenerator[str, None]:
    if not OPENROUTER_API_KEY:
        yield "خدمة OpenRouter غير متاحة حالياً 💜"
        return
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"OpenRouter stream error: {e}")
        yield "أواجه صعوبة تقنية 💜"

logger.info("✅ Multi-Provider Streaming Client v2.0 initialized")
