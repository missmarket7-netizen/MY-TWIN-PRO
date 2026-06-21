"""
Image Orchestrator v2.0 – محرك توليد الصور (مجاني + Gemini)
=============================================================
- يدعم: Gemini (3 مفاتيح)، Stability AI (مجاني)
- احتياطي تلقائي بين المزودين
- تكامل TCMA
"""
import logging, os, httpx, random
from typing import Dict, Any, Optional

logger = logging.getLogger("image_lab")

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

# إعدادات Gemini (3 مفاتيح مع احتياطي)
GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY", ""),
    os.getenv("GEMINI_API_KEY_2", ""),
    os.getenv("GEMINI_API_KEY_3", ""),
]
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]  # إزالة المفاتيح الفارغة

# إعدادات Stability AI (مجاني)
STABILITY_KEY = os.getenv("STABILITY_API_KEY", "")
STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

class ImageOrchestrator:
    async def generate(
        self, user_id: str, prompt: str, style: str = "realistic",
        size: str = "1024x1024", provider: str = "gemini"
    ) -> Dict[str, Any]:
        image_url = None
        provider_used = provider

        # 1. محاولة Gemini (3 مفاتيح)
        if provider == "gemini" and GEMINI_KEYS:
            image_url = await self._gemini_generate(prompt, style)
            if not image_url:
                provider_used = "stability"
                image_url = await self._stability_generate(prompt)

        # 2. محاولة Stability AI
        elif provider == "stability" and STABILITY_KEY:
            image_url = await self._stability_generate(prompt)
            if not image_url and GEMINI_KEYS:
                provider_used = "gemini"
                image_url = await self._gemini_generate(prompt, style)

        # 3. تخزين في TCMA
        if image_url and TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=prompt,
                detected_emotion={"primary": "creative", "intensity": 0.8, "valence": 0.7},
                trigger="image_generation", cultural_context=f"style: {style}"
            )

        return {
            "prompt": prompt,
            "style": style,
            "image_url": image_url,
            "provider": provider_used,
            "status": "success" if image_url else "failed"
        }

    async def _gemini_generate(self, prompt: str, style: str) -> Optional[str]:
        """توليد صورة باستخدام Gemini (3 مفاتيح مع احتياطي)"""
        for i, key in enumerate(GEMINI_KEYS):
            try:
                from google import genai
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp-image-generation",
                    contents=prompt,
                )
                if response and response.text:
                    logger.info(f"✅ Gemini image generated (key {i+1})")
                    return response.text
            except Exception as e:
                logger.warning(f"Gemini key {i+1} failed: {e}")
                continue
        return None

    async def _stability_generate(self, prompt: str) -> Optional[str]:
        """توليد صورة باستخدام Stability AI (مجاني)"""
        if not STABILITY_KEY:
            return None
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    STABILITY_URL,
                    headers={"Authorization": f"Bearer {STABILITY_KEY}"},
                    json={"text_prompts": [{"text": prompt}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1}
                )
                if resp.status_code == 200:
                    return resp.json().get("artifacts", [{}])[0].get("base64")
        except Exception as e:
            logger.error(f"Stability AI failed: {e}")
        return None

    async def enhance_prompt(self, user_id: str, prompt: str) -> str:
        """تحسين الوصف للحصول على نتائج أفضل"""
        try:
            from app.infrastructure.ai.provider_router import provider_router
            enhanced = await provider_router.generate(
                f"حسّن هذا الوصف لتوليد صورة احترافية. أضف تفاصيل الإضاءة، الزاوية، الجودة. الوصف: {prompt}",
                language="en"
            )
            return enhanced or prompt
        except:
            return prompt

image_lab = ImageOrchestrator()
logger.info("✅ I.M.A.G.E. Lab v2.0 (Free + Gemini Multi-Key)")
