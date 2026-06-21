""" Business Canvas Generator - نموذج العمل التجاري """
import logging
logger = logging.getLogger("canvas_generator")

class BusinessCanvasGenerator:
    async def generate(self, idea: str, language: str = "ar") -> dict:
        try:
            from app.infrastructure.ai.provider_router import provider_router
            prompt = f"أنشئ نموذج العمل التجاري (Business Model Canvas) لمشروع '{idea}' باللغة {language}. غطِّ جميع العناصر التسعة."
            text = await provider_router.generate(prompt, language=language)
            return {"raw_canvas": text}
        except Exception as e:
            logger.error(f"Canvas generation failed: {e}")
            return {"error": str(e)}
