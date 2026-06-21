"""
SDLC Orchestrator v3.0 – مهندس برمجيات بذاكرة حية
====================================================
يتكامل عميقاً مع TCMA: يتذكر أسلوبك، أخطاءك، وحالتك النفسية.
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except: AI_AVAILABLE = False

try:
    from app.memory.identity.identity_model import get_identity
    from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_state_for_response
    from app.memory.reflection.reflection_engine import process_message_for_reflections
    from app.memory.graph.memory_graph import auto_create_edges_from_memory
    TCMA_AVAILABLE = True
except: TCMA_AVAILABLE = False

logger = logging.getLogger("code_lab_v3")

class CodeLabOrchestrator:
    def __init__(self):
        self.git = GitManager()
        self.finder = SolutionFinder()
        self.analyzer = CodeAnalyzer()
        self.boilerplate = ProjectBoilerplate()
        self.active_projects: Dict[str, Any] = {}

    async def get_developer_profile(self, user_id: str) -> Dict[str, Any]:
        if not TCMA_AVAILABLE: return {"level": "intermediate", "favorite_lang": "Python"}
        try:
            identity = await get_identity(user_id)
            emotion = await get_emotional_state_for_response(user_id, "")
            return {
                "traits": identity.get("traits", []) if identity else [],
                "emotion": emotion.get("current_emotion", "neutral"),
                "level": "expert" if identity and "مبرمج" in str(identity.get("traits", [])) else "intermediate"
            }
        except: return {"level": "intermediate", "emotion": "neutral"}

    async def generate_code(self, user_id: str, prompt: str, lang: str = "Python") -> Dict[str, Any]:
        profile = await self.get_developer_profile(user_id)
        
        # تكييف الموجه حسب خبرة المستخدم وحالته النفسية
        adapted_prompt = prompt
        if profile.get("emotion") == "frustration":
            adapted_prompt = f"(المستخدم محبط، كن داعماً ومبسطاً)\n{prompt}"
        elif profile.get("level") == "expert":
            adapted_prompt = f"(المستخدم خبير، استخدم تقنيات متقدمة)\n{prompt}"
        
        code = await provider_router.generate(f"اكتب كود {lang}: {adapted_prompt}") if AI_AVAILABLE else "// تعذر التوليد"
        
        # تخزين في الذاكرة العاطفية
        if TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=prompt,
                detected_emotion={"primary": "focused", "intensity": 0.8, "valence": 0.5},
                trigger="code_generation", cultural_context=f"برمجة: {lang}"
            )
            # توليد استنتاج
            await process_message_for_reflections(
                user_id=user_id, message=f"كتب كود {lang} لـ: {prompt[:50]}",
                language="ar", detected_emotion="focused"
            )
        
        return {"code": code, "adapted_for_emotion": profile.get("emotion")}

    async def debug(self, user_id: str, error: str, lang: str = "Python") -> Dict[str, Any]:
        solution = await self.finder.search(error, lang)
        
        if TCMA_AVAILABLE:
            await store_emotional_memory(
                user_id=user_id, expressed_text=error,
                detected_emotion={"primary": "frustration", "intensity": 0.7, "valence": -0.3},
                trigger="debugging", cultural_context=f"خطأ برمجي: {lang}"
            )
        
        return solution

    async def review(self, user_id: str, code: str, lang: str = "Python") -> Dict[str, Any]:
        review = await self.analyzer.deep_review(code, lang)
        
        if TCMA_AVAILABLE:
            await process_message_for_reflections(
                user_id=user_id, message=f"راجع كود {lang} وحصل على تحليل",
                language="ar", detected_emotion="neutral"
            )
        
        return review

class GitManager:
    async def create_repo(self, name: str): return {"repo_url": f"https://github.com/user/{name}"}
    async def generate_commit_message(self, diff: str) -> str:
        return await provider_router.generate(f"اكتب رسالة Commit: {diff}") if AI_AVAILABLE else "Update"

class SolutionFinder:
    async def search(self, error: str, lang: str) -> Dict[str, Any]:
        prompt = f"اشرح الخطأ وقدم 3 حلول:\n{error}\nاللغة: {lang}"
        return {"solutions": await provider_router.generate(prompt) if AI_AVAILABLE else "ابحث في Stack Overflow"}

class CodeAnalyzer:
    async def deep_review(self, code: str, lang: str) -> Dict[str, Any]:
        prompt = f"حلل الكود {lang} (Big O، أمان، جودة):\n{code}"
        return {"analysis": await provider_router.generate(prompt) if AI_AVAILABLE else "تعذر التحليل"}

class ProjectBoilerplate:
    async def generate(self, project_type: str, name: str) -> Dict[str, Any]:
        return {"command": f"npx create-{project_type} {name}"}

code_lab = CodeLabOrchestrator()
